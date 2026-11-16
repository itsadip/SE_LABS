"""Blood donation input processing - hardened after fuzz testing (Lab 7).

Every function validates its input and returns a descriptive
"Invalid ..." message instead of raising on bad data.
"""
import math
import re

VALID_ANTIGENS = {"A", "B", "AB", "O"}
RH_MAP = {"+": "Positive", "-": "Negative"}

SYSTOLIC_RANGE = (50, 300)     # mmHg
DIASTOLIC_RANGE = (20, 200)    # mmHg
WEIGHT_RANGE_KG = (0.0, 300.0)  # exclusive lower bound
HB_RANGE = (0.0, 25.0)          # g/dL, exclusive lower bound
DONOR_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,32}")


def validate_blood_type(blood_code):
    """
    Standardizes blood group and Rh factor (e.g. 'O+', 'AB-').
    Returns e.g. 'AB Negative', or an 'Invalid blood type: ...' message.
    """
    if not isinstance(blood_code, str):
        return "Invalid blood type: input must be text"
    cleaned = blood_code.strip().upper()
    if len(cleaned) < 2:
        return "Invalid blood type: expected an ABO group followed by + or -"
    antigen = cleaned[:-1].strip()
    rh_char = cleaned[-1]
    if rh_char not in RH_MAP:
        return "Invalid blood type: Rh factor must be '+' or '-'"
    if antigen not in VALID_ANTIGENS:
        return "Invalid blood type: ABO group must be A, B, AB or O"
    return f"{antigen} {RH_MAP[rh_char]}"


def _parse_mmhg(text):
    """Return a positive whole number from ASCII digits, or None."""
    text = text.strip()
    if not text or len(text) > 3 or not (text.isascii() and text.isdigit()):
        return None
    return int(text)


def calculate_pulse_pressure(bp_string):
    """
    Calculates pulse pressure (systolic - diastolic) and arterial ratio.
    Expects 'systolic/diastolic' (e.g. '120/80').
    """
    if not isinstance(bp_string, str):
        return "Invalid BP: input must be text"
    parts = bp_string.split('/')
    if len(parts) != 2:
        return "Invalid BP: expected format 'systolic/diastolic' (e.g. 120/80)"
    systolic = _parse_mmhg(parts[0])
    diastolic = _parse_mmhg(parts[1])
    if systolic is None or diastolic is None:
        return "Invalid BP: values must be whole numbers in mmHg"
    if not SYSTOLIC_RANGE[0] <= systolic <= SYSTOLIC_RANGE[1]:
        return f"Invalid BP: systolic must be {SYSTOLIC_RANGE[0]}-{SYSTOLIC_RANGE[1]} mmHg"
    if not DIASTOLIC_RANGE[0] <= diastolic <= DIASTOLIC_RANGE[1]:
        return f"Invalid BP: diastolic must be {DIASTOLIC_RANGE[0]}-{DIASTOLIC_RANGE[1]} mmHg"
    if systolic <= diastolic:
        return "Invalid BP: systolic must be greater than diastolic"
    pulse_diff = systolic - diastolic
    ratio = round(systolic / diastolic, 2)
    return f"Diff: {pulse_diff}, Ratio: {ratio}"


def _parse_measure(text, low, high):
    """Return a finite float with low < value <= high, or None."""
    try:
        value = float(text)
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(value) or not low < value <= high:
        return None
    return value


def parse_donor_registry(donor_entry):
    """
    Parses pipe-delimited record: 'DonorID|WeightKg|Hemoglobin'.
    Returns 'Donor <id>: Eligible/Deferred' or an 'Invalid record: ...' message.
    """
    if not isinstance(donor_entry, str):
        return "Invalid record: input must be text"
    fields = donor_entry.split('|')
    if len(fields) != 3:
        return "Invalid record: expected 'DonorID|WeightKg|Hemoglobin'"
    donor_id = fields[0].strip()
    if not DONOR_ID_PATTERN.fullmatch(donor_id):
        return "Invalid record: donor ID must be 1-32 letters, digits, '-' or '_'"
    weight = _parse_measure(fields[1], *WEIGHT_RANGE_KG)
    if weight is None:
        return f"Invalid record: weight must be a number in ({WEIGHT_RANGE_KG[0]:g}, {WEIGHT_RANGE_KG[1]:g}] kg"
    hemoglobin = _parse_measure(fields[2], *HB_RANGE)
    if hemoglobin is None:
        return f"Invalid record: hemoglobin must be a number in ({HB_RANGE[0]:g}, {HB_RANGE[1]:g}] g/dL"
    eligible = weight >= 50.0 and hemoglobin >= 12.5
    return f"Donor {donor_id}: {'Eligible' if eligible else 'Deferred'}"


def main():
    try:
        print("==== Running validate_blood_type ====")
        b_input = input("Enter blood type (e.g. A+, O-, AB+): ")
        print("Validated:", validate_blood_type(b_input))

        print("\n==== Running calculate_pulse_pressure ====")
        bp_input = input("Enter BP (e.g. 120/80): ")
        print("BP Metrics:", calculate_pulse_pressure(bp_input))

        print("\n==== Running parse_donor_registry ====")
        d_input = input("Enter record (ID|Weight|Hemoglobin): ")
        print("Status:", parse_donor_registry(d_input))
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended - exiting.")


if __name__ == "__main__":
    main()
