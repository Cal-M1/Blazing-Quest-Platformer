import pygame, sys
from settings import * 
from pytmx.util_pygame import load_pygame
from tile import Tile, CollisionTile
from player import Player
from pygame.math import Vector2 as vector
from enemy import Enemy

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()

        # imports
        self.fg_sky = pygame.image.load('graphics/sky/back.png').convert_alpha()
        tmx_map = load_pygame('data/map.tmx')

        # Sky Setup
        self.padding = WINDOW_WIDTH /2
        self.sky_width = self.fg_sky.get_width()
        map_width = tmx_map.tilewidth * tmx_map.width + (2 * self.padding)
        self.sky_num = int(map_width // self.sky_width)

    def custom_draw(self,player):

        # change the offset vector
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        # Draws sky
        for x in range(self.sky_num):
            x_pos = -self.padding + (x * self.sky_width)
            self.display_surface.blit(self.fg_sky,(x_pos - self.offset.x / 2, 350 -self.offset.y / 2))

        # blit all sprites
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.z):
            offset_rect = sprite.image.get_rect(center = sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('CS50 Final')
        self.clock = pygame.time.Clock()

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        # audio
        main_theme = pygame.mixer.Sound('audio/theme.ogg')
        main_theme.set_volume(0.25)
        main_theme.play(loops = -1)

        self.setup()

    def setup(self):
        tmx_map = load_pygame('data/map.tmx')
        
        # collision tiles 
        for x,y, surf in tmx_map.get_layer_by_name('Level').tiles():
            CollisionTile((x * 64,y * 64), surf, [self.all_sprites,self.collision_sprites])
        
        # tiles
        for layer in ['BG', 'BG Detail', 'FG Detail Bottom', 'FG Detail Top']:
            for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Tile((x * 64,y * 64), surf, self.all_sprites, LAYERS[layer])

        # objects
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, 'graphics/player', self.collision_sprites)
            if obj.name == 'Enemy':
                Enemy((obj.x, obj.y), self.all_sprites, 'graphics/enemy', self.collision_sprites, self.player)
            if obj.name == 'End':
                self.end_area = ((obj.x, obj.y, obj.width, obj.height))

    def run(self):
        while True:

            # checks if player has died if true runs game over screen
            if self.player.is_dead:
                self.game_over()
                break 

            # checks if player has reched end of level if true runs game won screen
            elif self.player.rect.colliderect(self.end_area):
                self.game_over()  # Call game won method
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            
            self.display_surface.fill((173,216,230))
            self.all_sprites.update(dt)
            self.all_sprites.custom_draw(self.player)

            pygame.display.update()

    def game_over(self):
        # checks if player lost
        if self.player.is_dead == True:
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over', True, (255, 253, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        else: # checks if player won
            font = pygame.font.Font(None, 74)
            text = font.render('Game Won!!', True, (255, 253, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

        # Restart Game Text
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render('Press R to Restart', True, (255, 253, 255))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))

        # Draws text and fills background
        self.display_surface.fill((10, 186, 181))
        self.display_surface.blit(text, text_rect)
        self.display_surface.blit(restart_text, restart_rect)
        pygame.display.flip()

        # Player input waits till player quits or restarts
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_game()
                    waiting = False
    
    def reset_game(self):
        # Resets existing sprites
        self.all_sprites.empty()
        self.collision_sprites.empty()
        
        # resets player death status
        self.player.death = False

        # reloads the game
        self.setup()
        self.run()

if __name__ == '__main__':
    main = Main()
    main.run()
