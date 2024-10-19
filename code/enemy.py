import pygame
from settings import * 
from pygame.math import Vector2 as vector
from os import walk
from entity import Entity

class Enemy(Entity):
    def __init__(self, pos, groups, path, collision_sprites, player):
        super().__init__(pos, path, groups, collision_sprites)
        self.player = player
        self.player.enemy_sprites.add(self)

        # makes sure enemy is on platform
        for sprite in collision_sprites.sprites():
            if sprite.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = sprite.rect.top

        # Movement settings
        self.speed = 100  # Speed of enemy movement
        self.collision_sprites = collision_sprites

        # Initialize direction
        self.direction = vector(1, 0)

        # vertical movement 
        self.gravity = 15 
        self.jump_speed = 1400 
        self.on_floor = False
        self.duck = False
       
    def move(self, dt):
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision('horizontal')

        # vertical movement 
        self.direction.y += self.gravity
        self.pos.y += self.direction.y * dt
        self.rect.y = round(self.pos.y)
        self.collision('vertical')

        self.check_platform_edges()

    def check_platform_edges(self):
        # Checks if there is no floor ahead if so turns enemy around
        test_point = self.rect.midbottom + pygame.math.Vector2(self.direction.x * self.rect.width/2, 5)
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.collidepoint(test_point):
                return
        self.direction.x *= -1

    def get_status(self):
        # Moving
        if self.direction.x != 0:
            if self.direction.x > 0:
                self.status = 'left'
            else:
                self.status = 'right'
        # Idle
        else:
            if self.direction.x >= 0:  # Use the last direction to determine idle facing
                self.status = 'left'
            else:
                self.status = 'right'

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.move(dt)
        self.get_status()
        self.animate(dt)