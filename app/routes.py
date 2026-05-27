from flask import Blueprint, render_template, request, jsonify, send_file
from app.models import Formula, FormulaVariable, Calculation
from app import db
from app.services import evaluate_formula
import pandas as pd
from flask import redirect
from flask import request, jsonify
from flask import flash, redirect, url_for
from datetime import datetime
import json
import os
import logging
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)


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

    print("TOTAL CALCULATIONS:", len(calculations))

    export_folder = 'exports'

    os.makedirs(export_folder, exist_ok=True)

    file_path = os.path.join(
        export_folder,
        'calculations.xlsx'
    )

    formula_groups = {}

    for calc in calculations:

        if calc.formula_name not in formula_groups:

            formula_groups[calc.formula_name] = []

        formula_groups[calc.formula_name].append({

            'Values Used': calc.values_used,
            'Answer': calc.answer,
            'Created At': calc.created_at
        })

    with pd.ExcelWriter(
        file_path,
        engine='openpyxl'
    ) as writer:

        for formula_name, records in formula_groups.items():

            df = pd.DataFrame(records)

            safe_sheet_name = formula_name[:31]

            df.to_excel(
                writer,
                sheet_name=safe_sheet_name,
                index=False
            )

    print("EXCEL GENERATED")

    return send_file(
        os.path.abspath(file_path),
        as_attachment=True,
        download_name='calculations.xlsx'
    )


# CREATE FORMULA
@main.route('/create-formula', methods=['GET', 'POST'])
def create_formula():
    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        expression = request.form['expression']

        formula = Formula(
            name=name,
            description=description,
            expression=expression,
        )

        db.session.add(formula)
        db.session.commit()

        variables = request.form.getlist('variable_name[]')
        labels = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        available_units = request.form.getlist('available_units[]')
        variable_types = request.form.getlist('variable_type[]')

        for i in range(len(variables)):

            if variables[i].strip() == '':
                continue

            variable = FormulaVariable(
                formula_id=formula.id,
                variable_name=variables[i],
                display_name=labels[i],
                expected_unit=expected_units[i],
                available_units=available_units[i] + '|' + variable_types[i]
            )

            db.session.add(variable)

        db.session.commit()

        return redirect(url_for('main.home'))

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

    try:

        data = request.json

        formula_id = data.get('formula_id')

        selected_formula = Formula.query.get(formula_id)

        if not selected_formula:

            return jsonify({
                'success': False,
                'error': 'Formula not found'
            }), 404

        variables = FormulaVariable.query.filter_by(
            formula_id=formula_id
        ).all()

        variable_config = {}

        for var in variables:

            parts = var.available_units.split('|')

            variable_type = "none"

            if len(parts) > 1:
                variable_type = parts[-1].strip().lower()

            variable_config[var.variable_name] = {

                'expected_unit': var.expected_unit,
                'variable_type': variable_type
            }

        answer = evaluate_formula(

            selected_formula.expression,
            data['values'],
            variable_config
        )

        calculation = Calculation(

            formula_name=selected_formula.name,

            values_used=json.dumps(data['values']),

            answer=str(answer['value']),

            created_at=datetime.utcnow()
        )

        db.session.add(calculation)
        db.session.commit()

        return jsonify({

            'success': True,
            'answer': answer
        })

    except Exception as e:

        logging.error(str(e))

        print("SAVE ERROR:", e)

        return jsonify({

            'success': False,
            'error': str(e)

        }), 400


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
    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    if request.method == 'POST':

        formula.name = request.form['name']
        formula.description = request.form['description']
        formula.expression = request.form['expression']

        db.session.commit()

        FormulaVariable.query.filter_by(
            formula_id=formula.id
        ).delete()

        variable_names = request.form.getlist('variable_name[]')
        display_names = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        available_units = request.form.getlist('available_units[]')
        variable_types = request.form.getlist('variable_type[]')

        for i in range(len(variable_names)):

            if variable_names[i].strip() == '':
                continue

            variable = FormulaVariable(
                formula_id=formula.id,
                variable_name=variable_names[i],
                display_name=display_names[i],
                expected_unit=expected_units[i],
                available_units=available_units[i] + '|' + variable_types[i]
            )

            db.session.add(variable)

        db.session.commit()

        return redirect('/')

    return render_template(
        'edit_formula.html',
        formula=formula,
        variables=variables
    )


# DELETE FORMULA
@main.route('/delete-formula/<int:formula_id>')
def delete_formula(formula_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    formula = Formula.query.get_or_404(formula_id)

    FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).delete()

    db.session.delete(formula)

    db.session.commit()

    return redirect('/')

# LOGIN PAGE
@main.route('/login', methods=['GET', 'POST'])
def login():

    from app.models import User

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect('/')

        return "Invalid Username or Password"

    return render_template('login.html')

# LOGOUT
@main.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/')