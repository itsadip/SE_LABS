"""Lab 7 - Property-based fuzz tests for processor.py using Hypothesis.

Aditya Pradeep - PES2UG24AM900

Part 1 (the three starter tests) fuzz each function with arbitrary text or
None and assert that it never raises - invalid input must be handled
gracefully and a string returned.

Part 2 adds targeted strategies (strings that *almost* look valid, e.g.
'120/0', 'O', 'D1|nan|13') and correctness properties, so the fuzzer can
also detect wrong answers, not just crashes.
"""
import math

from hypothesis import given, settings, strategies as st
from processor import validate_blood_type, calculate_pulse_pressure, parse_donor_registry

ANTIGENS = ["A", "B", "AB", "O"]
RH = {"+": "Positive", "-": "Negative"}


def _no_crash(func, value):
    """Call func(value); fail the test with a clear message if it raises."""
    try:
        result = func(value)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"{func.__name__} crashed on {value!r} with {type(e).__name__}: {e}"
    assert isinstance(result, str), f"{func.__name__} returned {result!r}, expected str"
    return result


# =====================================================================
# Part 1 - the three starter fuzz tests (completed with try/except)
# =====================================================================

@given(st.text() | st.none())
def test_validate_blood_type_no_crash(s):
    try:
        result = validate_blood_type(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"validate_blood_type crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


@given(st.text() | st.none())
def test_calculate_pulse_pressure_safe(s):
    try:
        result = calculate_pulse_pressure(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"calculate_pulse_pressure crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


@given(st.text() | st.none())
def test_parse_donor_registry_safe(s):
    try:
        result = parse_donor_registry(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_donor_registry crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


# =====================================================================
# Part 2 - targeted fuzzing: inputs that are close to the expected format
# =====================================================================

# --- validate_blood_type -------------------------------------------------

blood_like = st.builds(
    lambda a, r, pad1, pad2: f"{pad1}{a}{r}{pad2}",
    st.text(alphabet="ABOabo XZ", max_size=3),
    st.sampled_from(["+", "-", "", "*", "±"]),
    st.sampled_from(["", " ", "\t"]),
    st.sampled_from(["", " ", "\n"]),
)


@given(blood_like)
def test_validate_blood_type_near_valid_no_crash(s):
    _no_crash(validate_blood_type, s)


@given(st.sampled_from(ANTIGENS), st.sampled_from(list(RH)), st.booleans(),
       st.sampled_from(["", " ", "  "]))
def test_validate_blood_type_valid_codes(antigen, sign, lower, pad):
    """Every real ABO/Rh code (any case, padded) is standardised correctly."""
    code = antigen.lower() if lower else antigen
    assert validate_blood_type(f"{pad}{code}{sign}{pad}") == f"{antigen} {RH[sign]}"


@given(st.text(max_size=6))
def test_validate_blood_type_only_real_groups_accepted(s):
    """Output is either one of the 8 real blood groups or an 'Invalid' message."""
    result = _no_crash(validate_blood_type, s)
    valid_outputs = {f"{a} {v}" for a in ANTIGENS for v in RH.values()}
    assert result in valid_outputs or result.startswith("Invalid"), \
        f"{s!r} produced bogus blood group {result!r}"


# --- calculate_pulse_pressure ---------------------------------------------

bp_like = st.builds(
    lambda a, sep, b: f"{a}{sep}{b}",
    st.one_of(st.integers(-500, 500).map(str), st.text(max_size=4)),
    st.sampled_from(["/", "//", " / ", "\\", ""]),
    st.one_of(st.integers(-500, 500).map(str), st.just("0"), st.text(max_size=4)),
)


@given(bp_like)
def test_calculate_pulse_pressure_near_valid_no_crash(s):
    _no_crash(calculate_pulse_pressure, s)


@given(st.integers(70, 250).flatmap(
    lambda sys_: st.tuples(st.just(sys_), st.integers(40, min(sys_ - 1, 200)))))
def test_calculate_pulse_pressure_valid_values(pair):
    """For physiologically valid readings the maths is right."""
    systolic, diastolic = pair
    result = calculate_pulse_pressure(f"{systolic}/{diastolic}")
    assert result == f"Diff: {systolic - diastolic}, Ratio: {round(systolic / diastolic, 2)}"


@given(st.integers(-1000, 1000), st.integers(-1000, 1000))
def test_calculate_pulse_pressure_rejects_impossible_readings(systolic, diastolic):
    """Zero/negative values or systolic <= diastolic must not produce metrics."""
    result = _no_crash(calculate_pulse_pressure, f"{systolic}/{diastolic}")
    if systolic <= 0 or diastolic <= 0 or systolic <= diastolic:
        assert result.startswith("Invalid"), f"{systolic}/{diastolic} gave {result!r}"


# --- parse_donor_registry -------------------------------------------------

number_text = st.one_of(
    st.floats(allow_nan=True, allow_infinity=True).map(str),
    st.integers(-1000, 1000).map(str),
    st.sampled_from(["", " ", "abc", "nan", "inf", "-inf", "1e309", "65kg"]),
)
record_like = st.lists(st.one_of(st.text(max_size=5), number_text), min_size=0, max_size=5).map("|".join)


@given(record_like)
def test_parse_donor_registry_near_valid_no_crash(s):
    _no_crash(parse_donor_registry, s)


@given(st.from_regex(r"[A-Z][0-9]{1,4}", fullmatch=True),
       st.floats(30, 200, allow_nan=False), st.floats(5, 22, allow_nan=False))
def test_parse_donor_registry_valid_records(donor_id, weight, hb):
    """Valid records give the correct eligibility decision."""
    result = parse_donor_registry(f"{donor_id}|{weight}|{hb}")
    expected = "Eligible" if weight >= 50.0 and hb >= 12.5 else "Deferred"
    assert result == f"Donor {donor_id}: {expected}"


@settings(max_examples=200)
@given(record_like)
def test_parse_donor_registry_never_judges_non_finite_values(s):
    """NaN/inf weights or hemoglobin must be rejected, never Eligible/Deferred."""
    result = _no_crash(parse_donor_registry, s)
    fields = s.split("|")
    if len(fields) == 3:
        for raw in fields[1:]:
            try:
                value = float(raw)
            except ValueError:
                continue
            if not math.isfinite(value):
                assert result.startswith("Invalid"), f"{s!r} gave {result!r}"
