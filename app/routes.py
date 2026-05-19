from flask import Blueprint, render_template, request, jsonify, send_file
from app.models import Formula, FormulaVariable, Calculation
from app import db
from app.services import evaluate_formula
import pandas as pd
from flask import redirect
from flask import flash, redirect, url_for
import json
import os

main = Blueprint('main', __name__)


# HOME PAGE
@main.route('/')
def home():

    formulas = Formula.query.all()

    calculations = Calculation.query.order_by(
        Calculation.id.desc()
    ).limit(10)

    return render_template(
        'home.html',
        formulas=formulas,
        calculations=calculations
    )


# HISTORY PAGE
@main.route('/history')
def history():

    calculations = Calculation.query.order_by(
        Calculation.id.desc()
    ).all()

    return render_template(
        'history.html',
        calculations=calculations
    )


# EXPORT EXCEL
@main.route('/export-excel')
def export_excel():

    calculations = Calculation.query.all()

    data = []

    for calc in calculations:

        data.append({
            'Formula': calc.formula_name,
            'Values Used': calc.values_used,
            'Answer': calc.answer,
            'Created At': calc.created_at
        })

    df = pd.DataFrame(data)

    export_folder = 'exports'

    os.makedirs(export_folder, exist_ok=True)

    file_path = os.path.join(
        export_folder,
        'calculations.xlsx'
    )

    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

# CREATE FORMULA
@main.route('/create-formula', methods=['GET', 'POST'])
def create_formula():

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        expression = request.form['expression']

        formula = Formula(
            name=name,
            description=description,
            expression=expression
        )

        db.session.add(formula)
        db.session.commit()

        variables = request.form.getlist('variable_name[]')
        labels = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        available_units = request.form.getlist('available_units[]')
        variable_types = request.form.getlist('variable_type[]')

        for i in range(len(variables)):

            variable = FormulaVariable(
                formula_id=formula.id,
                variable_name=variables[i],
                display_name=labels[i],
                expected_unit=expected_units[i],
                available_units=available_units[i] + '|' + variable_types[i]
            )

            db.session.add(variable)

        db.session.commit()

        return "Formula Created Successfully"

    return render_template('create_formula.html')


# CALCULATE PAGE
@main.route('/calculate/<int:formula_id>')
def calculate_page(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    return render_template(
        'calculate.html',
        formula=formula,
        variables=variables
    )


# API CALCULATE
@main.route('/api/calculate', methods=['POST'])
def calculate_api():

    data = request.json

    formula_id = data['formula_id']

    formula = Formula.query.get(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    variable_config = {}

    for var in variables:

        variable_type = var.available_units.split('|')[1].strip().lower()

        variable_config[var.variable_name] = {
            'expected_unit': var.expected_unit,
            'variable_type': variable_type
        }

    answer = evaluate_formula(
        formula.expression,
        data['values'],
        variable_config
    )

    calculation = Calculation(
        formula_name=formula.name,
        values_used=json.dumps(data['values']),
        answer=str(answer)
    )

    db.session.add(calculation)
    db.session.commit()

    return jsonify({
        'answer': answer
    })

    # VIEW FORMULA
@main.route('/formula/<int:formula_id>')
def view_formula(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    return render_template(
        'view_formula.html',
        formula=formula,
        variables=variables
    )


# EDIT FORMULA
@main.route('/edit-formula/<int:formula_id>', methods=['GET', 'POST'])
def edit_formula(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    if request.method == 'POST':

        formula.name = request.form['name']
        formula.description = request.form['description']
        formula.expression = request.form['expression']

        db.session.commit()

        return "Formula Updated Successfully"

    return render_template(
        'edit_formula.html',
        formula=formula,
        variables=variables
    )

    # DELETE FORMULA
@main.route('/delete-formula/<int:formula_id>')
def delete_formula(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    # pehle variables delete karo
    FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).delete()

    # formula delete
    db.session.delete(formula)

    db.session.commit()

    return redirect('/')