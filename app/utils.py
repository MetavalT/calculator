from app.unit_conversions import UNIT_CONVERSIONS


def convert_to_expected(

    value,

    variable_type,

    current_unit,

    expected_unit

):

    try:

        if value == '' or value is None:

            raise ValueError(
                "Please enter all values"
            )

        value = float(value)

        # CLEAN UNITS
        current_unit = str(current_unit).strip().lower()

        expected_unit = str(expected_unit).strip().lower()

        variable_type = str(variable_type).strip().lower()

        # NO UNIT CASE
        if current_unit in ['', 'none', 'null']:

            return value

        # SAME UNIT
        if current_unit == expected_unit:

            return value

        # UNIT EXIST CHECK
        if current_unit not in UNIT_CONVERSIONS:

            raise Exception(
                f"Unit not found: {current_unit}"
            )

        if expected_unit not in UNIT_CONVERSIONS:

            raise Exception(
                f"Unit not found: {expected_unit}"
            )

        # CURRENT → BASE
        base_value = (
            value *
            UNIT_CONVERSIONS[current_unit]
        )

        # BASE → EXPECTED
        converted_value = (
            base_value /
            UNIT_CONVERSIONS[expected_unit]
        )

        return converted_value

    except Exception as e:

        print("Conversion Error:", e)

        return float(value)