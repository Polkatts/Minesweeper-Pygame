import pygame

from random import randrange

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
gray = (128, 128, 128)

width = 30
height = 30

spaces = 30

margin = 10
menu_size = 50
left_click = 1
right_click = 3

num_colors = {
    1: (0, 0, 255),     
    2: (0, 128, 0),    
    3: (255, 0, 0),    
    4: (0, 0, 128),    
    5: (128, 0, 0),    
    6: (0, 128, 128),  
    7: (0, 0, 0),      
    8: (128, 128, 128) 
}


class Cell:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.is_bomb = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_count = 0

    def draw(self, surface, font):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        if self.is_revealed:
            if self.is_bomb:
                pygame.draw.rect(surface, red, rect)
            else:
                pygame.draw.rect(surface, gray, rect)

                if self.neighbor_count > 0:
                    color = num_colors.get(self.neighbor_count, black)
                    text_surf = font.render(str(self.neighbor_count), True, color)
                    text_rect = text_surf.get_rect(center=rect.center)
                    surface.blit(text_surf, text_rect)
                    
        else:
            pygame.draw.rect(surface, white, rect)
            if self.is_flagged:
                pygame.draw.circle(surface, blue, rect.center, self.size // 4)

        pygame.draw.rect(surface, black, rect, 1)


def create_grid(rows, cols, size, bombs):
    grid = [[Cell(c * size + margin, r * size + menu_size + margin, size) 
             for c in range(cols)] for r in range(rows)]
    
    count = 0
    while count < bombs:
        r = randrange(rows)
        c = randrange(cols)
        if not grid[r][c].is_bomb:
            grid[r][c].is_bomb = True # Define a bomba
            count += 1

    for r in range(rows):
        for c in range(cols):
            if grid[r][c].is_bomb: continue
            grid[r][c].neighbor_count = sum(
                1 for i in range(max(0, r-1), min(rows, r+2))
                for j in range(max(0, c-1), min(cols, c+2))
                if grid[i][j].is_bomb
            )
    return grid

def reveal_empty(grid, r, c, max_rows, max_cols):
    if not (0 <= r < max_rows and 0 <= c < max_cols):
        return
    
    cell = grid[r][c]
    if cell.is_revealed or cell.is_bomb or cell.is_flagged:
        return

    cell.is_revealed = True

    if cell.neighbor_count == 0:
        for i in range(r - 1, r + 2):
            for j in range(c - 1, c + 2):
                if i == r and j == c:
                    continue
                reveal_empty(grid, i, j, max_rows, max_cols)

def check_win(grid):
    for row in grid:
        for cell in row:
            if not cell.is_bomb and not cell.is_revealed:
                return False
    return True


pygame.init()

font = pygame.font.SysFont("Arial", 18, bold=True)
clock = pygame.time.Clock()


screen_width = (width * spaces) + (margin * 2)
screen_height = (height * spaces) + menu_size + (margin * 2)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Minesweeper")

grid = create_grid(height, width, spaces, 80)

game_over = False
game_won = False

running = True
while running:
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game_over:
                grid = create_grid(height, width, spaces, 80) 
                game_over = False
                victory = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = pygame.mouse.get_pos()
            c = (mx - margin) // spaces
            r = (my - (menu_size + margin)) // spaces

            if 0 <= r < height and 0 <= c < width:
                cell = grid[r][c]
                
                if event.button == left_click and not cell.is_flagged:
                    if cell.is_bomb:
                        game_over = True
                        victory = False
                        for row in grid:
                            for c_obj in row:
                                if c_obj.is_bomb: c_obj.is_revealed = True
                    else:
                        reveal_empty(grid, r, c, height, width)
                        if check_win(grid):
                            game_over = True
                            victory = True

                elif event.button == right_click:
                    if not grid[r][c].is_revealed:
                        grid[r][c].is_flagged = not grid[r][c].is_flagged
                
    for row in grid:
        for cell in row:
            cell.draw(screen, font)
    if game_over:
        msg = "VOCÊ VENCEU!" if victory else "GAME OVER!"
        color = green if victory else red
        
        end_font = pygame.font.SysFont('Arial', 30, bold=True)
        text_surf = end_font.render(msg, True, color)
        text_rect = text_surf.get_rect(center=(screen_width // 2, menu_size // 2 + margin))
        
        restart_font = pygame.font.SysFont('Arial', 15)
        restart_surf = restart_font.render("Pressione ENTER para jogar novamente", True, white)
        restart_rect = restart_surf.get_rect(center=(screen_width // 2, menu_size // 2 + 27))

        pygame.draw.rect(screen, black, text_rect.inflate(20, 10))
        screen.blit(text_surf, text_rect)
        screen.blit(restart_surf, restart_rect)
    pygame.display.flip()
    clock.tick(60)


pygame.quit()

