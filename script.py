import pygame, sys, random, importlib
pygame.init()

running = True
loss = False

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_image = pygame.Surface((32, 32))
        self.player_image.fill((200, 100, 100))
        self.player_rect = self.player_image.get_rect()
        self.rect = self.player_rect
        self.x = 0
        self.y = 100
        self.jump_strength = 10
        self.gravity = 0.8
        self.velocity_y = 0
        self.velocity_x = 6
        self.acceleration_x = 0
        self.friction = 0.3
        self.on_ground = False

    def update(self, tile_group):
        global loss

        self.velocity_x += self.acceleration_x

        if self.acceleration_x == 0:
            if self.velocity_x > 0:
                self.velocity_x = max(0, self.velocity_x - self.friction)
            elif self.velocity_x < 0:
                self.velocity_x = min(0, self.velocity_x + self.friction)


        self.velocity_x = max(-5, min(self.velocity_x, 5))
        self.x += self.velocity_x

        self.velocity_y += self.gravity

        if self.velocity_y > 5:
            self.velocity_y = 5

        self.y += self.velocity_y

        self.player_rect.y = self.y
        self.player_rect.x = self.x

        collided_tiles = pygame.sprite.spritecollide(self, tile_group, False)
        for tile in collided_tiles:
            if self.velocity_y > 0:
                self.player_rect.bottom = tile.rect.top
                self.y = self.player_rect.y
                self.velocity_y = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False
            if self.y > 192:
                loss = True
                print("LOSS")

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_strength

    def draw(self, screen):
        screen.blit(self.player_image, self.player_rect)

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

game = Game()
#######EDIT LEVEL HERE
game.load_level("level1")
game.map_setup()
player = Player()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        keys = pygame.key.get_pressed()
        player.acceleration_x = 0
        if keys[pygame.K_w]:
            player.jump()
        if keys[pygame.K_a]:
            player.acceleration_x = -0.5
        if keys[pygame.K_d]:
            player.acceleration_x = 0.5

    game.screen.fill((0, 0, 0))
    game.tile_group.draw(game.screen)
    player.update(game.tile_group)
    player.draw(game.screen)
    game.clock.tick(60)
    pygame.display.update()

pygame.quit()