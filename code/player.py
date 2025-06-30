import pygame
import sys
from settings import HITBOX_OFFSET, weapon_data, magic_data
from support import get_path, import_folder
from entity import Entity


class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups, pos)
        player_path = get_path('../graphics/test/player.png')
        self.image = pygame.image.load(player_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        # graphics
        self.import_player_assets()
        self.status = 'down'
        self.shield = False
        self.shield_image = None

        # Load shield image
        shield_path = get_path('../graphics/player/shield/shield-1.png')
        self.shield_image = pygame.image.load(shield_path).convert_alpha()

        # movement
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.pos = pygame.math.Vector2(self.rect.center)
        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None  # <- FIXED

        # stats
        self.stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 3,
            'speed': 300
        }
        self.max_stats = {
            'health': 300,
            'energy': 140,
            'attack': 20,
            'magic': 10,
            'speed': 720
        }
        self.upgrade_cost = {
            'health': 100,
            'energy': 100,
            'attack': 100,
            'magic': 100,
            'speed': 100
        }
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.speed = self.stats['speed']
        self.exp = 0

        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # sound
        self.weapon_attack_sound = pygame.mixer.Sound(get_path('../audio/sword.wav'))
        self.weapon_attack_sound.set_volume(0.2)

    def import_player_assets(self):
        character_path = get_path('../graphics/player')
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [],
        }

        for animation in self.animations.keys():
            full_path = character_path + '/' + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # Movement
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # Attack
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()
                self.direction.x = 0
                self.direction.y = 0

            # Magic
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

                style = self.magic
                strength = magic_data[style]['strength'] + self.stats['magic']
                cost = magic_data[style]['cost']
                self.create_magic(style, strength, cost)
                self.direction.x = 0
                self.direction.y = 0

            # Weapon switching
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                self.weapon_index = (self.weapon_index + 1) % len(weapon_data)
                self.weapon = list(weapon_data.keys())[self.weapon_index]

            # Magic switching
            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
                self.magic_index = (self.magic_index + 1) % len(magic_data)
                self.magic = list(magic_data.keys())[self.magic_index]

            # Shield toggle
            if keys[pygame.K_r]:
                self.shield = True
            else:
                self.shield = False

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status += '_idle'
        if self.attacking:
            if 'attack' not in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status += '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking and current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
            self.attacking = False
            self.destroy_attack()

        if not self.can_switch_weapon and current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
            self.can_switch_weapon = True

        if not self.can_switch_magic and current_time - self.magic_switch_time >= self.switch_duration_cooldown:
            self.can_switch_magic = True

        if not self.vulnerable and current_time - self.hurt_time >= self.invulnerability_duration:
            self.vulnerable = True

    def animate(self, dt):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
        if not self.vulnerable:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    def get_shield_rect(self):
        if self.shield and self.shield_image:
            shield_rect = self.shield_image.get_rect(center=self.rect.center)
            shield_rect.y -= -10  # Offset upward
            return shield_rect
        return None

    def get_full_weapon_damage(self):
        return self.stats['attack'] + weapon_data[self.weapon]['damage']

    def get_full_magic_damage(self):
        return self.stats['magic'] + magic_data[self.magic]['strength']

    def get_value_by_index(self, idx):
        return list(self.stats.values())[idx]

    def get_cost_by_index(self, idx):
        return list(self.upgrade_cost.values())[idx]

    def energy_recovery(self, dt):
        if self.energy < self.stats['energy']:
            self.energy += self.stats['magic'] * dt
        else:
            self.energy = self.stats['energy']

    def update(self, dt):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate(dt)
        self.move(self.stats['speed'], self.pos, dt)
        self.energy_recovery(dt)

    @staticmethod
    def check_shield(self):
        if self.shield:
            return True
        else:
            return False

# Game loop
def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Example player
    player = Player(
        pos=(400, 300),
        groups=[],
        obstacle_sprites=[],
        create_attack=lambda: None,
        destroy_attack=lambda: None,
        create_magic=lambda style, strength, cost: None
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        dt = clock.tick(60) / 1000
        player.update(dt)

        screen.fill((30, 30, 30))
        screen.blit(player.image, player.rect)

        shield_rect = player.get_shield_rect()
        if shield_rect:
            screen.blit(player.shield_image, shield_rect)

        pygame.display.flip()

if __name__ == '__main__':
    game_loop()
