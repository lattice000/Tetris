import pygame
import random

# 初始化
pygame.init()

# 畫面大小與方塊格數
cell_size = 30
cols, rows = 10, 20
width, height = cols * cell_size, rows * cell_size

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# 方塊形狀（以 4x4 矩陣定義）
shapes = [
    [[1, 1, 1, 1]],                         # I
    [[1, 1], [1, 1]],                       # O
    [[0, 1, 0], [1, 1, 1]],                 # T
    [[1, 0, 0], [1, 1, 1]],                 # J
    [[0, 0, 1], [1, 1, 1]],                 # L
    [[1, 1, 0], [0, 1, 1]],                 # S
    [[0, 1, 1], [1, 1, 0]]                  # Z
]

# 顏色對應
colors = [
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 0, 255),
    (255, 165, 0),
    (0, 255, 0),
    (255, 0, 0)
]

# 建立空白遊戲板
def create_board():
    return [[0] * cols for _ in range(rows)]

# 方塊物件
class Tetromino:
    def __init__(self):
        self.shape = random.choice(shapes)
        self.color = colors[shapes.index(self.shape)]
        self.x = cols // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

# 檢查是否碰撞
def check_collision(board, shape, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if (
                    x + j < 0 or x + j >= cols or
                    y + i >= rows or
                    board[y + i][x + j]
                ):
                    return True
    return False

# 鎖定方塊到版面
def lock_piece(board, piece):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                board[piece.y + i][piece.x + j] = colors.index(piece.color) + 1

# 加入音效
rotate_sound = pygame.mixer.Sound("rotate.wav")
drop_sound = pygame.mixer.Sound("drop.wav")
clear_sound = pygame.mixer.Sound("line_clear.wav")
gameover_sound = pygame.mixer.Sound("game_over.wav")

# 畫面刷新加入計分板
def draw_board(screen, board, piece, score):
    screen.fill((0, 0, 0))
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, colors[cell - 1],
                                 (x * cell_size, y * cell_size, cell_size, cell_size))

    # 畫目前方塊
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color,
                                 ((piece.x + j) * cell_size, (piece.y + i) * cell_size, cell_size, cell_size))

    # 計分板文字
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

# 動畫（清除列閃爍）
def animate_clear(screen, board, rows_to_clear):
    for _ in range(3):
        for y in rows_to_clear:
            for x in range(cols):
                pygame.draw.rect(screen, (255, 255, 255),
                                 (x * cell_size, y * cell_size, cell_size, cell_size))
        pygame.display.flip()
        pygame.time.wait(100)

        for y in rows_to_clear:
            for x in range(cols):
                pygame.draw.rect(screen, (0, 0, 0),
                                 (x * cell_size, y * cell_size, cell_size, cell_size))
        pygame.display.flip()
        pygame.time.wait(100)

# 修改 clear_lines 回傳要清除的列
def get_full_rows(board):
    return [i for i, row in enumerate(board) if all(row)]

def clear_lines(board, full_rows):
    for row in full_rows:
        del board[row]
        board.insert(0, [0] * cols)

# 修改 main loop 中的流程
board = create_board()
piece = Tetromino()
drop_time = 0
score = 0
running = True

while running:
    dt = clock.tick(30)
    drop_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if not check_collision(board, piece.shape, piece.x - 1, piece.y):
            piece.x -= 1
    if keys[pygame.K_RIGHT]:
        if not check_collision(board, piece.shape, piece.x + 1, piece.y):
            piece.x += 1
    if keys[pygame.K_DOWN]:
        if not check_collision(board, piece.shape, piece.x, piece.y + 1):
            piece.y += 1
    if keys[pygame.K_UP]:
        new_shape = list(zip(*piece.shape[::-1]))
        if not check_collision(board, new_shape, piece.x, piece.y):
            piece.shape = new_shape
            rotate_sound.play()

    if drop_time > 500:
        drop_time = 0
        if not check_collision(board, piece.shape, piece.x, piece.y + 1):
            piece.y += 1
        else:
            lock_piece(board, piece)
            drop_sound.play()
            full_rows = get_full_rows(board)
            if full_rows:
                animate_clear(screen, board, full_rows)
                clear_lines(board, full_rows)
                score += len(full_rows) * 100
                clear_sound.play()
            piece = Tetromino()
            if check_collision(board, piece.shape, piece.x, piece.y):
                gameover_sound.play()
                print("Game Over!")
                running = False

    draw_board(screen, board, piece, score)


# 遊戲主迴圈
def main():
    board = create_board()
    piece = Tetromino()
    drop_time = 0
    score = 0
    running = True

    while running:
        dt = clock.tick(30)
        drop_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 控制
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if not check_collision(board, piece.shape, piece.x - 1, piece.y):
                piece.x -= 1
        if keys[pygame.K_RIGHT]:
            if not check_collision(board, piece.shape, piece.x + 1, piece.y):
                piece.x += 1
        if keys[pygame.K_DOWN]:
            if not check_collision(board, piece.shape, piece.x, piece.y + 1):
                piece.y += 1
        if keys[pygame.K_UP]:
            new_shape = list(zip(*piece.shape[::-1]))
            if not check_collision(board, new_shape, piece.x, piece.y):
                piece.shape = new_shape

        # 自動下落
        if drop_time > 500:
            drop_time = 0
            if not check_collision(board, piece.shape, piece.x, piece.y + 1):
                piece.y += 1
            else:
                lock_piece(board, piece)
                board, lines = clear_lines(board)
                score += lines * 100
                piece = Tetromino()
                if check_collision(board, piece.shape, piece.x, piece.y):
                    print("Game Over!")
                    running = False

        draw_board(screen, board, piece)

    pygame.quit()

if __name__ == "__main__":
    main()
