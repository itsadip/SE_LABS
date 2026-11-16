# Lab 4 – Vibe Coding: Chat History (Balloon Pop)

**Name:** Aditya Pradeep · **SRN:** PES2UG24AM900 · **Repo assigned:** `SETAPESU26/05_balloon_pop`
**AI assistant used:** Claude (Claude Code, model Claude Opus 5.5)

This is the prompt/response history for the four README tasks. Each task took one prompt and one iteration, and each landed as its own git commit (hash shown). Every response includes the exact code diff that was applied.

| Commit | Task |
|--------|------|
| `df5c439` | Task 1 – Fix the click-detection bug |
| `e8cb796` | Task 2 – Implement different balloon types |
| `9b0e437` | Task 3 – Implement a lives / miss system |
| `1ee0d09` | Task 4 – Implement a timed round |

## Task 1 – Fix the click-detection bug  (commit `df5c439`)

### Prompt

> Here is `game/click_detection.py` from my Pygame Balloon Pop game. Clicking near the edge of a balloon doesn't pop it; only clicks almost exactly on the centre work. The README says `check_pop` compares the *squared* distance with the plain radius. Fix it so that any click inside the visible circle pops the balloon. Keep it efficient (no `sqrt` needed). If two balloons overlap, pop the one drawn on top.

### Response

**Diagnosis:** `distance_squared <= balloon.radius` compares units of px² with px. For a balloon of radius 30, a click registers only within √30 ≈ 5.5 px of the centre, instead of 30 px.

**Fix:** compare like with like: `dx*dx + dy*dy <= radius*radius`. This is mathematically identical to `sqrt(dx²+dy²) <= radius` and avoids the square root. I also iterate `reversed(balloons)`: the renderer draws later balloons on top, so when two overlap, the visible one pops.

**Verification:** a click 29 px from the centre of a radius-30 balloon now pops it, and a click 31 px away does not. In the after video, clicks at 75% of the radius pop reliably.

**Code changes applied:**

```diff
diff --git a/Lab-4/balloon-pop/game/click_detection.py b/Lab-4/balloon-pop/game/click_detection.py
index cae9bc9..aaea248 100644
--- a/Lab-4/balloon-pop/game/click_detection.py
+++ b/Lab-4/balloon-pop/game/click_detection.py
@@ -8,10 +8,18 @@ def check_pop(balloons, click_pos):
     Returns the balloon that was clicked, or None if the click missed
     every balloon.
+
+    A click counts as a hit when it lands anywhere inside the balloon's
+    visible circle, i.e. when the distance from the click to the centre
+    is <= radius. Both sides are compared squared (dist^2 <= radius^2),
+    which is equivalent and avoids a square root.
+
+    Balloons are checked in reverse draw order, so when two balloons
+    overlap, the one drawn on top is the one that pops.
     """
-    for balloon in balloons:
+    for balloon in reversed(balloons):
         dx = click_pos[0] - balloon.x
         dy = click_pos[1] - balloon.y
         distance_squared = dx * dx + dy * dy
-        if distance_squared <= balloon.radius:
+        if distance_squared <= balloon.radius * balloon.radius:
             return balloon
     return None
```

## Task 2 – Implement different balloon types  (commit `e8cb796`)

### Prompt

> Now add at least three balloon types: **normal** (regular points), **bonus** (more points) and **penalty** (reduces the score). Give each its own colour so they are easy to tell apart, and make sure the right effect happens when each is popped. Keep the data in one place so the values are easy to tune, and show a small legend on screen.

### Response

**Design:** a `BALLOON_TYPES` table in `balloon.py` holds the colour, points, spawn weight and an on-balloon marker for each type:

| Type | Colour | Points | Spawn weight | Marker |
|------|--------|--------|--------------|--------|
| normal | red | +10 | 65% | – |
| bonus | gold | +30 | 20% | white `+` |
| penalty | dark grey | −15 | 15% | white `−` |

`Balloon` now takes a `kind` and validates it. `_spawn_balloon` picks a kind using `random.choices(weights=…)`. `handle_click` adds `popped.points` and floors the score at 0, so a penalty can't push it negative. The renderer draws the `+`/`−` marker (useful for colour-blind players) and a legend in the top-right corner.

**Verification:** a headless test spawned all three kinds. Clicking the edge of a bonus balloon gave a score of 30; a penalty click then gave 15.

**Code changes applied:**

```diff
diff --git a/Lab-4/balloon-pop/game/balloon.py b/Lab-4/balloon-pop/game/balloon.py
index d0aafad..b266ddb 100644
--- a/Lab-4/balloon-pop/game/balloon.py
+++ b/Lab-4/balloon-pop/game/balloon.py
@@ -3,16 +3,32 @@ Balloon: falls from the top of the screen. The player must pop it
 before it reaches the bottom. Balloons vary in size - this matters for
 how click detection should work.
+
+Each balloon has a *kind* that decides its colour and what happens when
+it is popped (see BALLOON_TYPES).
 """
 
 import pygame
 
+# kind -> settings. "points" is added to the score when the balloon is
+# popped (negative = penalty). "weight" is the relative spawn chance.
+BALLOON_TYPES = {
+    "normal": {"color": (220, 70, 95), "points": 10, "weight": 65, "label": ""},
+    "bonus": {"color": (245, 185, 30), "points": 30, "weight": 20, "label": "+"},
+    "penalty": {"color": (70, 70, 85), "points": -15, "weight": 15, "label": "-"},
+}
+
 
 class Balloon:
-    def __init__(self, x, y, radius, speed, color=(220, 90, 120)):
+    def __init__(self, x, y, radius, speed, kind="normal"):
+        if kind not in BALLOON_TYPES:
+            raise ValueError(f"Unknown balloon kind: {kind!r}")
         self.x = x
         self.y = y
         self.radius = radius
         self.speed = speed
-        self.color = color
+        self.kind = kind
+        self.color = BALLOON_TYPES[kind]["color"]
+        self.points = BALLOON_TYPES[kind]["points"]
+        self.label = BALLOON_TYPES[kind]["label"]
 
     def update(self):
diff --git a/Lab-4/balloon-pop/game/game_engine.py b/Lab-4/balloon-pop/game/game_engine.py
index 9569186..9624f95 100644
--- a/Lab-4/balloon-pop/game/game_engine.py
+++ b/Lab-4/balloon-pop/game/game_engine.py
@@ -2,17 +2,15 @@
 GameEngine: owns all balloons, spawns new ones, and handles clicks.
 
-Starter version: one balloon type (random size, fixed points), no
-lives system yet, no timer yet. Click detection also has a known bug
-(see game/click_detection.py) that Task 1 asks you to fix.
+Balloon types: normal (+10), bonus (+30) and penalty (-15), each with
+its own colour (see game/balloon.py).
 """
 
 import random
 
-from game.balloon import Balloon
+from game.balloon import Balloon, BALLOON_TYPES
 from game.click_detection import check_pop
 from game.renderer import WIDTH, HEIGHT
 
 SPAWN_INTERVAL_FRAMES = 45
-POINTS_PER_POP = 10
 
 
@@ -27,5 +25,8 @@ class GameEngine:
         x = random.randint(radius + 10, WIDTH - radius - 10)
         speed = random.uniform(1.5, 3.0)
-        self.balloons.append(Balloon(x=x, y=-radius, radius=radius, speed=speed))
+        kinds = list(BALLOON_TYPES)
+        weights = [BALLOON_TYPES[k]["weight"] for k in kinds]
+        kind = random.choices(kinds, weights=weights, k=1)[0]
+        self.balloons.append(Balloon(x=x, y=-radius, radius=radius, speed=speed, kind=kind))
 
     def handle_click(self, pos):
@@ -33,5 +34,6 @@ class GameEngine:
         if popped is not None:
             self.balloons.remove(popped)
-            self.score += POINTS_PER_POP
+            # score can't go below zero from a penalty balloon
+            self.score = max(0, self.score + popped.points)
 
     def update(self):
@@ -50,2 +52,3 @@ class GameEngine:
         renderer.draw_scene(surface, self.balloons)
         renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
+        renderer.draw_legend(surface, font)
diff --git a/Lab-4/balloon-pop/game/renderer.py b/Lab-4/balloon-pop/game/renderer.py
index cd1fcfb..ed231e0 100644
--- a/Lab-4/balloon-pop/game/renderer.py
+++ b/Lab-4/balloon-pop/game/renderer.py
@@ -5,4 +5,6 @@ renderer: all pygame drawing lives here, kept separate from game logic.
 import pygame
 
+from game.balloon import BALLOON_TYPES
+
 WIDTH, HEIGHT = 700, 500
 WINDOW_SIZE = (WIDTH, HEIGHT)
@@ -16,5 +18,34 @@ def draw_scene(surface, balloons):
     for b in balloons:
         pygame.draw.circle(surface, b.color, (int(b.x), int(b.y)), b.radius)
+        # small highlight so balloons look rounder
+        pygame.draw.circle(surface, (255, 255, 255),
+                           (int(b.x - b.radius * 0.35), int(b.y - b.radius * 0.35)),
+                           max(3, b.radius // 6))
         pygame.draw.line(surface, (120, 120, 120), (b.x, b.y + b.radius), (b.x, b.y + b.radius + 12), 2)
+        if b.label:
+            _draw_mark(surface, b)
+
+
+def _draw_mark(surface, b):
+    """Draw a '+' (bonus) or '-' (penalty) on the balloon so types are distinguishable."""
+    cx, cy = int(b.x), int(b.y)
+    arm = max(5, b.radius // 2)
+    width = max(3, b.radius // 7)
+    pygame.draw.line(surface, (255, 255, 255), (cx - arm, cy), (cx + arm, cy), width)
+    if b.label == "+":
+        pygame.draw.line(surface, (255, 255, 255), (cx, cy - arm), (cx, cy + arm), width)
+
+
+def draw_legend(surface, font):
+    """Top-right legend: colour swatch + points for each balloon type."""
+    x = surface.get_width() - 10
+    for kind in reversed(list(BALLOON_TYPES)):
+        info = BALLOON_TYPES[kind]
+        txt = font.render(f"{kind} {info['points']:+d}", True, COLOR_TEXT)
+        x -= txt.get_width()
+        surface.blit(txt, (x, 12))
+        x -= 16
+        pygame.draw.circle(surface, info["color"], (x + 4, 24), 9)
+        x -= 18
```

## Task 3 – Implement a lives / miss system  (commit `9b0e437`)

### Prompt

> Add 3 lives. Whenever a balloon reaches the bottom of the screen without being popped, the player loses a life. Show the remaining lives on screen and end the game when they reach zero. Popping a balloon must never cost a life, whatever its type.

### Response

**Change:** the engine has `lives = 3` and a `game_over` flag. In `update()`, balloons past the bottom are collected as `missed`, removed from play, and each costs one life (any type, as the README says). The click path never touches `lives`, so popping can't cost one. When lives reach 0, the game stops: no updates, clicks are ignored, and the field is cleared. A banner shows the final score. The renderer draws `Lives:` followed by one red dot per life.

**Verification:** a headless run with no clicks reached game over after 338 frames with lives = 0 and the field cleared.

**Code changes applied:**

```diff
diff --git a/Lab-4/balloon-pop/game/game_engine.py b/Lab-4/balloon-pop/game/game_engine.py
index 9624f95..dcde2b1 100644
--- a/Lab-4/balloon-pop/game/game_engine.py
+++ b/Lab-4/balloon-pop/game/game_engine.py
@@ -4,4 +4,8 @@ GameEngine: owns all balloons, spawns new ones, and handles clicks.
 Balloon types: normal (+10), bonus (+30) and penalty (-15), each with
 its own colour (see game/balloon.py).
+
+Lives: the player starts with 3 lives and loses one for every balloon
+(of any type) that falls past the bottom unpopped. Popping never costs
+a life. The game is over when lives reach zero.
 """
 
@@ -13,4 +17,5 @@ from game.renderer import WIDTH, HEIGHT
 
 SPAWN_INTERVAL_FRAMES = 45
+STARTING_LIVES = 3
 
 
@@ -20,4 +25,6 @@ class GameEngine:
         self.frames_until_spawn = 0
         self.score = 0
+        self.lives = STARTING_LIVES
+        self.game_over = False
 
     def _spawn_balloon(self):
@@ -31,4 +38,6 @@ class GameEngine:
 
     def handle_click(self, pos):
+        if self.game_over:
+            return
         popped = check_pop(self.balloons, pos)
         if popped is not None:
@@ -38,4 +47,6 @@ class GameEngine:
 
     def update(self):
+        if self.game_over:
+            return
         self.frames_until_spawn -= 1
         if self.frames_until_spawn <= 0:
@@ -46,5 +57,11 @@ class GameEngine:
             b.update()
 
-        self.balloons = [b for b in self.balloons if not b.is_past_bottom(HEIGHT)]
+        missed = [b for b in self.balloons if b.is_past_bottom(HEIGHT)]
+        if missed:
+            self.balloons = [b for b in self.balloons if b not in missed]
+            self.lives = max(0, self.lives - len(missed))
+            if self.lives == 0:
+                self.game_over = True
+                self.balloons.clear()
 
     def draw(self, surface, font):
@@ -52,3 +69,6 @@ class GameEngine:
         renderer.draw_scene(surface, self.balloons)
         renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
+        renderer.draw_lives(surface, font, self.lives, (10, 38))
         renderer.draw_legend(surface, font)
+        if self.game_over:
+            renderer.draw_banner(surface, font, f"Out of lives!  Final score: {self.score}")
diff --git a/Lab-4/balloon-pop/game/renderer.py b/Lab-4/balloon-pop/game/renderer.py
index ed231e0..8074a9a 100644
--- a/Lab-4/balloon-pop/game/renderer.py
+++ b/Lab-4/balloon-pop/game/renderer.py
@@ -50,4 +50,15 @@ def draw_legend(surface, font):
 
 
+def draw_lives(surface, font, lives, pos):
+    """'Lives:' followed by one small red heart-dot per remaining life."""
+    label = font.render("Lives:", True, COLOR_TEXT)
+    surface.blit(label, pos)
+    x = pos[0] + label.get_width() + 12
+    y = pos[1] + label.get_height() // 2
+    for _ in range(lives):
+        pygame.draw.circle(surface, (210, 40, 60), (x, y), 8)
+        x += 22
+
+
 def draw_text(surface, font, text, pos, color=COLOR_TEXT):
     surface.blit(font.render(text, True, color), pos)
```

## Task 4 – Implement a timed round  (commit `1ee0d09`)

### Prompt

> Add a 30-second countdown for the round and show the remaining time on screen. When it reaches zero, or lives run out, stop spawning and accepting balloons, show the final score clearly, and give a way to start a new round with the score, lives and timer all reset. Make the timer frame-rate independent.

### Response

**Change:**
* `GameEngine.reset()` initialises the score, lives, timer, balloons and state. `__init__` and restart both call it, so nothing can be left un-reset.
* `update(dt)` takes real elapsed seconds; `main.py` passes `clock.tick(60)/1000`. The timer therefore follows wall-clock time even if frames drop.
* `_end_round(reason)` is shared by "Time's up!" and "Out of lives!": it sets `game_over`, clears balloons and stops spawning.
* The game-over screen dims the field and shows the reason, a large **Final score** and a **Play Again** button. Pressing **R** also restarts (`handle_key`). The timer is centred at the top and turns red in the last 5 seconds.

**Verification:** a headless run that kept popping balloons ended with "Time's up!" after 30.0 s with lives = 3. A stray click afterwards had no effect, and *Play Again* reset everything to score 0, lives 3, time 30.0 and `game_over = False`.

**Code changes applied:**

```diff
diff --git a/Lab-4/balloon-pop/game/game_engine.py b/Lab-4/balloon-pop/game/game_engine.py
index dcde2b1..7a2201c 100644
--- a/Lab-4/balloon-pop/game/game_engine.py
+++ b/Lab-4/balloon-pop/game/game_engine.py
@@ -7,9 +7,17 @@ its own colour (see game/balloon.py).
 Lives: the player starts with 3 lives and loses one for every balloon
 (of any type) that falls past the bottom unpopped. Popping never costs
-a life. The game is over when lives reach zero.
+a life.
+
+Timed round: each round lasts 30 seconds. The round ends when the timer
+reaches zero or lives reach zero, whichever comes first. After that no
+balloons spawn or accept clicks, the final score is shown, and pressing
+R (or clicking "Play Again") starts a fresh round with score, lives and
+timer all reset.
 """
 
 import random
 
+import pygame
+
 from game.balloon import Balloon, BALLOON_TYPES
 from game.click_detection import check_pop
@@ -18,13 +26,26 @@ from game.renderer import WIDTH, HEIGHT
 SPAWN_INTERVAL_FRAMES = 45
 STARTING_LIVES = 3
+ROUND_SECONDS = 30.0
+FRAME_SECONDS = 1 / 60
 
 
 class GameEngine:
     def __init__(self):
+        self.reset()
+
+    def reset(self):
+        """Start a new round: score, lives, timer and balloons all reset."""
         self.balloons = []
         self.frames_until_spawn = 0
         self.score = 0
         self.lives = STARTING_LIVES
+        self.time_left = ROUND_SECONDS
         self.game_over = False
+        self.end_reason = ""
+
+    def _end_round(self, reason):
+        self.game_over = True
+        self.end_reason = reason
+        self.balloons.clear()
 
     def _spawn_balloon(self):
@@ -39,4 +60,7 @@ class GameEngine:
     def handle_click(self, pos):
         if self.game_over:
+            from game import renderer
+            if renderer.play_again_rect().collidepoint(pos):
+                self.reset()
             return
         popped = check_pop(self.balloons, pos)
@@ -46,7 +70,18 @@ class GameEngine:
             self.score = max(0, self.score + popped.points)
 
-    def update(self):
+    def handle_key(self, key):
+        if key == pygame.K_r and self.game_over:
+            self.reset()
+
+    def update(self, dt=FRAME_SECONDS):
+        """Advance the game by one frame. dt = seconds since the last frame."""
         if self.game_over:
             return
+
+        self.time_left = max(0.0, self.time_left - dt)
+        if self.time_left <= 0:
+            self._end_round("Time's up!")
+            return
+
         self.frames_until_spawn -= 1
         if self.frames_until_spawn <= 0:
@@ -62,6 +97,5 @@ class GameEngine:
             self.lives = max(0, self.lives - len(missed))
             if self.lives == 0:
-                self.game_over = True
-                self.balloons.clear()
+                self._end_round("Out of lives!")
 
     def draw(self, surface, font):
@@ -70,5 +104,6 @@ class GameEngine:
         renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
         renderer.draw_lives(surface, font, self.lives, (10, 38))
+        renderer.draw_timer(surface, font, self.time_left)
         renderer.draw_legend(surface, font)
         if self.game_over:
-            renderer.draw_banner(surface, font, f"Out of lives!  Final score: {self.score}")
+            renderer.draw_game_over(surface, font, self.end_reason, self.score)
diff --git a/Lab-4/balloon-pop/game/renderer.py b/Lab-4/balloon-pop/game/renderer.py
index 8074a9a..b5751eb 100644
--- a/Lab-4/balloon-pop/game/renderer.py
+++ b/Lab-4/balloon-pop/game/renderer.py
@@ -38,5 +38,6 @@ def _draw_mark(surface, b):
 
 def draw_legend(surface, font):
-    """Top-right legend: colour swatch + points for each balloon type."""
+    """Top-right legend (second row): colour swatch + points for each balloon type."""
+    font = pygame.font.SysFont("consolas", 18)
     x = surface.get_width() - 10
     for kind in reversed(list(BALLOON_TYPES)):
@@ -44,7 +45,7 @@ def draw_legend(surface, font):
         txt = font.render(f"{kind} {info['points']:+d}", True, COLOR_TEXT)
         x -= txt.get_width()
-        surface.blit(txt, (x, 12))
+        surface.blit(txt, (x, 42))
         x -= 16
-        pygame.draw.circle(surface, info["color"], (x + 4, 24), 9)
+        pygame.draw.circle(surface, info["color"], (x + 4, 52), 8)
         x -= 18
 
@@ -61,4 +62,40 @@ def draw_lives(surface, font, lives, pos):
 
 
+def draw_timer(surface, font, time_left):
+    """Countdown centred at the top; turns red in the last 5 seconds."""
+    color = (200, 30, 30) if time_left <= 5 else COLOR_TEXT
+    surf = font.render(f"Time: {time_left:4.1f}s", True, color)
+    surface.blit(surf, (surface.get_width() // 2 - surf.get_width() // 2, 10))
+
+
+def play_again_rect():
+    """Clickable 'Play Again' button shown on the game-over screen."""
+    return pygame.Rect(WIDTH // 2 - 90, HEIGHT // 2 + 40, 180, 44)
+
+
+def draw_game_over(surface, font, reason, score):
+    """Dim the field and show the reason, the final score and how to restart."""
+    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
+    shade.fill((0, 0, 0, 120))
+    surface.blit(shade, (0, 0))
+    panel = pygame.Rect(0, 0, 420, 250)
+    panel.center = (WIDTH // 2, HEIGHT // 2 + 10)
+    pygame.draw.rect(surface, (250, 250, 250), panel, border_radius=12)
+    pygame.draw.rect(surface, (60, 60, 60), panel, 3, border_radius=12)
+    big = pygame.font.SysFont("consolas", 40, bold=True)
+    for text, y, fnt, col in (
+        (reason, panel.top + 38, font, (180, 40, 40)),
+        (f"Final score: {score}", panel.top + 88, big, COLOR_TEXT),
+    ):
+        surf = fnt.render(text, True, col)
+        surface.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))
+    btn = play_again_rect()
+    pygame.draw.rect(surface, (40, 140, 80), btn, border_radius=8)
+    surf = font.render("Play Again", True, (255, 255, 255))
+    surface.blit(surf, surf.get_rect(center=btn.center))
+    hint = font.render("or press R", True, (90, 90, 90))
+    surface.blit(hint, hint.get_rect(center=(WIDTH // 2, btn.bottom + 16)))
+
+
 def draw_text(surface, font, text, pos, color=COLOR_TEXT):
     surface.blit(font.render(text, True, color), pos)
diff --git a/Lab-4/balloon-pop/main.py b/Lab-4/balloon-pop/main.py
index 2a0d793..9d5b5ce 100644
--- a/Lab-4/balloon-pop/main.py
+++ b/Lab-4/balloon-pop/main.py
@@ -1,8 +1,13 @@
 """
-Balloon Pop (Lab Starter)
+Balloon Pop
 
 Run with:  python3 main.py
 
 Click balloons to pop them before they reach the bottom.
+  red    = normal  (+10)
+  gold + = bonus   (+30)
+  grey - = penalty (-15)
+You have 3 lives and 30 seconds. Press R (or click Play Again) to restart
+once the round is over.
 """
 
@@ -23,15 +28,17 @@ def main():
     running = True
     while running:
+        dt = clock.tick(60) / 1000.0
         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 running = False
-            elif event.type == pygame.MOUSEBUTTONDOWN:
+            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                 engine.handle_click(event.pos)
+            elif event.type == pygame.KEYDOWN:
+                engine.handle_key(event.key)
 
-        engine.update()
+        engine.update(dt)
         engine.draw(screen, font)
 
         pygame.display.flip()
-        clock.tick(60)
 
     pygame.quit()
```

## Result

* **Before video** (`videos/before_changes.mp4`): clicks inside a balloon's circle miss (red ✕); only pixel-perfect centre clicks pop it (green ring).
* **After video** (`videos/after_changes.mp4`): edge clicks pop every type (normal +10, bonus +30, penalty −15). Missed balloons cost lives, the round ends with the final score shown, and R starts a fresh round.

