import pygame, sys
from settings import * 
from pygame.math import Vector2 as vector
from os import walk
from entity import Entity

class Player(Entity):
    def __init__(self, pos, groups, path, collision_sprites):
        super().__init__(pos, path, groups, collision_sprites)
        self.enemy_sprites = pygame.sprite.Group()

        # audio
        self.jump = pygame.mixer.Sound('audio/jump.wav')
        self.jump.set_volume(0.2)
        self.hit = pygame.mixer.Sound('audio/hit.wav')

        # vertical movement 
        self.gravity = 15 
        self.jump_speed = 1400 
        self.on_floor = False
        self.duck = False

        # Fall tracking to check if player has fell off the platform
        self.fall_time = 0  # 
        self.max_fall_time = 2.5

        # Initializes players death status
        self.is_dead = False

    def get_status(self):
        # idle
        if self.direction.x == 0 and self.on_floor:
            self.status = self.status.split('_')[0] + '_idle'
        # jump
        if self.direction.y != 0 and not self.on_floor:
            self.status = self.status.split('_')[0] + '_jump'

        # duck
        if self.on_floor and self.duck:
            self.status = self.status.split('_')[0] + '_duck'

    def check_contact(self):
        # checks player is on ground
        bottom_rect = pygame.Rect(0,0,self.rect.width,5)
        bottom_rect.midtop = self.rect.midbottom
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(bottom_rect):
                if self.direction.y > 0:
                    self.on_floor = True

    def input(self):
        keys = pygame.key.get_pressed()

        # Horizontal Movement
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

        # Jump
        if keys[pygame.K_UP] and self.on_floor or keys[pygame.K_w] and self.on_floor:
            self.direction.y = -self.jump_speed
            self.jump.play()

        # Duck
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.duck = True
        else:
            self.duck = False

    def move(self,dt):
        if self.duck and self.on_floor: 
            self.direction.x = 0

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision('horizontal')

        # vertical movement 
        self.direction.y += self.gravity
        self.pos.y += self.direction.y * dt
        self.rect.y = round(self.pos.y)
        self.collision('vertical')

    def check_enemy_collisions(self):
        for enemy in self.enemy_sprites:
            if self.rect.colliderect(enemy.rect):
                # Player jumped on top of the enemy
                if self.rect.bottom <= enemy.rect.top + 10 and self.direction.y > 0:
                    self.hit.play()
                    enemy.kill()
                    self.direction.y = -self.jump_speed * 0.5  # Small bounce
                else:
                    # If player hits the sides of the enemy game over.
                    self.death()
                    
    def track_fall(self, dt):
        # Check if player is falling
        if not self.on_floor and self.direction.y > 0:
            self.fall_time += dt
            # Check if player has fallen for too long
            if self.fall_time >= self.max_fall_time:
                self.death() 
        else:
            self.fall_time = 0  # Reset fall time once on ground

    def death(self):
        self.is_dead = True
 
    def update(self,dt):
        self.old_rect = self.rect.copy()
        self.input()
        self.get_status()
        self.move(dt)

        self.animate(dt)

        self.track_fall(dt)
        self.check_contact()
        self.check_enemy_collisions()

        