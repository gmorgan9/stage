import os
from flask import Flask, request, jsonify, render_template
import MySQLdb
import random
import string
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Database connection
db = MySQLdb.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    passwd=os.getenv('DB_PASS'),
    db=os.getenv('DB_NAME')
)

cursor = db.cursor()

# Generate random password
def generate_password():
    special_characters = "!@#$&"
    numbers = ''.join(random.choices(string.digits, k=3))
    lowercase = ''.join(random.choices(string.ascii_lowercase, k=4))
    special = random.choice(special_characters)
    return lowercase + numbers + special

# Create username
def create_username(first_name, last_name):
    base_username = (last_name[:5] + first_name[:3]).lower()
    query = "SELECT COUNT(*) FROM students WHERE username LIKE '{}%'".format(base_username)
    cursor.execute(query)
    count = cursor.fetchone()[0]
    return f"{base_username}{str(count).zfill(3)}"

@app.route('/add_students_form', methods=['GET'])
def add_students_form():
    return render_template('add_students_form.html')

@app.route('/add_students', methods=['POST'])
def add_students():
    num_students = int(request.form.get('num_students'))
    students = []

    # Generate the student entries
    for _ in range(num_students):
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        grade = request.form.get('grade')

        username = create_username(first_name, last_name)
        password = generate_password()

        students.append({
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "grade": grade
        })

    # Insert students into the database
    for student in students:
        query = """INSERT INTO students (first_name, last_name, username, password, grade)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (student['first_name'], student['last_name'], student['username'], student['password'], student['grade']))
        db.commit()

    return render_template('student_list.html', students=students)

@app.route('/view_students', methods=['GET'])
def view_students():
    query = "SELECT first_name, last_name, username, password, grade FROM students"
    cursor.execute(query)
    students = cursor.fetchall()

    student_list = []
    for student in students:
        student_list.append({
            "first_name": student[0],
            "last_name": student[1],
            "username": student[2],
            "password": student[3],
            "grade": student[4]
        })

    return jsonify(student_list), 200

if __name__ == '__main__':
    # Use SSL context with certificates in the same directory as app.py
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
