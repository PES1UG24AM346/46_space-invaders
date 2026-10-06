import pygame
import random
from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet
from .sounds import SoundManager

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

YELLOW = (255, 220, 50)

# Difficulty presets: (enemy_speed, enemy_fire_chance)
DIFFICULTY_SETTINGS = {
    "Easy":   (1.0, 0.005),
    "Medium": (1.5, 0.01),
    "Hard":   (2.5, 0.02),
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 30)
        self.sounds = SoundManager()
        self.reset()

    def reset(self, enemy_speed=1.5, fire_chance=0.01):
        """Reset all game state for a new round."""
        self.player = Player(self.width // 2 - 20, self.height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(self.width, speed=enemy_speed)

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        self.enemy_fire_chance = fire_chance

        self.score = 0
        self.game_over = False
        self.game_won = False
        self._end_sound_played = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2
                self.player_bullets.append(Bullet(bullet_x, self.player.y, direction=-1))
                self.sounds.play_shoot()
                self._shoot_cooldown = 15

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    @property
    def round_ended(self):
        """True when the round is over (loss or win)."""
        return self.game_over or self.game_won

    def update(self):
        if self.round_ended:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        self.enemy_grid.move()

        for enemy in self.enemy_grid.alive_enemies():
            if random.random() < self.enemy_fire_chance:
                bullet_x = enemy.x + enemy.width // 2
                self.enemy_bullets.append(Bullet(bullet_x, enemy.y + enemy.height, direction=1))

        for bullet in self.player_bullets:
            bullet.move()
        for bullet in self.enemy_bullets:
            bullet.move()

        self.player_bullets = [b for b in self.player_bullets if not b.off_screen(self.height)]
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.off_screen(self.height)]

        # Collect bullets that hit an enemy so we can remove them after
        # the loop finishes, avoiding mutation during iteration.
        bullets_to_remove = set()
        for bullet in self.player_bullets:
            if bullet in bullets_to_remove:
                continue
            bullet_rect = bullet.rect()
            for enemy in self.enemy_grid.alive_enemies():
                if bullet_rect.colliderect(enemy.rect()):
                    enemy.alive = False
                    bullets_to_remove.add(bullet)
                    self.score += 1
                    self.sounds.play_enemy_destroyed()
                    break
        self.player_bullets = [b for b in self.player_bullets if b not in bullets_to_remove]

        # Check win condition — all enemies destroyed
        if not self.enemy_grid.alive_enemies():
            self.game_won = True
            return

        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                break

        if self.enemy_grid.reached_bottom(self.player.y):
            self.game_over = True

    def render(self, screen):
        pygame.draw.rect(screen, GREEN, self.player.rect())

        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(screen, WHITE, enemy.rect())

        for bullet in self.player_bullets:
            pygame.draw.rect(screen, WHITE, bullet.rect())
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            if not self._end_sound_played:
                self.sounds.play_game_over()
                self._end_sound_played = True
            self._render_end_screen(screen, "GAME OVER", RED)
        elif self.game_won:
            if not self._end_sound_played:
                self.sounds.play_game_over()
                self._end_sound_played = True
            self._render_end_screen(screen, "SUCCESS", GREEN)

    def _render_end_screen(self, screen, title, title_color):
        # Semi-transparent dark overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont("Arial", 64, bold=True)
        score_font = pygame.font.SysFont("Arial", 36)
        option_font = pygame.font.SysFont("Arial", 28)
        hint_font = pygame.font.SysFont("Arial", 22)

        title_text = title_font.render(title, True, title_color)
        score_text = score_font.render(f"Final Score: {self.score}", True, WHITE)

        replay_text = option_font.render("Play Again?", True, YELLOW)
        easy_text   = option_font.render("1 - Easy", True, GREEN)
        medium_text = option_font.render("2 - Medium", True, WHITE)
        hard_text   = option_font.render("3 - Hard", True, RED)
        exit_text   = hint_font.render("ESC - Exit", True, (180, 180, 180))

        cx = self.width // 2
        cy = self.height // 2

        screen.blit(title_text,  (cx - title_text.get_width() // 2, cy - 120))
        screen.blit(score_text,  (cx - score_text.get_width() // 2, cy - 40))
        screen.blit(replay_text, (cx - replay_text.get_width() // 2, cy + 20))
        screen.blit(easy_text,   (cx - easy_text.get_width() // 2,   cy + 60))
        screen.blit(medium_text, (cx - medium_text.get_width() // 2, cy + 95))
        screen.blit(hard_text,   (cx - hard_text.get_width() // 2,   cy + 130))
        screen.blit(exit_text,   (cx - exit_text.get_width() // 2,   cy + 175))


