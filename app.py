from flask import Flask, render_template, request, redirect, flash
from sqlite3 import connect, Row
from datetime import datetime
import os 
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g, make_response
import cv2
import numpy as np
from io import BytesIO
import sqlite3
import base64
import os
import traceback
from datetime import datetime

database: str = "studentchecker.db"

# Helper functions to interact with the database
def postprocess(sql: str, params: tuple = ()) -> bool:
    """Executes an SQL statement with optional parameters."""
    with connect(database) as db:
        cursor = db.cursor()
        cursor.execute(sql, params)
        db.commit()
        return True if cursor.rowcount > 0 else False

def getprocess(sql: str, params: tuple = ()) -> list:
    """Fetches data from the database using an SQL statement and optional parameters."""
    with connect(database) as db:
        db.row_factory = Row
        cursor = db.cursor()
        cursor.execute(sql, params)
        data = cursor.fetchall()
    return data

# Student functions
def add_student(**kwargs) -> bool:
    """Inserts a new student into the database."""
    keys = list(kwargs.keys())
    values = list(kwargs.values())
    flds = "`,`".join(keys)
    vals = ",".join("?" for _ in values)  # Using placeholders for parameterized query
    sql = f"INSERT INTO students (`{flds}`) VALUES({vals})"
    return postprocess(sql, tuple(values))

def get_admin()->list:
    sql = "SELECT * FROM `admin`"
    return getprocess(sql)
def get_adminId(id: int) -> list:
    """Retrieves a single admin record by ID."""
    sql = "SELECT * FROM `admin` WHERE id=?"
    return getprocess(sql, (id,))

def get_students() -> list:
    """Retrieves all student records from the database."""
    sql = "SELECT * FROM `students`"
    return getprocess(sql)

import sqlite3

def get_student(student_id):
    """Fetch student details by ID from the database."""
    conn = sqlite3.connect('studentchecker.db')
    cursor = conn.cursor()
    
    # Ensure the column order matches your database schema
    cursor.execute("SELECT idno, lastname, firstname, course, level, image FROM students WHERE idno = ?", (student_id,))
    student = cursor.fetchone()  # Fetch one record
    conn.close()
    
    if student: 
        return {
            'idno': student[0],  
            'lastname': student[1],
            'firstname': student[2],
            'course': student[3],
            'level': student[4],
            'image': student[5]  # Assuming this is the correct path
        }
    return None



def edit_student(id: int, **kwargs) -> bool:
    """Updates a student record by ID."""
    updates = [f"`{key}`=?" for key in kwargs.keys()]
    sql = f"UPDATE `students` SET {', '.join(updates)} WHERE idno=?"
    return postprocess(sql, tuple(kwargs.values()) + (id,))

def delete_student(id: int) -> bool:
    """Deletes a student record by ID."""
    sql = "DELETE FROM `students` WHERE idno=?"
    return postprocess(sql, (id,))

# Flask app setup
app = Flask(__name__)

uploadfolder: str = "static/images/students"
app.config['UPLOAD_FOLDER'] = uploadfolder
app.config['SECRET_KEY'] = "secretkey!@#$##$%%$"

@app.route("/saveinformation", methods=['POST'])
def saveinfomartion():
    try:
        idno = request.form.get('idno')
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        course = request.form.get('course')
        level = request.form.get('level')
        image_data = request.form.get('image')  # Captured image from frontend as base64

        # Validate that all required fields are provided
        if not all([idno, lastname, firstname, course, level, image_data]):
            return jsonify({"message": "All form fields must be provided", "success": False}), 400
       
        # Check if the image data is in the correct format
        if not image_data.startswith("data:image/jpeg;base64,"):
            return jsonify({"message": "Image data is not in the expected format.", "success": False}), 400
        
        # Decode the image data and save the image
        image_data = image_data.split(',')[1]  # Remove the data URI prefix
        image_bytes = base64.b64decode(image_data)
        
        # Save the image file to the static/images directory
        os.makedirs('static/images', exist_ok=True)
        image_filename = f"static/images/{idno}_{lastname}.jpeg"
        with open(image_filename, 'wb') as image_file:
            image_file.write(image_bytes)
         
        # Save student data to the database
        db = connect('studentchecker.db')
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO students (idno, lastname, firstname, course, level, image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (idno, lastname, firstname, course, level, image_filename))
        db.commit()

        return jsonify({"message": "Data stored successfully!", "success": True}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "IDNO already exists. Please use a unique IDNO.", "success": False}), 400
    except sqlite3.Error as db_error:
        return jsonify({"message": f"Failed to store data. SQLite Error: {db_error}", "success": False}), 500
    except Exception as e:
        return jsonify({"message": f"Failed to store data. General Error: {e}", "success": False}), 500

@app.route("/edit/<idno>", methods=['GET', 'POST'])
def edit_student(idno):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    db = database('studentchecker.db')
    cursor = db.cursor()

    if request.method == 'POST':
        # Get updated student data from the form
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        course = request.form['course']
        level = request.form['level']
        image_data = request.form.get('image')  

        cursor.execute("SELECT * FROM students WHERE idno = ?", (idno,))
        student = cursor.fetchone()

        if student:
            # Handle image update if provided
            if image_data:
                image_data = image_data.split(',')[1]  # Remove the data URI prefix
                image_bytes = base64.b64decode(image_data)

                # Save the image file to the static/images directory
                os.makedirs('static/images', exist_ok=True)
                image_filename = f"static/images/{idno}_{lastname}.jpeg"
                with open(image_filename, 'wb') as image_file:
                    image_file.write(image_bytes)

                # Update the student's record with the new image path
                cursor.execute('''UPDATE students SET lastname = ?, firstname = ?, course = ?, level = ?, image_path = ? WHERE idno = ?''', 
                               (lastname, firstname, course, level, image_filename, idno))
            else:
                # Update without changing the image
                cursor.execute('''UPDATE students SET lastname = ?, firstname = ?, course = ?, level = ? WHERE idno = ?''', 
                               (lastname, firstname, course, level, idno))

            db.commit()
            return redirect(url_for('mainpage'))  # Redirect after update

    else:
        # Fetch the current student's data to pre-fill the form
        cursor.execute("SELECT * FROM students WHERE idno = ?", (idno,))
        student = cursor.fetchone()

        if student:
            return render_template('edit_student.html', student=student)
        else:
            return "Student not found", 404


@app.route("/delete/<int:idno>", methods=['GET'])
def delete(idno: int) -> None:
    """Handles deleting a student record."""
    if delete_student(idno):
        flash("Student Deleted")
    else:
        flash("Failed to delete student. Please try again.")
    return redirect("/")

@app.route("/mainpage")
def mainpage() -> None:
    """Displays the student registration page with all students."""
    students = get_students()
    return render_template("index.html",pagetitle="Student Registration",students = students)

# @app.route("/login")
# def index() -> None:
#     """Displays the student registration page with all students."""
#     students = get_students()
#     return render_template("login.html")

@app.route("/admin")
def admin() -> None:
    """Displays the student registration page with all students."""
    admin = get_admin()
    return render_template("login.html",pagetitle ="Login",admin = admin)


@app.route("/studlist")
def studlist()->None:
    """Display Student List"""
    students = get_students()
    return render_template("studentlist.html",  pagetitle="Student List", students=students)

@app.route("/mark_attendance", methods=['POST'])
def mark_attendance():
    """Handles marking attendance for a student."""
    try:
        student_id = int(request.form['student_id'])
        status = request.form['status']

        # Validate student existence
        student = getprocess("SELECT * FROM `students` WHERE idno=?", (student_id,))
        if not student:
            flash("Student does not exist. Attendance will not be recorded.")
            return redirect('/')

        if status not in ['Present', 'Absent', 'Late']:
            flash("Invalid status. Please select 'Present', 'Absent', or 'Late'.")
            return redirect('/')

        # Insert attendance record
        if postprocess("INSERT INTO `attendance` (`student_id`, `date`, `status`) VALUES (?, CURRENT_TIMESTAMP, ?)", 
                       (student_id, status)):
            flash("Attendance marked successfully.")
        else:
            flash("Failed to mark attendance. Please try again.")
            return redirect('/')

        # Pass the specific student details to the redirect route
        return redirect(f'/student/{student_id}')
    except ValueError:
        flash("Invalid student ID. Please enter a valid number.")
    except Exception as e:
        flash(f"An error occurred: {e}")
    return redirect('/')

@app.route("/student/<int:student_id>")
def student_details(student_id):
    """Displays details of a specific student."""
    student = get_student(student_id)
    if not student:
        flash("Student not found.")
        return redirect('/')
    return render_template('attendancechecker.html', student=[student])
    

@app.route("/")
def checker() -> None:
    """Displays the student registration page with all students."""
    students = get_students()
    return render_template("attendancechecker.html", pagetitle="Attendance Checker", students=students)


@app.route("/attendance")
def attendance() -> None:
    """Displays the attendance records."""
    try:
        sql = """
        SELECT a.attendance_id, s.idno, s.lastname, s.firstname, a.date, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.idno 
        ORDER BY a.date DESC
        """
        attendance_records = getprocess(sql)
        return render_template("attendance.html",pagetitle = "VIEW ATTENDANCE", attendance_records=attendance_records)
    except Exception as e:
        flash(f"An error occurred while retrieving attendance records: {e}")
        return render_template("attendance.html", pagetitle = "VIEW ATTENDANCE", attendance_records=attendance_records)


@app.route("/login", methods=['post'])
def login() -> None:
    admin = get_admin()
    """Login with RFID."""
    try:
        # Extract student ID (idno) and status from the form
        admin_id = int(request.form['admin_id'])

        # Check if the student exists in the database using idno
        if not getprocess("SELECT * FROM `admin` WHERE id=?", (admin_id,)):
            flash("Invalid admin credentials.")
            return redirect("/admin")
        else:
            flash("Login Successfully!")
    except ValueError:
        flash("Invalid admin credentials.")
    except Exception as e:
        flash(f"An error occurred: {e}")
        print(admin)
    return redirect("/mainpage")

if __name__ == "__main__":
    app.run(debug=True)
