import pygame
from settings import *
from support import import_folder, get_path
from entity import Entity
from random import choice, uniform


class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites,
                 damage_player, trigger_death_particles, add_exp, create_stick_projectile):
        super().__init__(groups, pos)
        self.sprite_type = 'enemy'

        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites
        self.pos = pygame.math.Vector2(self.rect.center)

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp

        # invisibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invisibility_duration = 300

        # sounds
        self.hit_sound = pygame.mixer.Sound(get_path('../audio/hit.wav'))
        self.death_sound = pygame.mixer.Sound(get_path('../audio/death.wav'))
        self.attack_sound = pygame.mixer.Sound(monster_data[self.monster_name]['attack_sound'])
        self.hit_sound.set_volume(0.6)
        self.death_sound.set_volume(0.6)
        self.attack_sound.set_volume(0.3)

        # stick projectile
        self.create_stick_projectile = create_stick_projectile
        self.stick_timer = pygame.time.get_ticks()
        self.stick_interval = 2000  # 2초마다

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(f'../graphics/monsters/{name}/' + animation)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        direction = (player_vec - enemy_vec).normalize() if distance > 0 else pygame.math.Vector2()
        return (distance, direction)

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]
        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self, dt):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

        if not self.vulnerable:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True
        if not self.vulnerable and current_time - self.hit_time >= self.invisibility_duration:
            self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.death_sound.play()

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def shoot_stick(self):
        current_time = pygame.time.get_ticks()
        if self.monster_name == 'raccoon' and current_time - self.stick_timer >= self.stick_interval:
            self.stick_timer = current_time
            for _ in range(1):  # 1개만 발사
                angle = uniform(0, 360)
                direction = pygame.math.Vector2(1, 0).rotate(angle)
                self.create_stick_projectile(self.rect.center, direction)

    def update(self, dt):
        self.hit_reaction()
        self.move(self.speed, self.pos, dt)
        self.animate(dt)
        self.cooldown()
        self.check_death()
        self.shoot_stick()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)