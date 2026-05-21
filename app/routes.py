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
from app.models import Calculation
from app import db

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

    # formula wise grouping
    for calc in calculations:

        if calc.formula_name not in formula_groups:

            formula_groups[calc.formula_name] = []

        formula_groups[calc.formula_name].append({

            'Values Used': calc.values_used,
            'Answer': calc.answer,
            'Created At': calc.created_at
        })

    # NEW FILE EVERY TIME
    with pd.ExcelWriter(
        file_path,
        engine='openpyxl'
    ) as writer:

        for formula_name, records in formula_groups.items():

            df = pd.DataFrame(records)

            safe_sheet_name = formula_name[:31]

            print(df)

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
def calculate():
    try:
        data = request.get_json()

        values = data.get('values', {})
        formula_id = data.get('formula_id')

        speed = values.get('speed', {})
        time = values.get('time', {})

        speed_value = float(speed.get('value') or 0)
        time_value = float(time.get('value') or 0)

        result = speed_value * time_value

        # 💾 SAVE TO DATABASE (IMPORTANT PART)
        calculation = Calculation(
            formula_name="Dynamic Formula",
            values_used=json.dumps(values),
            answer=result,
            created_at=datetime.now()
        )

        db.session.add(calculation)
        db.session.commit()

        return jsonify({
            "success": True,
            "answer": {
                "value": result,
                "unit": speed.get("unit", "")
            }
        })

    except Exception as e:
        print("SAVE ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
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

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    if request.method == 'POST':

# formula update
        formula.name = request.form['name']
        formula.description = request.form['description']
        formula.expression = request.form['expression']

        db.session.commit()

# old variables delete
        FormulaVariable.query.filter_by(
            formula_id=formula.id
        ).delete()

# new variables add
        variable_names = request.form.getlist('variable_name[]')
        display_names = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        available_units = request.form.getlist('available_units[]')
        variable_types = request.form.getlist('variable_type[]')

        for i in range(len(variable_names)):

# empty rows skip
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

    formula = Formula.query.get_or_404(formula_id)

# pehle variables delete karo
    FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).delete()

# formula delete
    db.session.delete(formula)

    db.session.commit()

    return redirect('/')