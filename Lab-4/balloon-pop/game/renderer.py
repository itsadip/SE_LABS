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
    """Top-right legend: colour swatch + points for each balloon type."""
    x = surface.get_width() - 10
    for kind in reversed(list(BALLOON_TYPES)):
        info = BALLOON_TYPES[kind]
        txt = font.render(f"{kind} {info['points']:+d}", True, COLOR_TEXT)
        x -= txt.get_width()
        surface.blit(txt, (x, 12))
        x -= 16
        pygame.draw.circle(surface, info["color"], (x + 4, 24), 9)
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


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (180, 40, 40))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)
