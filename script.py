import pygame, sys, random, importlib
pygame.init()

running = True

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y)

class Game:
    def __init__(self):
        #regular stuff
        self.WIDTH, self.HEIGHT = 680, 192
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        #tile stuff
        self.tile_group = pygame.sprite.Group()

    def load_level(self, level_name):
        level_module = importlib.import_module(f"levels.{level_name}")
        self.level_map = level_module.level1_map

    def map_setup(self):
        self.tile_size = 32
        for row_index, row in enumerate(self.level_map):
            for col_index, cell in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                if cell == "X":
                    tile = Tile(x, y)
                    self.tile_group.add(tile)

                if cell == "P":


game = Game()
game.load_level("level1")
game.map_setup()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

    game.screen.fill((0, 0, 0))
    game.tile_group.draw(game.screen)
    game.clock.tick(60)
    pygame.display.update()

pygame.quit()