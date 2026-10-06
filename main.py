import pygame
from game.game_engine import GameEngine, DIFFICULTY_SETTINGS

# Initialize pygame/Start application
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Pygame Version")

# Colors
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Difficulty keys: 1 = Easy, 2 = Medium, 3 = Hard
DIFFICULTY_KEYS = {
    pygame.K_1: "Easy",
    pygame.K_2: "Medium",
    pygame.K_3: "Hard",
}

# Game loop
engine = GameEngine(WIDTH, HEIGHT)

def main():
    running = True
    while running:
        SCREEN.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif engine.round_ended:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in DIFFICULTY_KEYS:
                        name = DIFFICULTY_KEYS[event.key]
                        speed, fire_chance = DIFFICULTY_SETTINGS[name]
                        engine.reset(enemy_speed=speed, fire_chance=fire_chance)
            else:
                engine.handle_event(event)

        if not engine.round_ended:
            engine.handle_input()
            engine.update()
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
