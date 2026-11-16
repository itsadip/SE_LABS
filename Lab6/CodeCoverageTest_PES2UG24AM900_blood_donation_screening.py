"""Lab 6 - Code (line) coverage tests for blood_donation_screening.py

Aditya Pradeep - PES2UG24AM900

Goal: execute every line of the module at least once (>= 90% line coverage).
Each test is aimed at one or more specific statements; the line numbers
in the comments refer to blood_donation_screening.py.
"""
import pytest

from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def _cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {"clinic_registered": registered, "type": ctype,
            "fast_track": fast_track, "donors": donors}


HEALTHY = {"age": 25, "weight_kg": 65, "hb": 14.0}


# ---------------- process_donor_cohort ----------------

def test_single_accepted_donor():
    """Lines 5-18, 33, 38-42: one healthy donor -> ACCEPTED with one unit."""
    result = process_donor_cohort([_cohort([HEALTHY])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_invalid_cohort_list_raises():
    """Lines 2-3: cohorts that is not a list -> ValueError."""
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort("not-a-list", 450)


def test_unregistered_cohort_is_skipped():
    """Lines 9-10: unregistered clinic cohort is ignored -> ZERO_YIELD (40-41)."""
    result = process_donor_cohort([_cohort([HEALTHY], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_underage_or_underweight_donor_is_deferred():
    """Lines 20-22: age < 17 / weight < 50 -> deferred, not collected."""
    donors = [{"age": 16, "weight_kg": 70, "hb": 14.0}, HEALTHY]
    result = process_donor_cohort([_cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_low_hemoglobin_high_altitude_resets_and_stops():
    """Lines 24-28: low Hb in a high-altitude cohort wipes the cohort's yield."""
    donors = [HEALTHY, {"age": 30, "weight_kg": 70, "hb": 11.0}, HEALTHY]
    result = process_donor_cohort([_cohort(donors, ctype="high_altitude")], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_hemoglobin_is_deferred():
    """Lines 29-31: Hb > 18.0 -> deferred."""
    donors = [{"age": 40, "weight_kg": 80, "hb": 19.0}, HEALTHY]
    result = process_donor_cohort([_cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_fast_track_cohort_adds_bonus_volume():
    """Lines 35-36: fast-track cohort adds 50 ml."""
    result = process_donor_cohort([_cohort([HEALTHY], fast_track=True)], 450)
    assert result == {"collected_ml": 500, "status": "ACCEPTED"}


def test_more_than_four_deferrals_is_high_deferral():
    """Lines 38-39: more than 4 deferred donors -> HIGH_DEFERRAL."""
    donors = [{"age": 15, "weight_kg": 40, "hb": 13.0}] * 5 + [HEALTHY]
    result = process_donor_cohort([_cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


# ---------------- verify_storage_centrifuge ----------------

def test_centrifuge_no_data():
    """Lines 46-47: empty run list -> NO_DATA."""
    assert verify_storage_centrifuge([]) == "NO_DATA"


def test_centrifuge_two_consecutive_drops_abort():
    """Lines 49-55: two consecutive RPM readings < 3000 -> ABORT_SPIN."""
    assert verify_storage_centrifuge([[3500, 2900, 2800, 3600]]) == "ABORT_SPIN"


def test_centrifuge_isolated_drop_is_stable():
    """Lines 56-58: a drop followed by recovery resets the streak -> STABLE."""
    assert verify_storage_centrifuge([[3500, 2900, 3400, 2950, 3300]]) == "STABLE"
