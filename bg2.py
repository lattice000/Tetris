# Tetris with Next Piece Preview, Hold Piece, Particle Background, Line Clear Explosion,
# Scoreboard, Difficulty Scaling, and Restart Button
import pygame
import random
import numpy as np
import os

pygame.init()
pygame.mixer.init()

cell_size = 30
cols, rows = 10, 20
width, height = cell_size * cols, cell_size * rows
screen = pygame.display.set_mode((width + 200, height + 50))
pygame.display.set_caption("Fancy Tetris")
font = pygame.font.SysFont("consolas", 24)
clock = pygame.time.Clock()

colors = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

shapes = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 0], [1, 1, 1]]
]

class Tetromino:
    def __init__(self, shape=None):
        self.shape = shape if shape else random.choice(shapes)
        self.color = random.choice(colors)
        self.x = cols // 2 - len(self.shape[0]) // 2
        self.y = 0

board = [[0] * cols for _ in range(rows)]

def check_collision(board, shape, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if x + j < 0 or x + j >= cols or y + i >= rows or board[y + i][x + j]:
                    return True
    return False

def lock_piece(board, piece):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                board[piece.y + i][piece.x + j] = colors.index(piece.color) + 1

def clear_lines(board):
    cleared = []
    for i in range(rows):
        if all(board[i]):
            cleared.append(i)
            del board[i]
            board.insert(0, [0] * cols)
    return cleared

class Particle:
    def __init__(self):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.speed = random.uniform(0.1, 0.5)
        self.color = random.choice(colors)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.uniform(0, width)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

particles = [Particle() for _ in range(100)]

def generate_beep(freq=440, duration_ms=200, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = np.sin(freq * 2 * np.pi * t)
    audio = (tone * 32767 * volume).astype(np.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

rotate_sound = generate_beep(880, 100)
drop_sound = generate_beep(440, 150)
clear_sound = generate_beep(660, 200)
gameover_sound = generate_beep(220, 1000)

hold_piece = None
hold_used = False
next_piece = Tetromino()

explosions = []
class Spark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.life = random.randint(20, 40)
        self.color = random.choice(colors)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)

def draw_board():
    screen.fill((0, 0, 0))

    for p in particles:
        p.update()
        p.draw(screen)

    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, colors[cell - 1], (x * cell_size, y * cell_size, cell_size, cell_size))

    for i, row in enumerate(current.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, current.color,
                                 ((current.x + j) * cell_size, (current.y + i) * cell_size, cell_size, cell_size))

    for x in range(cols):
        pygame.draw.line(screen, (50, 50, 50), (x * cell_size, 0), (x * cell_size, height))
    for y in range(rows):
        pygame.draw.line(screen, (50, 50, 50), (0, y * cell_size), (width, y * cell_size))

    if hold_piece:
        for i, row in enumerate(hold_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, hold_piece.color,
                                     (width + 30 + j * cell_size, 50 + i * cell_size, cell_size, cell_size))
        screen.blit(font.render("HOLD", True, (255, 255, 255)), (width + 30, 20))

    for i, row in enumerate(next_piece.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_piece.color,
                                 (width + 30 + j * cell_size, 180 + i * cell_size, cell_size, cell_size))
    screen.blit(font.render("NEXT", True, (255, 255, 255)), (width + 30, 150))

    for spark in explosions[:]:
        spark.update()
        spark.draw(screen)
        if spark.life <= 0:
            explosions.remove(spark)

    screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, height + 10))
    screen.blit(font.render(f"High Score: {high_score}", True, (255, 215, 0)), (200, height + 10))

    if not running:
        pygame.draw.rect(screen, (100, 100, 100), (width // 2 - 60, height // 2 - 20, 120, 40))
        screen.blit(font.render("Restart", True, (255, 255, 255)), (width // 2 - 40, height // 2 - 10))

    pygame.display.flip()

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt") as f:
            return int(f.read())
    return 0

current = Tetromino()
running = True
drop_time = 0
score = 0
high_score = load_high_score()
difficulty = 500

def restart_game():
    global board, current, next_piece, hold_piece, hold_used, running, drop_time, score, difficulty
    board = [[0] * cols for _ in range(rows)]
    current = Tetromino()
    next_piece = Tetromino()
    hold_piece = None
    hold_used = False
    drop_time = 0
    score = 0
    difficulty = 500
    return True

while True:
    dt = clock.tick(30)
    if running:
        drop_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if not running and event.type == pygame.MOUSEBUTTONDOWN:
            if width // 2 - 60 <= event.pos[0] <= width // 2 + 60 and height // 2 - 20 <= event.pos[1] <= height // 2 + 20:
                running = restart_game()

    if running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and not check_collision(board, current.shape, current.x - 1, current.y):
            current.x -= 1
        if keys[pygame.K_RIGHT] and not check_collision(board, current.shape, current.x + 1, current.y):
            current.x += 1
        if keys[pygame.K_DOWN] and not check_collision(board, current.shape, current.x, current.y + 1):
            current.y += 1
        if keys[pygame.K_UP]:
            rotated = list(zip(*current.shape[::-1]))
            if not check_collision(board, rotated, current.x, current.y):
                current.shape = rotated
                rotate_sound.play()
        if keys[pygame.K_c] and not hold_used:
            hold_used = True
            if hold_piece:
                current, hold_piece = hold_piece, current
                current.x = cols // 2 - len(current.shape[0]) // 2
                current.y = 0
            else:
                hold_piece = current
                current = next_piece
                next_piece = Tetromino()

        if drop_time > difficulty:
            drop_time = 0
            if not check_collision(board, current.shape, current.x, current.y + 1):
                current.y += 1
            else:
                lock_piece(board, current)
                drop_sound.play()
                cleared = clear_lines(board)
                if cleared:
                    clear_sound.play()
                    for row in cleared:
                        for x in range(cols):
                            explosions.append(Spark(x * cell_size + 15, row * cell_size + 15))
                    score += len(cleared) * 100
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    difficulty = max(100, difficulty - 10)
                current = next_piece
                next_piece = Tetromino()
                hold_used = False
                if check_collision(board, current.shape, current.x, current.y):
                    gameover_sound.play()
                    running = False

    draw_board()
