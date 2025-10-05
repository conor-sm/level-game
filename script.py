import pygame, sys, random, importlib
pygame.init()

running = True
menu_active = True
game_over = False
game_active = False
game_won = False

large_font = pygame.font.Font("data/font.ttf", 32)
small_font = pygame.font.Font("data/font.ttf", 24)

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.original_x = x
        self.original_y = y
        self.tile_type = tile_type

        if self.tile_type == "X":
            self.image.fill((105, 169, 194))

        elif self.tile_type == "Y":
            self.image.fill((200, 0, 0))

    def update(self, camera_offset_x):
        self.rect.x = self.original_x - camera_offset_x
        self.rect.y = self.original_y

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale((pygame.image.load("data/idle.png")), (32, 32))
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 100
        self.jump_strength = 12
        self.gravity = 0.7
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

        self.rect.topleft = (self.x - camera_offset_x, self.y)

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
            if tile.tile_type == "Y":
                next_level = level_manager.increase_level()
                if next_level:
                    reset(next_level)
                return

            if self.velocity_y > 0:
                self.rect.bottom = tile.rect.top
                self.y = self.rect.y
                self.velocity_y = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False
            if self.y > 480:
                game_active = False
                game_over = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_strength

    def draw(self, screen, camera_offset_x):
        screen.blit(self.image,(self.x - camera_offset_x, self.y))

class Game:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 680, 480
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.background = pygame.transform.scale((pygame.image.load("data/background.png")), (680, 480))

        self.tile_group = pygame.sprite.Group()

        self.camera_offset_x = 0

    def load_level(self, level_name):
        level_module = importlib.import_module(f"levels.{level_name}")
        self.level_map = getattr(level_module, f"{level_name}_map")

    def map_setup(self):
        self.tile_size = 32
        self.player_spawn = (0, 100)
        for row_index, row in enumerate(self.level_map):
            for col_index, cell in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                if cell == "X":
                    tile = Tile(x, y, "X")
                    self.tile_group.add(tile)

                elif cell == "Y":
                    tile = Tile(x, y, "Y")
                    self.tile_group.add(tile)

                elif cell == "P":
                    self.player_spawn = (x, y)

class LevelManager:
    def __init__(self):
        self.level_index = 0
        self.level_names = ["level1", "level2", "level3", "level4", "level5", "level6"]

    @property
    def level_index_readable(self):
        return self.level_index + 1

    def get_current_level(self):
        return self.level_names[self.level_index]
    
    def increase_level(self):
        global game_won, game_active
        self.level_index += 1
        if self.level_index >= len(self.level_names):
            game_active = False
            game_won = True
            return None
        return self.get_current_level()

level_manager = LevelManager()
def menu():
    pygame.display.update()
    game.clock.tick(60)

def game_loop():
    game.screen.blit(game.background, (0, 0) )
    for tile in game.tile_group:
        tile.update(game.camera_offset_x)
    game.tile_group.draw(game.screen)
    game.camera_offset_x = player.x - game.WIDTH // 2
    player.draw(game.screen, game.camera_offset_x)
    player.update(game.tile_group, game.camera_offset_x)
    level_prompt = small_font.render(f"Level: {level_manager.level_index_readable}", True, (0, 0, 0))
    game.screen.blit(level_prompt, (5, 5))
    game.clock.tick(60)
    pygame.display.update()

def game_over_function():
    print("Game Over Function")
    game.screen.fill((255,0,0))
    pygame.display.update()
    game.clock.tick(60)

def game_won_function():
    print("Game Won Function")
    game.screen.fill((0, 255, 0))
    pygame.display.update()
    game.clock.tick(60)

def reset(level_name):
    game.tile_group.empty()
    game.load_level(level_name)
    game.map_setup()

    spawn_x, spawn_y = game.player_spawn
    player.x, player.y = spawn_x, spawn_y
    player.rect.topleft = (player.x, player.y)

    player.velocity_x = 0
    player.velocity_y = 0
    player.on_ground = False
    game.camera_offset_x = 0

game = Game()
game.load_level(level_manager.get_current_level())
game.map_setup()

spawn_x, spawn_y = game.player_spawn
player = Player()
player.x, player.y = spawn_x, spawn_y
player.rect.topleft = (player.x, player.y)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and menu_active:
                menu_active = False
                game_active = True
            if event.key == pygame.K_RETURN and game_over:
                game_over = False
                reset(level_manager.get_current_level())
                game_active = True

    if menu_active:
        menu()

    elif game_active:
        game_loop()

    elif game_over:
        game_over_function()

    elif game_won:
        game_won_function()
    

pygame.quit()