import pygame
from support import get_path

class StickProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(get_path('../graphics/particles/stick.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = direction
        self.speed = 5
        self.obstacle_sprites = obstacle_sprites
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 10000000  # 2초 후 제거

    def update(self, dt):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        # 충돌 시 제거
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                self.kill()

        # 수명 제한
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()