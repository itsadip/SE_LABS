"""
GameEngine: owns all balloons, spawns new ones, and handles clicks.

Balloon types: normal (+10), bonus (+30) and penalty (-15), each with
its own colour (see game/balloon.py).

Lives: the player starts with 3 lives and loses one for every balloon
(of any type) that falls past the bottom unpopped. Popping never costs
a life.

Timed round: each round lasts 30 seconds. The round ends when the timer
reaches zero or lives reach zero, whichever comes first. After that no
balloons spawn or accept clicks, the final score is shown, and pressing
R (or clicking "Play Again") starts a fresh round with score, lives and
timer all reset.
"""

import random

import pygame

from game.balloon import Balloon, BALLOON_TYPES
from game.click_detection import check_pop
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 45
STARTING_LIVES = 3
ROUND_SECONDS = 30.0
FRAME_SECONDS = 1 / 60


class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        """Start a new round: score, lives, timer and balloons all reset."""
        self.balloons = []
        self.frames_until_spawn = 0
        self.score = 0
        self.lives = STARTING_LIVES
        self.time_left = ROUND_SECONDS
        self.game_over = False
        self.end_reason = ""

    def _end_round(self, reason):
        self.game_over = True
        self.end_reason = reason
        self.balloons.clear()

    def _spawn_balloon(self):
        radius = random.randint(16, 44)
        x = random.randint(radius + 10, WIDTH - radius - 10)
        speed = random.uniform(1.5, 3.0)
        kinds = list(BALLOON_TYPES)
        weights = [BALLOON_TYPES[k]["weight"] for k in kinds]
        kind = random.choices(kinds, weights=weights, k=1)[0]
        self.balloons.append(Balloon(x=x, y=-radius, radius=radius, speed=speed, kind=kind))

    def handle_click(self, pos):
        if self.game_over:
            from game import renderer
            if renderer.play_again_rect().collidepoint(pos):
                self.reset()
            return
        popped = check_pop(self.balloons, pos)
        if popped is not None:
            self.balloons.remove(popped)
            # score can't go below zero from a penalty balloon
            self.score = max(0, self.score + popped.points)

    def handle_key(self, key):
        if key == pygame.K_r and self.game_over:
            self.reset()

    def update(self, dt=FRAME_SECONDS):
        """Advance the game by one frame. dt = seconds since the last frame."""
        if self.game_over:
            return

        self.time_left = max(0.0, self.time_left - dt)
        if self.time_left <= 0:
            self._end_round("Time's up!")
            return

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_balloon()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for b in self.balloons:
            b.update()

        missed = [b for b in self.balloons if b.is_past_bottom(HEIGHT)]
        if missed:
            self.balloons = [b for b in self.balloons if b not in missed]
            self.lives = max(0, self.lives - len(missed))
            if self.lives == 0:
                self._end_round("Out of lives!")

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.balloons)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_lives(surface, font, self.lives, (10, 38))
        renderer.draw_timer(surface, font, self.time_left)
        renderer.draw_legend(surface, font)
        if self.game_over:
            renderer.draw_game_over(surface, font, self.end_reason, self.score)
