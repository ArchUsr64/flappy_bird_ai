import sys

# Disables logs leaking from pygame
sys.stdout = sys.__stdin__
sys.stderr = sys.__stdin__
import pygame
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

pygame.init()
game_display = pygame.display.set_mode((640, 480))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("jump")
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        pygame.display.update()

pygame.quit()
