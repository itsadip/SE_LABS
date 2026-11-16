"""
click_detection: figures out whether a click landed on a balloon.
"""


def check_pop(balloons, click_pos):
    """
    Returns the balloon that was clicked, or None if the click missed
    every balloon.

    A click counts as a hit when it lands anywhere inside the balloon's
    visible circle, i.e. when the distance from the click to the centre
    is <= radius. Both sides are compared squared (dist^2 <= radius^2),
    which is equivalent and avoids a square root.

    Balloons are checked in reverse draw order, so when two balloons
    overlap, the one drawn on top is the one that pops.
    """
    for balloon in reversed(balloons):
        dx = click_pos[0] - balloon.x
        dy = click_pos[1] - balloon.y
        distance_squared = dx * dx + dy * dy
        if distance_squared <= balloon.radius * balloon.radius:
            return balloon
    return None
