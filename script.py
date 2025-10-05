import pygame, sys, random, importlib
pygame.init()

running = True
menu_active = True
game_over = False
game_active = False

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.original_x = x
        self.original_y = y
        
    def update(self, camera_offset_x):
        self.rect.x = self.original_x - camera_offset_x
        self.rect.y = self.original_y

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((200, 100, 100))
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 100
        self.jump_strength = 12
        self.gravity = 0.6
        self.velocity_y = 0
        self.velocity_x = 6
        self.acceleration_x = 0
        self.friction = 0.3
        self.rect.topleft = (self.x, self.y)
        self.on_ground = False

    def update(self, tile_group, camera_offset_x):
        global game_over, game_active, menu_active

        keys = pygame.key.get_pressed()
        self.acceleration_x = 0
        if keys[pygame.K_SPACE]:
            self.jump()
        if keys[pygame.K_a]:
            self.acceleration_x = -0.5
        if keys[pygame.K_d]:
            self.acceleration_x = 0.5

        self.rect.x = self.x - camera_offset_x
        self.rect.y = self.y

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

        self.collided_tiles = pygame.sprite.spritecollide(self, tile_group, False)
        for tile in self.collided_tiles:
            if self.velocity_y > 0:
                self.rect.bottom = tile.rect.top
                self.y = self.rect.y
                self.velocity_y = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False
            if self.y > 288:
                game_active = False
                game_over = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_strength

    def draw(self, screen, camera_offset_x):
        screen.blit(self.image,(self.x - camera_offset_x, self.y))

class Game:
    def __init__(self):
        #regular stuff
        self.WIDTH, self.HEIGHT = 680, 288
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        #tile stuff
        self.tile_group = pygame.sprite.Group()

        #camera stuff
        self.camera_offset_x = 0

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
                    tile.original_x = x
                    tile.original_y = y
                    self.tile_group.add(tile)

                if cell == "Y":
                    tile = Tile(x, y)
                    tile.image.fill((255, 0, 0))
                    self.tile_group.add(tile)

def menu():
    print("Menu")
    pygame.display.update()
    game.clock.tick(80)

def game_loop():
    game.screen.fill((0, 0, 0))
    for tile in game.tile_group:
        tile.update(game.camera_offset_x)
    game.tile_group.draw(game.screen)
    game.camera_offset_x = player.x - game.WIDTH // 2
    player.draw(game.screen, game.camera_offset_x)
    player.update(game.tile_group, game.camera_offset_x)
    game.clock.tick(80)
    pygame.display.update()

def game_over_function():
    print("Game Over Function")
    game.screen.fill((255,0,0))
    pygame.display.update()
    game.clock.tick(80)

def reset():
    player.x = 0
    player.y = 100
    player.velocity_x = 0
    player.velocity_y = 0
    player.on_ground = False
    game.camera_offset_x = 0

game = Game()
#######EDIT LEVEL HERE
game.load_level("level1")
game.map_setup()
player = Player()

while running:
    print(f"game: {game_active} | menu: {menu_active} | game over: {game_over}")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and menu_active:
                menu_active = False
                game_active = True
            if event.key == pygame.K_RETURN and game_over:
                game_over = False
                reset()
                game_active = True

    if menu_active:
        menu()

    elif game_active:
        game_loop()

    elif game_over:
        game_over_function()
    

pygame.quit()