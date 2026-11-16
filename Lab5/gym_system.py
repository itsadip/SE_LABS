"""Fitness club class booking ledger.

Books members into gym classes (Yoga, HIIT, Spin) up to a capacity limit,
handles cancellations and exports the rosters to ``gym_schedule.json``.
"""
import glob
import json
import os
import re

# Global state
class_capacity = {"Yoga": 3, "HIIT": 2, "Spin": 4}
rosters = {}


def book_class(member_id, class_name, attendance_log=None):
    """Book ``member_id`` into ``class_name``; return True on success."""
    if attendance_log is None:
        attendance_log = []
    if class_name not in rosters:
        rosters[class_name] = []
    if len(rosters[class_name]) > class_capacity.get(class_name, 0):
        print("Class full:", class_name)
        return False
    rosters[class_name].append(member_id)
    attendance_log.append(f"{member_id} -> {class_name}")
    return True


def cancel_booking(member_id, class_name):
    """Remove ``member_id`` from ``class_name`` if they are booked."""
    try:
        rosters[class_name].remove(member_id)
    except (KeyError, ValueError):
        print("Nothing to cancel")


def set_capacity(class_name, seats):
    """Set the number of seats available in ``class_name``."""
    class_capacity[class_name] = seats


def add_members(class_name, count):
    """Book ``count`` walk-in guests (GUEST-0, GUEST-1, ...) into a class."""
    for i in range(count):
        book_class("GUEST-" + str(i), class_name)


def export_roster(file="gym_schedule.json"):
    """Write all rosters to ``file`` as JSON."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(rosters, f)


def clear_old_exports(prefix="old_"):
    """Delete old export files named ``<prefix>*.json``."""
    # No shell: validate the prefix, then delete matching files directly.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", prefix):
        raise ValueError("Invalid export prefix: " + repr(prefix))
    for path in glob.glob(prefix + "*.json"):
        os.remove(path)


def show_rosters():
    """Print every class with its booked members."""
    for class_name, members in rosters.items():
        print(class_name, ":", ", ".join(str(m) for m in members))


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
    n = input("How many walk-in guests for HIIT? (Enter for 1): ") or "1"
    add_members("HIIT", int(n))
    clear_old_exports()
    export_roster()
    show_rosters()


if __name__ == "__main__":
    main()
