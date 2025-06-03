from flask import Flask, render_template, request, redirect, flash, jsonify, url_for, session
from sqlite3 import connect, Row
import sqlite3
import base64
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/images/youths_name"
app.config['SECRET_KEY'] = "secretkey!@#$##$%%$"

DATABASE = "youths.db"

# ---------- Database Helper Functions ----------

def postprocess(sql: str, params: tuple = ()) -> bool:
    with connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute(sql, params)
        db.commit()
        return cursor.rowcount > 0

def getprocess(sql: str, params: tuple = ()) -> list:
    with connect(DATABASE) as db:
        db.row_factory = Row
        cursor = db.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

# ---------- Youths_name CRUD Functions ----------

def get_youths():
    return getprocess("SELECT * FROM youths_name")

def get_youth(idno):
    result = getprocess("SELECT * FROM youths_name WHERE idno = ?", (idno,))
    if not result:
        return None
    youth = dict(result[0])
    # Provide default image filename if missing or None
    if not youth.get('image'):
        youth['image'] = 'default.jpg'  # Make sure you have this image in your static folder
    return youth

def delete_youth(idno):
    return postprocess("DELETE FROM youths_name WHERE idno = ?", (idno,))

# ---------- Admin Functions ----------

def get_admin():
    return getprocess("SELECT * FROM admin")

# ---------- Routes ----------

@app.route("/")
def checker():
    youths = []
    return render_template("attendancechecker.html", pagetitle="Youth Information System", youths=youths)

@app.route("/mainpage")
def mainpage():
    youths = get_youths()
    return render_template("index.html", pagetitle="Youth Registration", youths=youths)

@app.route("/admin")
def admin():
    return render_template("login.html", pagetitle="Login")

@app.route("/login", methods=['POST'])
def login():
    try:
        admin_id = int(request.form['admin_id'])
        if getprocess("SELECT * FROM admin WHERE idno = ?", (admin_id,)):
            session['logged_in'] = True
            flash("Login successful.")
            return redirect(url_for("mainpage"))
        else:
            flash("Invalid admin ID.")
            return redirect(url_for("admin"))
    except Exception as e:
        flash(f"Login error: {e}")
        return redirect(url_for("admin"))

@app.route("/saveinformation", methods=['POST'])
def saveinformation():
    try:
        idno = request.form.get('idno')
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        sitio = request.form.get('sitio')
        image_data = request.form.get('image')

        if not all([idno, lastname, firstname, sitio, image_data]):
            return jsonify({"message": "All fields required", "success": False}), 400

        if not image_data.startswith("data:image/jpeg;base64,"):
            return jsonify({"message": "Invalid image format", "success": False}), 400

        # Decode the base64 image data
        image_bytes = base64.b64decode(image_data.split(",")[1])

        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Create a filename (just filename, no full path saved to DB)
        image_filename = f"{idno}_{lastname}.jpeg"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

        # Save the image file
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        # Save record with image filename in the DB
        postprocess(
            "INSERT INTO youths_name (idno, lastname, firstname, sitio, image) VALUES (?, ?, ?, ?, ?)",
            (idno, lastname, firstname, sitio, image_filename)
        )
        return jsonify({"message": "Youth saved successfully", "success": True}), 200

    except sqlite3.IntegrityError:
        return jsonify({"message": "ID already exists", "success": False}), 400
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 500

@app.route("/edit/<idno>", methods=['GET', 'POST'])
def edit_youth_route(idno):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    db = connect(DATABASE)
    cursor = db.cursor()

    if request.method == 'POST':
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        sitio = request.form['sitio']

        cursor.execute(
            '''UPDATE youths_name SET lastname=?, firstname=?, sitio=? WHERE idno=?''',
            (lastname, firstname, sitio, idno)
        )
        db.commit()
        return redirect(url_for('mainpage'))

    youth = get_youth(idno)
    return render_template('edit_youth.html', youth=youth) if youth else ("Youth not found", 404)

@app.route("/delete/<idno>")
def delete(idno):
    if delete_youth(idno):
        flash("Youth deleted.")
    else:
        flash("Error deleting youth.")
    return redirect(url_for("mainpage"))

@app.route("/studlist")
def studlist():
    youths = get_youths()
    return render_template("studentlist.html", pagetitle="Youth List", youths=youths)

@app.route("/mark_attendance", methods=['POST'])
def mark_attendance():
    try:
        youth_id = request.form['student_id']
        status = request.form['status']

        if status not in ['Present', 'Absent', 'Late']:
            flash("Invalid status.")
            return redirect(url_for("checker"))

        if not get_youth(youth_id):
            flash("Youth not found.")
            return redirect(url_for("checker"))

        postprocess(
            "INSERT INTO attendance (idno, date, status) VALUES (?, CURRENT_TIMESTAMP, ?)",
            (youth_id, status)
        )
        flash("Attendance marked.")
        return redirect(url_for("youth_details", idno=youth_id))

    except Exception as e:
        flash(f"Attendance error: {e}")
        return redirect(url_for("checker"))

@app.route("/student/<idno>")
def youth_details(idno):
    youth = get_youth(idno)
    if not youth:
        flash("Youth not found.")
        return redirect(url_for("checker"))
    return render_template("attendancechecker.html", youths=[youth])  # pass as youths list for template consistency

@app.route("/attendance")
def attendance():
    try:
        sql = """
        SELECT a.id, y.idno, y.lastname, y.firstname, a.date, a.status 
        FROM attendance a 
        JOIN youths_name y ON a.idno = y.idno 
        ORDER BY a.date DESC
        """
        attendance_records = getprocess(sql)
        return render_template("attendance.html", pagetitle="View Attendance", attendance_records=attendance_records)
    except Exception as e:
        flash(f"Failed to retrieve attendance: {e}")
        return render_template("attendance.html", attendance_records=[])

# ---------- App Entry ----------

if __name__ == "__main__":
    app.run(debug=True)
