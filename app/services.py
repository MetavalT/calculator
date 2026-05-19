from sympy import symbols, sympify
from app.utils import convert_to_expected


def evaluate_formula(expression, variables, variable_config):

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

    # IMPORTANT FIX
    # Q, S, N etc sympy reserved names hote hain
    # isliye custom symbols force kar rahe

    symbol_map = {}

    for key in processed_values.keys():
        symbol_map[key] = symbols(key)

    expr = sympify(
        expression,
        locals=symbol_map
    )

    result = expr.evalf(subs=processed_values)

    return round(float(result), 4)