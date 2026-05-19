UNIT_CONVERSIONS = {

    'flow_rate': {
        'GPM': 1,
        'LPM': 0.264172,
        'm3/hr': 4.40287
    },

    'pressure': {
        'psi': 1,
        'bar': 14.5038,
        'kPa': 0.145038
    },

    'speed': {
        'km/hr': 1,
        'm/s': 3.6
    },

    'time': {
        'hr': 1,
        'min': 0.0166667,
        'sec': 0.000277778
    },
    'area': {
        'm2': 1
    }
}




def convert_to_expected(
    value,
    variable_type,
    selected_unit,
    expected_unit
):

    variable_type = variable_type.strip().lower()

    unit_map = UNIT_CONVERSIONS.get(variable_type, {})

    if selected_unit not in unit_map:

        raise ValueError(
            f"Unit '{selected_unit}' not found for type '{variable_type}'"
        )

    if expected_unit not in unit_map:

        raise ValueError(
            f"Expected unit '{expected_unit}' not found"
        )

    if selected_unit == expected_unit:
        return float(value)

    base_value = float(value) * unit_map[selected_unit]

    return base_value / unit_map[expected_unit]