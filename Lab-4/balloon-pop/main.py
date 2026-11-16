"""
Balloon Pop

Run with:  python3 main.py

Click balloons to pop them before they reach the bottom.
  red    = normal  (+10)
  gold + = bonus   (+30)
  grey - = penalty (-15)
You have 3 lives and 30 seconds. Press R (or click Play Again) to restart
once the round is over.
"""

import pygame

from game.game_engine import GameEngine
from game.renderer import WINDOW_SIZE


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Balloon Pop")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)

    engine = GameEngine()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                engine.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                engine.handle_key(event.key)

        engine.update(dt)
        engine.draw(screen, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
