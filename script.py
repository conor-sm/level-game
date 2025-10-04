import pygame, sys, random
pygame.init()

running = True

WIDTH, HEIGHT = 680, 440
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

    screen.fill((0, 0, 0))
    clock.tick(60)
    pygame.display.update()

pygame.quit()