import pygame
from settings import * 
from pygame.math import Vector2 as vector
from os import walk
from math import sin

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, path,groups, collision_sprites):
        super().__init__(groups)

        # setup
        self.import_assets(path)
        self.frame_index = 0
        self.status = 'right'

        # image setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['Level']

        # float based movement 
        self.direction = vector()
        self.pos = vector(self.rect.topleft)
        self.old_rect = self.rect.copy()
        self.speed = 400

        # collision
        self.collision_sprites = collision_sprites
        
    def import_assets(self, path):
        self.animations = {}
        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    self.animations[name] = []
            else:
                for file_name in sorted(folder[2], key=lambda string: int(string.split('.')[0])):
                    path = folder[0].replace('\\', '/') + '/' + file_name
                    surf = pygame.image.load(path).convert_alpha()
                    key = folder[0].split('\\')[1]
                    self.animations[key].append(surf)
                    
                    left_sprite = pygame.transform.flip(surf, True, False) 
                    if 'right' in key: 
                        left_key = key.replace('right', 'left', 1)
                        if left_key not in self.animations:
                            self.animations[left_key] = []
                        self.animations[left_key].append(left_sprite)

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):

                if direction == 'horizontal':
                    # left collision
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                    # right collision
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                    self.pos.x = self.rect.x
                else: # horizontal collision
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.on_floor = True
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    self.pos.y = self.rect.y
                    self.direction.y = 0
        
        if self.on_floor and self.direction.y != 0:
            self.on_floor = False

    def animate(self,dt):
        self.frame_index += 7 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

