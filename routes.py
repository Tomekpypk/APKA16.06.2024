import datetime
from flask import render_template, request, jsonify, redirect, url_for, flash, abort, session, current_app as app
from blog import app, db
from .models import User, TrainingProgress, BodyMeasurements, CaloricDemand, ExerciseRecord
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user



# Inicjalizacja poprzednich wartości
previous_values = {
    'bialko': 0,
    'tluszcz': 0,
    'weglowodany': 0,
    'old_PR_bench_press': 0,
    'new_PR_bench_press': 0,
    'old_PR_deadlift': 0,
    'new_PR_deadlift': 0,
    'old_PR_row': 0,
    'new_PR_row': 0,
    'old_PR_squat': 0,
    'new_PR_squat': 0
}

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    global previous_values

    if request.method == 'POST':
        try:
            # Pobierz dane od użytkownika dotyczące zapotrzebowania kalorycznego
            bialko = float(request.form.get('bialko', previous_values['bialko']))
            tluszcz = float(request.form.get('tluszcz', previous_values['tluszcz']))
            weglowodany = float(request.form.get('weglowodany', previous_values['weglowodany']))

            # Oblicz wartość kaloryczną
            kcal_bialko = bialko * 4
            kcal_tluszcz = tluszcz * 9
            kcal_weglowodany = weglowodany * 4

            # Oblicz różnicę w kaloriach i dodaj do zapotrzebowania kalorycznego, jeśli wartości się zmieniły
            diff_bialko = (bialko - previous_values['bialko']) * 4
            diff_tluszcz = (tluszcz - previous_values['tluszcz']) * 9
            diff_weglowodany = (weglowodany - previous_values['weglowodany']) * 4

            # Aktualizuj poprzednie wartości
            previous_values['bialko'] = bialko
            previous_values['tluszcz'] = tluszcz
            previous_values['weglowodany'] = weglowodany

            # Oblicz zapotrzebowanie kaloryczne
            zapotrzebowanie_kaloryczne = (kcal_bialko + kcal_tluszcz + kcal_weglowodany +
                                           diff_bialko + diff_tluszcz + diff_weglowodany)

            # Pobierz dane od użytkownika dotyczące postępów w treningu
            old_PR_bench_press = float(request.form.get("old_PR_bench_press", previous_values['old_PR_bench_press']))
            new_PR_bench_press = float(request.form.get("new_PR_bench_press", previous_values['new_PR_bench_press']))

            old_PR_deadlift = float(request.form.get("old_PR_deadlift", previous_values['old_PR_deadlift']))
            new_PR_deadlift = float(request.form.get("new_PR_deadlift", previous_values['new_PR_deadlift']))

            old_PR_row = float(request.form.get("old_PR_row", previous_values['old_PR_row']))
            new_PR_row = float(request.form.get("new_PR_row", previous_values['new_PR_row']))

            old_PR_squat = float(request.form.get("old_PR_squat", previous_values['old_PR_squat']))
            new_PR_squat = float(request.form.get("new_PR_squat", previous_values['new_PR_squat']))

            # Oblicz procentowy przyrost dla każdego ćwiczenia
            percent_increase_bench_press = calculate_percent_increase(old_PR_bench_press, new_PR_bench_press)
            percent_increase_deadlift = calculate_percent_increase(old_PR_deadlift, new_PR_deadlift)
            percent_increase_row = calculate_percent_increase(old_PR_row, new_PR_row)
            percent_increase_squat = calculate_percent_increase(old_PR_squat, new_PR_squat)

            # Aktualizuj poprzednie wartości dla treningu
            previous_values['old_PR_bench_press'] = old_PR_bench_press
            previous_values['new_PR_bench_press'] = new_PR_bench_press
            previous_values['old_PR_deadlift'] = old_PR_deadlift
            previous_values['new_PR_deadlift'] = new_PR_deadlift
            previous_values['old_PR_row'] = old_PR_row
            previous_values['new_PR_row'] = new_PR_row        
            previous_values['old_PR_squat'] = old_PR_squat
            previous_values['new_PR_squat'] = new_PR_squat

            # Zwróć dane jako odpowiedź w formacie JSON
            return jsonify(
                zapotrzebowanie_kaloryczne=zapotrzebowanie_kaloryczne,
                percent_increase_bench_press=percent_increase_bench_press, 
                percent_increase_deadlift=percent_increase_deadlift,
                percent_increase_row=percent_increase_row,
                percent_increase_squat=percent_increase_squat
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # Jeśli metoda to GET, zwróć stronę z formularzem
    return render_template("index.html")

def calculate_percent_increase(old_value, new_value):
    if old_value != 0:
        return ((new_value - old_value) / old_value) * 100
    else:
        return 0

@app.route('/update_record', methods=['POST'])
@login_required
def update_record():
    data = request.json
    exercise_id = data['exerciseId']
    new_record = data['newRecord']
    exercise_name = data['exerciseName']

    # Tworzenie lub aktualizacja rekordu ćwiczenia w bazie danych
    record = TrainingProgress.query.filter_by(id=exercise_id).first()
    if not record:
        record = TrainingProgress(id=exercise_id, new_PR_bench_press=new_record)  # przykład dla jednego ćwiczenia
        db.session.add(record)
    else:
        record.new_PR_bench_press = new_record  # aktualizacja istniejącego rekordu

    db.session.commit()

    return jsonify({"status": "success", "message": "Record updated successfully"})



@app.route('/update_dimension', methods=['POST'])
@login_required
def update_dimension():
    try:
        data = request.json
        measurement_type = data['dimensionType']
        measurement_value = float(data['dimensionValue'])
        
        user_id = 1  # Na przykład zalogowany użytkownik
        measurement = BodyMeasurements.query.filter_by(user_id=user_id).order_by(BodyMeasurements.measurement_date.desc()).first()
        
        if not measurement or measurement.measurement_date.date() != datetime.date.today():
            measurement = BodyMeasurements(user_id=user_id)
            db.session.add(measurement)
        
        if measurement_type == "barki":
            measurement.shoulders = measurement_value
        elif measurement_type == "klatka":
            measurement.chest = measurement_value
        elif measurement_type == "pas":
            measurement.waist = measurement_value
        elif measurement_type == "biceps":
            measurement.biceps = measurement_value
        elif measurement_type == "biodra":
            measurement.hips = measurement_value
        elif measurement_type == "uda":
            measurement.thighs = measurement_value
        elif measurement_type == "łydki":
            measurement.calves = measurement_value
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"{measurement_type} updated successfully"})
    
    except KeyError as e:
        abort(400, description=f"Missing key {e} in the received data")
    except Exception as e:
        abort(500, description=f"An error occurred: {e}")



@app.route('/get_initial_data', methods=['GET'])
@login_required
def get_initial_data():
    user_id = 1
    measurements = BodyMeasurements.query.filter_by(user_id=user_id).order_by(BodyMeasurements.measurement_date.desc()).first()
    training_progress = TrainingProgress.query.filter_by(user_id=user_id).all()

    measurements_data = {
        "shoulders": measurements.shoulders if measurements else 0,
        "chest": measurements.chest if measurements else 0,
        "waist": measurements.waist if measurements else 0,
        "biceps": measurements.biceps if measurements else 0,
        "hips": measurements.hips if measurements else 0,
        "thighs": measurements.thighs if measurements else 0,
        "calves": measurements.calves if measurements else 0
    }

    training_data = [{
        "exercise_name": progress.exercise_name,
        "old_record": progress.old_PR_bench_press if hasattr(progress, 'old_PR_bench_press') else 0,
        "new_record": progress.new_PR_bench_press if hasattr(progress, 'new_PR_bench_press') else 0,
        "old_deadlift": progress.old_PR_deadlift if hasattr(progress, 'old_PR_deadlift') else 0,
        "new_deadlift": progress.new_PR_deadlift if hasattr(progress, 'new_PR_deadlift') else 0,
        "old_row": progress.old_PR_row if hasattr(progress, 'old_PR_row') else 0,
        "new_row": progress.new_PR_row if hasattr(progress, 'new_PR_row') else 0,
        "old_squat": progress.old_PR_squat if hasattr(progress, 'old_PR_squat') else 0,
        "new_squat": progress.new_PR_squat if hasattr(progress, 'new_PR_squat') else 0,
    } for progress in training_progress]

    return jsonify({
        "measurements": measurements_data,
        "training": training_data
    })



"""@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['exampleFirstName']
        last_name = request.form['exampleLastName']
        email = request.form['exampleInputEmail']
        password = request.form['exampleInputPassword']
        repeat_password = request.form['exampleRepeatPassword']

        if password != repeat_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')"""

ADMIN_EMAIL = "propsek@gmail.com"
ADMIN_PASSWORD = "tomek1"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['exampleInputEmail']
        password = request.form['exampleInputPassword']
        remember = 'customCheck' in request.form

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user_id'] = 1  # Załóżmy, że admin ma ID 1
            session['username'] = 'Admin'  # Nazwa dla admina
            flash('Welcome back, Admin!', 'success')
            return render_template('index.html', username='Admin')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username  # Zapisz nazwę użytkownika w sesji
            flash('Welcome back!', 'success')
            return render_template('index.html', username=user.username)
        else:
            flash('Invalid email or password!', 'danger')
    return render_template('login.html')


#new_user = User(username='TOMEKPK', email='propsek@gmail.com', password_hash=generate_password_hash('ghfew33nen4iR%'))

@app.route('/logout')
def logout():
    session.clear()  # Usuwa wszystkie dane z sesji
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['exampleFirstName']
        last_name = request.form['exampleLastName']
        email = request.form['exampleInputEmail']
        password = request.form['exampleInputPassword']
        repeat_password = request.form['exampleRepeatPassword']

        if password == repeat_password:
            hashed_password = generate_password_hash(password)
            new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match!', 'danger')
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['exampleInputEmail']
        user = User.query.filter_by(email=email).first()
        if user:
            # Tutaj umieścić logikę do wysyłania email z linkiem resetującym hasło
            flash('Please check your email for a password reset link.', 'info')
        else:
            flash('Email not found!', 'danger')
    return render_template('forgot-password.html')



"""from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db  # Importuj swój model User
from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
"""

@app.route('/buttons')
def buttons():
    return render_template('buttons.html')

@app.route('/cards')
def cards():
    return render_template('cards.html')

if __name__ == '__main__':
    app.run(debug=True)