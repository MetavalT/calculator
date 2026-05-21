# This file contains the unit conversion factors for various units.
# Each unit is defined in terms of a base SI unit for its category (e.g., meter for distance, second for time).
# 😎🙄🤐

UNIT_CONVERSIONS = {

    # =========================
    # DISTANCE
    # Base Unit = meter
    # =========================

    'm': 1,
    'km': 1000,
    'cm': 0.01,
    'mm': 0.001,

    # =========================
    # TIME
    # Base Unit = second
    # =========================

    'sec': 1,
    'min': 60,
    'hr': 3600,

    # =========================
    # SPEED
    # Base Unit = m/sec
    # =========================

    'm/sec': 1,
    'km/hr': 0.277778,

    # =========================
    # PRESSURE
    # Base Unit = Pascal
    # =========================

    'pa': 1,
    'kpa': 1000,
    'bar': 100000,
    'psi': 6894.76,

    # =========================
    # FLOW RATE
    # Base Unit = m3/sec
    # =========================

    'm3/sec': 1,
    'm3/hr': 0.000277778,
    'gpm': 0.0000630902,

  # =========================
    # jyada kuch nahi hai bas none case ke liye h nhi to error dega 😁
    # =========================

    'none': {
    'none': 1
}
}