"""Lab 6 - Branch coverage tests for blood_donation_screening.py

Aditya Pradeep - PES2UG24AM900

Goal: make every decision (if / for / or) evaluate both True and False
(>= 90% branch coverage). This file is a standalone superset of the line
coverage suite: it adds the paths that line coverage alone never forces,
e.g. low hemoglobin in a NON high-altitude cohort (26 -> 15), empty loops,
each side of the `or` conditions, and the exact threshold values.
"""
import pytest

from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def _cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {"clinic_registered": registered, "type": ctype,
            "fast_track": fast_track, "donors": donors}


HEALTHY = {"age": 25, "weight_kg": 65, "hb": 14.0}
LOW_HB = {"age": 30, "weight_kg": 70, "hb": 11.0}
HIGH_HB = {"age": 40, "weight_kg": 80, "hb": 19.0}


# ============ Decision 1 (line 2): input validation  `A or B` ============

@pytest.mark.parametrize("cohorts, volume", [
    ("not-a-list", 450),    # A True  (not a list)
    ({"a": 1}, 450),        # A True  (dict)
    (None, 450),            # A True  (None)
    ([], 0),                # A False, B True  (volume == 0)
    ([], -100),             # A False, B True  (negative volume)
])
def test_invalid_input_raises(cohorts, volume):
    with pytest.raises(ValueError):
        process_donor_cohort(cohorts, volume)


def test_empty_cohort_list_is_zero_yield():
    """Outer for-loop never entered (8 -> 38), then ZERO_YIELD branch."""
    assert process_donor_cohort([], 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


# ============ Decision 2 (line 9): clinic registered? ============

def test_unregistered_cohort_is_skipped():
    assert process_donor_cohort([_cohort([HEALTHY], registered=False)], 450)["status"] == "ZERO_YIELD"


def test_missing_registration_flag_defaults_to_skip():
    assert process_donor_cohort([{"donors": [HEALTHY]}], 450)["collected_ml"] == 0


def test_mixed_registered_and_unregistered():
    cohorts = [_cohort([HEALTHY], registered=False), _cohort([HEALTHY])]
    assert process_donor_cohort(cohorts, 450) == {"collected_ml": 450, "status": "ACCEPTED"}


# ============ Inner for-loop (line 15): empty donor list ============

def test_registered_cohort_with_no_donors():
    """Inner loop body never runs (15 -> 35)."""
    assert process_donor_cohort([_cohort([])], 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_registered_cohort_without_donors_key_uses_default():
    cohort = {"clinic_registered": True, "fast_track": True}
    assert process_donor_cohort([cohort], 450) == {"collected_ml": 50, "status": "ACCEPTED"}


# ============ Decision 3 (line 20): `age < 17 or weight < 50` ============

@pytest.mark.parametrize("donor, collected", [
    ({"age": 16, "weight_kg": 70, "hb": 14.0}, 0),     # age True
    ({"age": 30, "weight_kg": 49, "hb": 14.0}, 0),     # age False, weight True
    ({"age": 17, "weight_kg": 50, "hb": 14.0}, 450),   # both False at exact threshold
    ({}, 0),                                           # all defaults (age 0) -> deferred
])
def test_age_weight_screening(donor, collected):
    assert process_donor_cohort([_cohort([donor])], 450)["collected_ml"] == collected


# ============ Decision 4/5 (lines 24, 26, 29): hemoglobin ============

def test_low_hb_in_standard_cohort_continues_loop():
    """hb < 12.5 but NOT high-altitude: 26 -> 15, loop continues to next donor."""
    donors = [LOW_HB, HEALTHY, HEALTHY]
    assert process_donor_cohort([_cohort(donors)], 450) == {"collected_ml": 900, "status": "ACCEPTED"}


def test_low_hb_in_high_altitude_cohort_resets_and_breaks():
    """hb < 12.5 AND high-altitude: total reset to 0 and remaining donors skipped."""
    donors = [HEALTHY, LOW_HB, HEALTHY]
    assert process_donor_cohort([_cohort(donors, ctype="high_altitude")], 450) == \
        {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_altitude_cohort_with_good_donors_collects():
    """High-altitude cohort where the low-Hb branch is never taken."""
    donors = [HEALTHY, HEALTHY]
    assert process_donor_cohort([_cohort(donors, ctype="high_altitude")], 450)["collected_ml"] == 900


def test_high_altitude_break_then_later_cohort_still_collects():
    """break only exits the inner loop; the next cohort is still processed."""
    cohorts = [_cohort([HEALTHY, LOW_HB], ctype="high_altitude"), _cohort([HEALTHY])]
    assert process_donor_cohort(cohorts, 450) == {"collected_ml": 450, "status": "ACCEPTED"}


def test_high_hb_is_deferred():
    assert process_donor_cohort([_cohort([HIGH_HB, HEALTHY])], 450)["collected_ml"] == 450


@pytest.mark.parametrize("hb, collected", [
    (12.5, 450),    # lower boundary is accepted (not < 12.5)
    (18.0, 450),    # upper boundary is accepted (not > 18.0)
    (12.49, 0),
    (18.01, 0),
])
def test_hemoglobin_boundaries(hb, collected):
    donor = {"age": 30, "weight_kg": 70, "hb": hb}
    assert process_donor_cohort([_cohort([donor])], 450)["collected_ml"] == collected


# ============ Decision 6 (line 35): fast track ============

@pytest.mark.parametrize("fast_track, expected", [(True, 500), (False, 450)])
def test_fast_track_bonus(fast_track, expected):
    assert process_donor_cohort([_cohort([HEALTHY], fast_track=fast_track)], 450)["collected_ml"] == expected


def test_fast_track_bonus_added_even_after_high_altitude_reset():
    cohort = _cohort([HEALTHY, LOW_HB], ctype="high_altitude", fast_track=True)
    assert process_donor_cohort([cohort], 450) == {"collected_ml": 50, "status": "ACCEPTED"}


# ============ Decisions 7/8 (lines 38, 40): final status ============

def test_exactly_four_deferrals_is_not_high_deferral():
    donors = [HIGH_HB] * 4 + [HEALTHY]
    assert process_donor_cohort([_cohort(donors)], 450) == {"collected_ml": 450, "status": "ACCEPTED"}


def test_five_deferrals_is_high_deferral():
    donors = [HIGH_HB] * 5 + [HEALTHY]
    assert process_donor_cohort([_cohort(donors)], 450) == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


def test_high_deferral_takes_priority_over_zero_yield():
    donors = [LOW_HB] * 5
    assert process_donor_cohort([_cohort(donors)], 450) == {"collected_ml": 0, "status": "HIGH_DEFERRAL"}


# ============ verify_storage_centrifuge ============

@pytest.mark.parametrize("runs", [[], None])
def test_centrifuge_no_data(runs):
    assert verify_storage_centrifuge(runs) == "NO_DATA"


def test_centrifuge_two_consecutive_drops_abort():
    assert verify_storage_centrifuge([[3500, 2900, 2800, 3600]]) == "ABORT_SPIN"


def test_centrifuge_single_drop_at_end_is_stable():
    """rpm < 3000 once, streak only 1 (54 False) and the loop ends."""
    assert verify_storage_centrifuge([[3500, 3400, 2999]]) == "STABLE"


def test_centrifuge_isolated_drops_reset_streak():
    assert verify_storage_centrifuge([[3500, 2900, 3400, 2950, 3300]]) == "STABLE"


def test_centrifuge_exact_threshold_is_not_a_drop():
    assert verify_storage_centrifuge([[3000, 3000, 3000]]) == "STABLE"


def test_centrifuge_streak_does_not_carry_across_runs():
    """Streak is reset per run: a drop at the end of run 1 + start of run 2 is fine."""
    assert verify_storage_centrifuge([[3500, 2900], [2900, 3500]]) == "STABLE"


def test_centrifuge_empty_run_then_bad_run():
    """Inner loop over an empty run (51 -> 49), later run aborts."""
    assert verify_storage_centrifuge([[], [2500, 2400]]) == "ABORT_SPIN"


def test_centrifuge_all_runs_stable():
    assert verify_storage_centrifuge([[3200, 3300], [3100, 3050]]) == "STABLE"
