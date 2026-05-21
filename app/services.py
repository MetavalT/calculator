from app.utils import convert_to_expected
import math


def evaluate_formula(

    expression,

    variables,

    variable_config

):

    processed_values = {}

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

    final_expression = expression

    # ^ ko python power me convert karo
    final_expression = final_expression.replace("^", "**")

    # sqrt support
    final_expression = final_expression.replace(
        "sqrt",
        "math.sqrt"
    )

    for variable, value in processed_values.items():

        final_expression = final_expression.replace(
            variable,
            str(value)
        )

    result = eval(final_expression)

    if result == int(result):
        result = int(result)
    else:
        result = round(result, 4)

    return result