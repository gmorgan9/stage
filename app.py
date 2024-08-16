import os
from flask import Flask, request, jsonify
import MySQLdb
import random
import string
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)

db = MySQLdb.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    passwd=os.getenv('DB_PASS'), 
    db=os.getenv('DB_NAME'),
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

@app.route('/add_students', methods=['POST'])
def add_students():
    data = request.json
    students = data.get('students')

    if not students or not isinstance(students, list):
        return jsonify({"error": "Invalid input"}), 400

    added_students = []

    for student in students:
        first_name = student.get('first_name')
        last_name = student.get('last_name')
        grade = student.get('grade')

        if not first_name or not last_name or not grade:
            continue

        username = create_username(first_name, last_name)
        password = generate_password()

        query = """INSERT INTO students (first_name, last_name, username, password, grade)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (first_name, last_name, username, password, grade))
        db.commit()

        added_students.append({
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "grade": grade
        })

    return jsonify({"added_students": added_students}), 201

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
    app.run(debug=True)
