import pygame
import sys
import time
from settings import *
from level import Level
from support import get_path

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Perseus Infdev 0.0.3')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.show_splash_screen()
        self.home()

        self.level = Level()
        self.game_over = False
        self.font = pygame.font.Font(None, 240)
        self.button_font = pygame.font.Font(None, 40)
        self.restart_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 50, 100, 50)
        self.quit_button = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 50, 100, 50)
        main_sound = pygame.mixer.Sound(get_path('../audio/main.ogg'))
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)

    def show_splash_screen(self):
        pygame.time.delay(1000)
        logo = pygame.image.load(get_path('../graphics/syntax.png')).convert_alpha()
        logo = pygame.transform.scale(logo, (1200, 700))  # Resize as needed
        logo_rect = logo.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill('black')

        for alpha in range(255, -1, -5):  # From black to visible
            self.screen.fill('black')
            self.screen.blit(logo, logo_rect)
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)

        pygame.time.delay(5000)

        for alpha in range(0, 256, 5):  # From visible to black
            self.screen.fill('black')
            self.screen.blit(logo, logo_rect)
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)

    def home(self):
        # Load the background poster
        original_poster = pygame.image.load(get_path('../graphics/PERSEUS.png')).convert_alpha()

        # Try loading the Joystix font safely
        try:
            play_font = pygame.font.Font(get_path('../font/joystix.ttf'), 100)
        except FileNotFoundError:
            print("Warning: joystix.ttf not found, using default font.")
            play_font = pygame.font.Font(None, 100)

        play_text = play_font.render('PLAY', True, 'black')

        while True:
            current_width, current_height = self.screen.get_size()

            # Scale the poster to fit the screen
            scaled_poster = pygame.transform.scale(original_poster, (int(current_width), int(current_height * 1.3)))
            poster_rect = scaled_poster.get_rect(center=(current_width // 2, current_height // 2 - 50))

            # Define the play button
            self.play_button = pygame.Rect(current_width // 2 - 170, current_height // 2 + 150, 370, 90)

            # Draw everything
            self.screen.fill('black')
            self.screen.blit(scaled_poster, poster_rect)
            pygame.draw.rect(self.screen, 'white', self.play_button, border_radius=12)
            self.screen.blit(play_text, play_text.get_rect(center=self.play_button.center))

            pygame.display.update()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    # Update WIDTH and HEIGHT on resize
                    global WIDTH, HEIGHT
                    WIDTH, HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_button.collidepoint(event.pos):
                        return  # Start the game

    def check_game_over(self):
        if self.level.player.health <= 0:
            self.game_over = True

    def display_game_over(self):
        text = self.font.render('GAME OVER', True, 'red')
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        pygame.draw.rect(self.screen, 'gray', self.restart_button)
        pygame.draw.rect(self.screen, 'gray', self.quit_button)
        restart_text = self.button_font.render('Restart', True, 'white')
        quit_text = self.button_font.render('Quit', True, 'white')
        self.screen.blit(restart_text, restart_text.get_rect(center=self.restart_button.center))
        self.screen.blit(quit_text, quit_text.get_rect(center=self.quit_button.center))

    def handle_buttons(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_button.collidepoint(event.pos):
                self.__init__()
            elif self.quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    def run(self):
        last_time = time.time()
        while True:
            dt = time.time() - last_time
            last_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

                    # Optional: reposition UI elements that depend on WIDTH/HEIGHT
                    self.play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 80)
                    self.restart_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 50, 100, 50)
                    self.quit_button = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 50, 100, 50)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
                if self.game_over:
                    self.handle_buttons(event)

            if not self.game_over:
                self.screen.fill(WATER_COLOR)
                self.level.run(dt)
                self.check_game_over()
            else:
                self.screen.fill('black')
                self.display_game_over()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()