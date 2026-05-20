from app.utils import convert_to_expected


def evaluate_formula(

    expression,

    variables,

    variable_config

):

    processed_values = {}

    # =========================
    # UNIT CONVERSION
    # =========================

    for variable_name, value_data in variables.items():

        value = value_data['value']

        selected_unit = value_data['unit']

        config = variable_config[variable_name]

        expected_unit = config['expected_unit']

        variable_type = config['variable_type']

        converted_value = convert_to_expected(

            value,

            variable_type,

            selected_unit,

            expected_unit

        )

        processed_values[variable_name] = converted_value

    # =========================
    # REPLACE VARIABLES
    # =========================

    final_expression = expression

    for variable, value in processed_values.items():

        final_expression = final_expression.replace(
            variable,
            str(value)
        )

    # =========================
    # CALCULATE
    # =========================

    result = eval(final_expression)

    # =========================
    # ROUNDING
    # =========================

    if result == int(result):
        result = int(result)
    else:
        result = round(result, 4)

    return result