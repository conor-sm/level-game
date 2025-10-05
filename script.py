import pygame, sys, random, importlib
pygame.init()

running = True
menu_active = True
game_over = False
game_active = False
game_won = False
won_sound_played = False

large_font = pygame.font.Font("data/font.ttf", 48)
small_font = pygame.font.Font("data/font.ttf", 32)

game_over_sound = pygame.mixer.Sound("data/game-over.wav")
portal_sound = pygame.mixer.Sound("data/portal.ogg")
start_sound = pygame.mixer.Sound("data/jump.ogg")
won_sound = pygame.mixer.Sound("data/start.ogg")

BLOCK_IMAGE = pygame.transform.scale(pygame.image.load("data/block.png"), (32, 32))
IDLE_IMAGE = pygame.transform.scale(pygame.image.load("data/idle.png"), (32, 32))
PORTAL_IMAGE = pygame.transform.scale(pygame.image.load("data/portal.png"), (32, 32))

def gen_random_insult():
    insults = ["Caught in 4k", "Shot on iPhone", "Did you get that on camera?", "Dissapointing", "Better luck next time", "Sad", "You can do better", "The frost has gotten to you"]
    insult = random.choice(insults)
    return insult

random_insult = gen_random_insult()

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.block_image = BLOCK_IMAGE
        self.portal_image = PORTAL_IMAGE
        self.rect = self.image.get_rect(topleft=(x, y))
        self.original_x = x
        self.original_y = y
        self.tile_type = tile_type

        if self.tile_type == "X":
            self.image = self.block_image
            self.rect = self.image.get_rect(topleft=(x,y))

        elif self.tile_type == "Y":
            self.image = self.portal_image
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, camera_offset_x):
        self.rect.x = self.original_x - camera_offset_x
        self.rect.y = self.original_y

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IDLE_IMAGE
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 100
        self.jump_strength = 11.5
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
                portal_sound.play()
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
            if self.y > 512:
                global random_insult
                game_active = False
                game_over = True
                game_over_sound.play()
                random_insult = gen_random_insult()

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_strength

    def draw(self, screen, camera_offset_x):
        screen.blit(self.image,(self.x - camera_offset_x, self.y))

class Game:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 680, 512
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.background = pygame.transform.scale((pygame.image.load("data/background.png")), (680, 512))

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
        self.level_names = ["level1", "level2", "level3", "level4", "level5", "level6", "level7", "level8"]

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
    game.screen.blit(game.background, (0, 0))
    menu_text = large_font.render("Penguin: The Final Frost", True, (0, 0, 0))
    menu_prompt = small_font.render("ENTER at your own risk...", True, (0, 0, 0))
    game.screen.blit(menu_text, ((game.WIDTH - menu_text.get_width()) // 2, (game.HEIGHT - menu_text.get_height()) // 2 - 50))
    game.screen.blit(menu_prompt, ((game.WIDTH - menu_prompt.get_width()) // 2, (game.HEIGHT - menu_prompt.get_height()) // 2))
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
    global random_insult
    game.screen.blit(game.background, (0, 0))
    game_over_text = large_font.render(f"{random_insult}", True, (0, 0, 0))
    game_over_prompt = small_font.render("ENTER to retry...", True, (0, 0, 0))
    game.screen.blit(game_over_text, ((game.WIDTH - game_over_text.get_width()) // 2, (game.HEIGHT - game_over_text.get_height()) // 2 - 50))
    game.screen.blit(game_over_prompt, ((game.WIDTH - game_over_prompt.get_width()) // 2, (game.HEIGHT - game_over_prompt.get_height()) // 2))
    pygame.display.update()
    game.clock.tick(60)

def game_won_function():
    global won_sound_played
    game.screen.blit(game.background, (0, 0))
    game_won_text = large_font.render("You have won. Congratulations!", True, (0, 0, 0))
    game_won_prompt = small_font.render("thank you for playing", True, (0, 0, 0))
    game.screen.blit(game_won_text, ((game.WIDTH - game_won_text.get_width()) // 2, (game.HEIGHT - game_won_text.get_height()) // 2 - 50))
    game.screen.blit(game_won_prompt, ((game.WIDTH - game_won_prompt.get_width()) // 2, (game.HEIGHT - game_won_prompt.get_height()) // 2))
    if not won_sound_played:
        won_sound.play()
        won_sound_played = True

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
                start_sound.play()
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