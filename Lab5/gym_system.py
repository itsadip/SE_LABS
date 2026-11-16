"""Fitness club class booking ledger.

Books members into gym classes (Yoga, HIIT, Spin) up to a capacity limit,
handles cancellations and exports the rosters to ``gym_schedule.json``.
"""
import glob
import itertools
import json
import os
import re

# Global state
class_capacity = {"Yoga": 3, "HIIT": 2, "Spin": 4}
rosters = {}
_guest_numbers = itertools.count(1)


def book_class(member_id, class_name, attendance_log=None):
    """Book ``member_id`` into ``class_name``; return True on success."""
    if attendance_log is None:
        attendance_log = []
    if not isinstance(member_id, str) or not member_id.strip():
        print("Invalid member ID:", repr(member_id))
        return False
    if class_name not in class_capacity:
        print("Unknown class:", class_name)
        return False
    roster = rosters.setdefault(class_name, [])
    if member_id in roster:
        print("Already booked:", member_id, "in", class_name)
        return False
    if len(roster) >= class_capacity[class_name]:
        print("Class full:", class_name)
        return False
    roster.append(member_id)
    attendance_log.append(f"{member_id} -> {class_name}")
    return True


def cancel_booking(member_id, class_name):
    """Remove ``member_id`` from ``class_name``; return True if removed."""
    try:
        rosters[class_name].remove(member_id)
    except KeyError:
        print("Nothing to cancel: no bookings for class", class_name)
        return False
    except ValueError:
        print("Nothing to cancel:", member_id, "is not booked in", class_name)
        return False
    return True


def set_capacity(class_name, seats):
    """Set the seats available in ``class_name``; seats must be an int >= 0."""
    if isinstance(seats, bool) or not isinstance(seats, int) or seats < 0:
        print("Invalid capacity for", class_name + ":", seats)
        return False
    class_capacity[class_name] = seats
    return True


def add_members(class_name, count):
    """Book up to ``count`` walk-in guests; return how many got a seat."""
    booked = 0
    for _ in range(max(0, count)):
        if not book_class(f"GUEST-{next(_guest_numbers)}", class_name):
            break  # class full or unknown: stop instead of looping on
        booked += 1
    return booked


def parse_guest_count(text, default=1):
    """Turn the walk-in prompt answer into a non-negative int (or None)."""
    text = text.strip()
    if not text:
        return default
    if not (text.isascii() and text.isdigit()):
        return None
    return int(text)


def export_roster(file="gym_schedule.json"):
    """Write all rosters to ``file`` as JSON."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(rosters, f, indent=2)


def clear_old_exports(prefix="old_"):
    """Delete old export files named ``<prefix>*.json``."""
    # No shell: validate the prefix, then delete matching files directly.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", prefix):
        raise ValueError("Invalid export prefix: " + repr(prefix))
    for path in glob.glob(prefix + "*.json"):
        os.remove(path)


def show_rosters():
    """Print every class with its booked members and seat usage."""
    for class_name, members in rosters.items():
        seats = class_capacity.get(class_name, 0)
        print(f"{class_name} ({len(members)}/{seats}) :",
              ", ".join(str(m) for m in members))


def main():
    """Run the demo booking scenario."""
    book_class("M1", "Yoga")
    book_class("M2", "Yoga")
    book_class("M3", "Yoga")
    book_class("M4", "Yoga")
    book_class(55, "HIIT")
    book_class("M5", "Pilates")
    set_capacity("Spin", -2)
    add_members("Spin", 3)
    cancel_booking("M9", "Boxing")
    answer = input("How many walk-in guests for HIIT? (Enter for 1): ")
    count = parse_guest_count(answer)
    if count is None:
        print("Please enter a whole number of guests; no walk-ins added.")
    else:
        add_members("HIIT", count)
    clear_old_exports()
    export_roster()
    show_rosters()


if __name__ == "__main__":
    main()
