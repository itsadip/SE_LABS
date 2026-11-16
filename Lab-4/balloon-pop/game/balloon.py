"""
Balloon: falls from the top of the screen. The player must pop it
before it reaches the bottom. Balloons vary in size - this matters for
how click detection should work.

Each balloon has a *kind* that decides its colour and what happens when
it is popped (see BALLOON_TYPES).
"""

import pygame

# kind -> settings. "points" is added to the score when the balloon is
# popped (negative = penalty). "weight" is the relative spawn chance.
BALLOON_TYPES = {
    "normal": {"color": (220, 70, 95), "points": 10, "weight": 65, "label": ""},
    "bonus": {"color": (245, 185, 30), "points": 30, "weight": 20, "label": "+"},
    "penalty": {"color": (70, 70, 85), "points": -15, "weight": 15, "label": "-"},
}


class Balloon:
    def __init__(self, x, y, radius, speed, kind="normal"):
        if kind not in BALLOON_TYPES:
            raise ValueError(f"Unknown balloon kind: {kind!r}")
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.kind = kind
        self.color = BALLOON_TYPES[kind]["color"]
        self.points = BALLOON_TYPES[kind]["points"]
        self.label = BALLOON_TYPES[kind]["label"]

    def update(self):
        self.y += self.speed

    def is_past_bottom(self, height):
        return self.y - self.radius > height

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2,
        )
