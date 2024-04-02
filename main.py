import sys
import random

random.seed(0)

# Disables logs leaking from pygame
sys.stdout = sys.__stdin__
sys.stderr = sys.__stdin__
import pygame
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

pygame.init()

DISPLAY = pygame.display.set_mode((640, 480), vsync = 1)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)

GRAVITY: float = -0.001
TERMINAL_VELOCITY: float = 0.05
JUMP_VELCOITY: float = 0.015
FPS: float = 60

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
        pygame.draw.line(DISPLAY, COLOR_BLUE, (pos_x, 0), (pos_x, top))
        pygame.draw.line(DISPLAY, COLOR_BLUE, (pos_x, bottom), (pos_x, DISPLAY.get_height()))
    def random():
        return Obstacle(random.uniform(0.4, 0.8), random.uniform(0.2, 0.4))

class Game:
    def __init__(self):
        # Scales form 0 to 1
        self.pos: float = 0.8
        self.tick_count: int = 0
        self.velocity: float = 0
        self.dead = False
    def tick(self):
        self.pos += self.velocity
        if self.pos <= 0:
            self.pos = 0
            self.dead = True
        self.velocity += GRAVITY
        self.velocity = restrict(self.velocity, -TERMINAL_VELOCITY, TERMINAL_VELOCITY)
        self.tick_count += 1
    def jump(self):
        self.velocity = JUMP_VELCOITY
    def render(self):
        pygame.draw.circle(DISPLAY, COLOR_RED, (DISPLAY.get_width() / 2, lerp(self.pos, 0, 1, DISPLAY.get_height(), 0)), 5)
        obstacle = Obstacle.random()
        obstacle.render(0.7)

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
        pygame.draw.line(DISPLAY, COLOR_RED, (0, 0), (DISPLAY.get_width(), DISPLAY.get_height()))
        pygame.draw.line(DISPLAY, COLOR_RED, (DISPLAY.get_width(), 0), (0, DISPLAY.get_height()))
    pygame.display.update()
    pygame.time.delay(1000 // FPS - (pygame.time.get_ticks() - start_time))

pygame.quit()
