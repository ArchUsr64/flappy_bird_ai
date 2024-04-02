import sys
import random
import math

random.seed(0)

# Disables logs leaking from pygame
sys.stdout = None
sys.stderr = None
import pygame
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

class Matrix:
    def __init__(self, data: [[int]]):
        self.row_count = len(data)
        self.col_count = len(data[0])
        self.data = data
    @classmethod
    def from_size(self, row_count: int, col_count: int, rand = False):
        if rand:
            data = [[random.uniform(-1, 1) for _ in range(col_count)] for _ in range(row_count)]
        else:
            data = [[0 * col_count] for _ in range(row_count)]
        return Matrix(data)
    @classmethod
    def from_row(self, row: [int], rand = False):
            return Matrix([row])
    def __mul__(self, other):
        if self.col_count != other.row_count:
            print(f"[ERROR]: Mismatched order of Matrices {(self.row_count, self.col_count)} vs {(other.row_count, other.col_count)}")
            exit(1)
        res = [[0 for _ in range(other.col_count)] for _ in range(self.row_count)]
        for i in range(self.row_count):
            for j in range(other.col_count):
                for k in range(self.col_count):
                    res[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix(res)
    def sigmoid(self):
        if self.row_count != 1:
            print("[ERROR] Can't apply activation function for non row matrix")
            exit(1)
        for i in range(self.col_count):
            self.data[0][i] = 1 / (1 + math.e ** -self.data[0][i])

class NN:
    def __init__(self, architecture: [int], rand = False):
        self.layers = []
        for i in range(len(architecture) - 1):
            self.layers.append(Matrix.from_size(architecture[i], architecture[i + 1], rand))
    def solve(self, input: Matrix) -> Matrix:
        temp = input
        for layer in self.layers:
            temp = temp * layer
            temp.sigmoid()
        return temp

pygame.init()

DISPLAY = pygame.display.set_mode((640, 480), vsync = 1)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)

GRAVITY: float = -0.001
TERMINAL_VELOCITY: float = 0.05
JUMP_VELCOITY: float = 0.015
OBSTACLE_SPEED: float = 0.002
OBSTACLE_DENSITY: int = 5
BALL_RADIUS: float = 0.01
FPS: int = 60

def lerp(x, min_x, max_x, min_out, max_out):
    x -= min_x
    x /= (max_x - min_x)
    x *= (max_out - min_out)
    x += min_out
    return x

def restrict(value, range_min, range_max):
    value = max(value, range_min)
    value = min(value, range_max)
    return value

class Obstacle:
    def __init__(self, height, gap):
        self.top = height + gap
        self.bottom = height
    def render(self, pos_x):
        pos_x = lerp(pos_x, 0, 1, 0, DISPLAY.get_width())
        top = lerp(self.top, 0, 1, DISPLAY.get_height(), 0)
        bottom = lerp(self.bottom, 0, 1, DISPLAY.get_height(), 0)
        line_width = int(lerp(BALL_RADIUS, 0, 1, 0, DISPLAY.get_width()))
        pygame.draw.line(DISPLAY, COLOR_BLUE, (pos_x, 0), (pos_x, top), line_width)
        pygame.draw.line(DISPLAY, COLOR_BLUE, (pos_x, bottom), (pos_x, DISPLAY.get_height()), line_width)
    def mid(self):
        return (self.top + self.bottom) / 2
    def random():
        return Obstacle(random.uniform(0.1, 0.6), random.uniform(0.15, 0.35))
    def collision(self, pos) -> bool:
        return pos >= self.top or pos <= self.bottom

class Game:
    def __init__(self):
        # Scales form 0 to 1
        self.pos: float = 0.8
        self.tick_count: int = 0
        self.velocity: float = 0
        self.dead: bool = False
        self.obstacles: [Obstacle] = [Obstacle.random() for _ in range(OBSTACLE_DENSITY)]
        obstacle_start_position = random.uniform(0.8, 1.2)
        self.obstacle_positions = [obstacle_start_position + i / OBSTACLE_DENSITY for i in range(0, OBSTACLE_DENSITY + 1)]
    def tick(self):
        # Obstacle generation
        for i in range(len(self.obstacle_positions)):
            self.obstacle_positions[i] -= OBSTACLE_SPEED
        for i in range(len(self.obstacle_positions)):
            if self.obstacle_positions[i] <= 0:
                self.obstacle_positions.pop(i)
                self.obstacles.pop(i)
                self.obstacles.append(Obstacle.random())
                self.obstacle_positions.append(1 + 1 / OBSTACLE_DENSITY)
        # Physics
        self.pos += self.velocity
        if self.pos <= 0:
            self.pos = 0
            self.dead = True
        self.velocity += GRAVITY
        self.velocity = restrict(self.velocity, -TERMINAL_VELOCITY, TERMINAL_VELOCITY)
        # Collision
        for i, obstacle in enumerate(self.obstacles):
            obstacle_pos = self.obstacle_positions[i]
            if obstacle_pos >= 0.5 - BALL_RADIUS and obstacle_pos <= 0.5 + BALL_RADIUS :
                if obstacle.collision(self.pos):
                    self.dead = True
        self.tick_count += 1
    def jump(self):
        self.velocity = JUMP_VELCOITY
    def next_obstacle_coords(self):
        index = OBSTACLE_DENSITY // 2
        while self.obstacle_positions[index] <= 0.5:
            index += 1
        return [self.obstacle_positions[index] - 0.5, self.obstacles[index].mid()]
    def render(self):
        for i, obstacle in enumerate(self.obstacles):
            obstacle.render(self.obstacle_positions[i])
        pygame.draw.circle(DISPLAY, COLOR_RED, (DISPLAY.get_width() / 2, lerp(self.pos, 0, 1, DISPLAY.get_height(), 0)), lerp(BALL_RADIUS, 0, 1, 0, DISPLAY.get_width()))

running = True
bird = Game()
while running:
    start_time = pygame.time.get_ticks()
    DISPLAY.fill(COLOR_WHITE)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bird.jump()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
    bird.render()
    if not bird.dead:
        bird.tick()
    else:
        pygame.draw.line(DISPLAY, COLOR_RED, (0, 0), (DISPLAY.get_width(), DISPLAY.get_height()), DISPLAY.get_width() // 100)
        pygame.draw.line(DISPLAY, COLOR_RED, (DISPLAY.get_width(), 0), (0, DISPLAY.get_height()), DISPLAY.get_width() // 100)
    pygame.display.update()
    pygame.time.delay(1000 // FPS - (pygame.time.get_ticks() - start_time))

pygame.quit()
