from app.utils import convert_to_expected
from asteval import Interpreter
import math


def evaluate_formula(
    expression,
    variables,
    variable_config
):

    processed_values = {}

    for variable_name, value_data in variables.items():

        value = value_data['value']


        processed_values[variable_name] = float(value)

    final_expression = expression

    for variable, value in processed_values.items():

        final_expression = final_expression.replace(
            variable,
            str(value)
        )

    # SAFE FORMULA EVALUATION
    aeval = Interpreter(

        usersyms={
            "sqrt": math.sqrt
        }
    )

    result = aeval(final_expression)

    # ERROR CHECK
    if aeval.error:

        raise Exception(
            "Invalid Formula Expression"
        )

    # ROUNDING
    if result == int(result):

        result = int(result)

    else:

        result = round(result, 4)

    return {

        "value": result,

        "unit": ""
    }