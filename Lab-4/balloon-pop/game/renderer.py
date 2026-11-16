"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

from game.balloon import BALLOON_TYPES

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (200, 230, 245)
COLOR_TEXT = (30, 30, 30)


def draw_scene(surface, balloons):
    surface.fill(COLOR_BG)
    for b in balloons:
        pygame.draw.circle(surface, b.color, (int(b.x), int(b.y)), b.radius)
        # small highlight so balloons look rounder
        pygame.draw.circle(surface, (255, 255, 255),
                           (int(b.x - b.radius * 0.35), int(b.y - b.radius * 0.35)),
                           max(3, b.radius // 6))
        pygame.draw.line(surface, (120, 120, 120), (b.x, b.y + b.radius), (b.x, b.y + b.radius + 12), 2)
        if b.label:
            _draw_mark(surface, b)


def _draw_mark(surface, b):
    """Draw a '+' (bonus) or '-' (penalty) on the balloon so types are distinguishable."""
    cx, cy = int(b.x), int(b.y)
    arm = max(5, b.radius // 2)
    width = max(3, b.radius // 7)
    pygame.draw.line(surface, (255, 255, 255), (cx - arm, cy), (cx + arm, cy), width)
    if b.label == "+":
        pygame.draw.line(surface, (255, 255, 255), (cx, cy - arm), (cx, cy + arm), width)


def draw_legend(surface, font):
    """Top-right legend (second row): colour swatch + points for each balloon type."""
    font = pygame.font.SysFont("consolas", 18)
    x = surface.get_width() - 10
    for kind in reversed(list(BALLOON_TYPES)):
        info = BALLOON_TYPES[kind]
        txt = font.render(f"{kind} {info['points']:+d}", True, COLOR_TEXT)
        x -= txt.get_width()
        surface.blit(txt, (x, 42))
        x -= 16
        pygame.draw.circle(surface, info["color"], (x + 4, 52), 8)
        x -= 18


def draw_lives(surface, font, lives, pos):
    """'Lives:' followed by one small red heart-dot per remaining life."""
    label = font.render("Lives:", True, COLOR_TEXT)
    surface.blit(label, pos)
    x = pos[0] + label.get_width() + 12
    y = pos[1] + label.get_height() // 2
    for _ in range(lives):
        pygame.draw.circle(surface, (210, 40, 60), (x, y), 8)
        x += 22


def draw_timer(surface, font, time_left):
    """Countdown centred at the top; turns red in the last 5 seconds."""
    color = (200, 30, 30) if time_left <= 5 else COLOR_TEXT
    surf = font.render(f"Time: {time_left:4.1f}s", True, color)
    surface.blit(surf, (surface.get_width() // 2 - surf.get_width() // 2, 10))


def play_again_rect():
    """Clickable 'Play Again' button shown on the game-over screen."""
    return pygame.Rect(WIDTH // 2 - 90, HEIGHT // 2 + 40, 180, 44)


def draw_game_over(surface, font, reason, score):
    """Dim the field and show the reason, the final score and how to restart."""
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 120))
    surface.blit(shade, (0, 0))
    panel = pygame.Rect(0, 0, 420, 250)
    panel.center = (WIDTH // 2, HEIGHT // 2 + 10)
    pygame.draw.rect(surface, (250, 250, 250), panel, border_radius=12)
    pygame.draw.rect(surface, (60, 60, 60), panel, 3, border_radius=12)
    big = pygame.font.SysFont("consolas", 40, bold=True)
    for text, y, fnt, col in (
        (reason, panel.top + 38, font, (180, 40, 40)),
        (f"Final score: {score}", panel.top + 88, big, COLOR_TEXT),
    ):
        surf = fnt.render(text, True, col)
        surface.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))
    btn = play_again_rect()
    pygame.draw.rect(surface, (40, 140, 80), btn, border_radius=8)
    surf = font.render("Play Again", True, (255, 255, 255))
    surface.blit(surf, surf.get_rect(center=btn.center))
    hint = font.render("or press R", True, (90, 90, 90))
    surface.blit(hint, hint.get_rect(center=(WIDTH // 2, btn.bottom + 16)))


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (180, 40, 40))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)
