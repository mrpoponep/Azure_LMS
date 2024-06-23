from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash
import local_settings

import os

def read_student_ids_from_file(file_path):
    """
    Read student IDs from a text file, each line containing one student ID.
    """
    if not os.path.isfile(file_path):
        return (False, f"File not found: {file_path}")
    
    student_ids = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                student_id = line.strip()
                if student_id.isdigit():
                    student_ids.append(int(student_id))
                else:
                    return (False, f"Invalid student ID found in file: {line.strip()}")
    except Exception as e:
        return (False, str(e))
    
    return (True, student_ids)

def get_conn():
    conn = connect(
        host=local_settings.MYSQL_HOST,
        user=local_settings.MYSQL_USER,
        password=local_settings.MYSQL_PASSWORD,
        database=local_settings.MYSQL_DB,
    )
    return conn

def create_student_course(StudentID, CourseID):
    """
    CREATE TABLE StudentCourse (
        StudentID INT NOT NULL,
        CourseID INT NOT NULL,
        PRIMARY KEY (StudentID, CourseID),
        FOREIGN KEY (StudentID) REFERENCES Users(ID)
        ON DELETE RESTRICT,
        FOREIGN KEY (CourseID) REFERENCES Courses(ID)
        ON DELETE RESTRICT
    );
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        INSERT INTO StudentCourse
        (StudentID, CourseID)
        VALUES
        ({StudentID}, {CourseID})
    """
    try:
        cur.execute(sql_str)
        conn.commit()
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e))
    cur.close()
    conn.close()
    return (True, "Student participated in the course successfully.")

if __name__ == '__main__':
    file_path = 'studentlist.txt'
    students = read_student_ids_from_file(file_path)
    print(students)
    course_id = 6  # Replace with your course ID
    for student in students[1]:
        print(student)
        create_student_course(student,course_id)    
    #result = add_students_to_course(file_path, course_id)
    #print(result)