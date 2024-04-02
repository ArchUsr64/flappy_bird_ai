import sys

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

class Game:
    def __init__(self):
        # Scales form 0 to 1
        self.pos: float = 0.8
        self.progress: float = 0
        self.velocity: float = 0
        self.dead = False
    def tick(self):
        self.pos += self.velocity
        if self.pos <= 0:
            self.pos = 0
            self.dead = True
        self.velocity += GRAVITY
        self.velocity = restrict(self.velocity, -TERMINAL_VELOCITY, TERMINAL_VELOCITY)
        self.progress += 0.1
    def jump(self):
        self.velocity = JUMP_VELCOITY
    def render(self):
        pygame.draw.circle(DISPLAY, COLOR_RED, (DISPLAY.get_width() / 2, lerp(self.pos, 0, 1, DISPLAY.get_height(), 0)), 5)

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
