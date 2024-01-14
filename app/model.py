from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash
import local_settings


def get_conn():
    conn = connect(
        host=local_settings.MYSQL_HOST,
        user=local_settings.MYSQL_USER,
        password=local_settings.MYSQL_PASSWORD,
        database=local_settings.MYSQL_DB,
    )
    return conn


def create_user(
    Username,
    Password,
    is_student="DEFAULT",
    is_teacher="DEFAULT",
    is_manager="DEFAULT",
    is_admin="DEFAULT",
    LastName="DEFAULT",
    FirstName="DEFAULT",
    PhoneNumber="DEFAULT",
    Email="DEFAULT",
    Faculty="DEFAULT",
    Institution="DEFAULT",
    Address="DEFAULT",
):
    """
    CREATE TABLE Users (
        ID INT NOT NULL AUTO_INCREMENT,
        Username VARCHAR(64) NOT NULL UNIQUE,
        Password VARCHAR(255) NOT NULL,
        is_student BOOLEAN DEFAULT false,
        is_teacher BOOLEAN DEFAULT false,
        is_manager BOOLEAN DEFAULT false,
        is_admin BOOLEAN DEFAULT false,
        LastName VARCHAR(255),
        FirstName VARCHAR(255),
        PhoneNumber CHAR(13),
        Email VARCHAR(320),
        Faculty VARCHAR(255),
        Institution VARCHAR(255),
        Address VARCHAR(2048),
        PRIMARY KEY (ID)
    );

    """
    if len(Username) < 4:
        error_message = "Username should be at least 4 characters long"
        return (False, error_message)
    if len(Password) < 6:
        error_message = "Password should be at least 6 characters long"
        return (False, error_message)
    conn = get_conn()
    cur = conn.cursor()
    Password = generate_password_hash(Password)
    sql_str = f"""
        INSERT INTO Users
        (Username, Password, is_student, is_teacher, is_manager, is_admin,
        LastName, FirstName, PhoneNumber, Email, Faculty, Institution, Address)
        VALUES
        ('{Username}', '{Password}', {is_student}, {is_teacher},
        {is_manager},{is_admin}, '{LastName}', '{FirstName}', '{PhoneNumber}',
        '{Email}', '{Faculty}', '{Institution}', '{Address}')
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
    return (True, f"User with username: {Username} created successfully")

def remove_content(ContentID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        DELETE FROM contents WHERE ID={ContentID};
    """
    try:
        cur.execute(sql_str)
        conn.commit()  # Commit the changes to the database
    except Error as e:
        cur.close()
        conn.close()
        return False, str(e)  # Return the error message if deletion fails
    finally:
        cur.close()
        conn.close()
    return True, "Success"

def check_login(Username, Password):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT ID, Username, Password, FirstName, LastName,
        is_student, is_teacher, is_manager, is_admin
        FROM Users WHERE
        Username = '{Username}'
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    raw_user = cur.fetchone()
    cur.close()
    conn.close()
    if raw_user:
        if check_password_hash(raw_user.pop("Password"), Password):
            return (True, "Correct username and password", raw_user)
    return (False, "Wrong username or password", raw_user)


def get_user_list():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = """
        SELECT Username, FirstName AS 'First Name', LastName AS 'Last Name',
        PhoneNumber AS 'Phone Number', Email, Faculty, ID
        FROM Users
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    user_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "User list retrieved from db, successfully", user_list)

def get_teacher_list():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = """
        SELECT Username, FirstName AS 'First Name', LastName AS 'Last Name',
        PhoneNumber AS 'Phone Number', Email, Faculty, ID
        FROM Users
        WHERE is_teacher = true
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    user_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "User list retrieved from db, successfully", user_list)


def get_user_profile(ID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT *
        FROM Users
        WHERE ID={ID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    raw_user = cur.fetchone()
    cur.close()
    conn.close()
    if raw_user:
        raw_user.pop("Password")
        return (True, "User profile retrieved from db, successfully", raw_user)
    return (False, "No such user exists", None)


def edit_user_profile(
    ID,
    Username,
    LastName="DEFAULT",
    FirstName="DEFAULT",
    PhoneNumber="DEFAULT",
    Email="DEFAULT",
    Faculty="DEFAULT",
    Institution="DEFAULT",
    Address="DEFAULT",
):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        UPDATE Users
        SET LastName = '{LastName}', FirstName = '{FirstName}',
        PhoneNumber = '{PhoneNumber}', Email = '{Email}',
        Faculty = '{Faculty}', Institution = '{Institution}',
        Address = '{Address}', Username = '{Username}'
        WHERE ID = {ID};
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
    return (True, "User profile updated successfully.")


def create_cluster(Name):
    """
    CREATE TABLE Clusters (
        ID INT NOT NULL AUTO_INCREMENT,
        Name VARCHAR(64) NOT NULL UNIQUE,
        PRIMARY KEY (ID)
    );
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        INSERT INTO Clusters (Name)
        VALUES ('{Name}')
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
    return (True, "Cluster created successfully.")


def create_manager_cluster(ManagerID, ClusterID):
    """
    CREATE TABLE ManagerCluster (
        ManagerID INT NOT NULL,
        ClusterID INT NOT NULL,
        PRIMARY KEY (ManagerID, ClusterID),
        FOREIGN KEY (ManagerID) REFERENCES Users(ID)
        ON DELETE RESTRICT,
        FOREIGN KEY (ClusterID) REFERENCES Clusters(ID)
        ON DELETE RESTRICT
    )
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        INSERT INTO ManagerCluster
        (ManagerID, ClusterID)
        VALUES
        ({ManagerID}, {ClusterID})
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
    return (True, "Cluster manager created successfully.")


def get_cluster_manager_list(ManagerID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT Name AS 'Cluster Name', ID AS 'Cluster ID'
        FROM Clusters WHERE ID IN
            (SELECT ClusterID
            FROM ManagerCluster
            WHERE ManagerID={ManagerID})
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    cluster_manager_list = cur.fetchall()
    cur.close()
    conn.close()
    return (
        True,
        "Manager's clusters retrieved from db, successfully",
        cluster_manager_list,
    )


def is_manager(UserID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT COUNT(1) AS is_manager
        FROM ManagerCluster
        WHERE ManagerID={UserID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    manager = cur.fetchone()
    cur.close()
    conn.close()
    return (
        True,
        "User checked for manager successfully",
        bool(int(manager["is_manager"])),
    )


def get_cluster_list(ManagerID, is_admin=False):
    if is_admin:
        return get_all_cluster_list()
    return get_cluster_manager_list(ManagerID)


def get_all_cluster_list():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = """
        SELECT Name AS 'Cluster Name', ID AS 'Cluster ID'
        FROM Clusters
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    cluster_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Clusters retrieved from db, successfully.", cluster_list)


def create_course(Name, TeacherID, ClusterID):
    """
    CREATE TABLE Courses (
        ID INT NOT NULL AUTO_INCREMENT,
        Name VARCHAR(64) NOT NULL,
        ClusterID INT NOT NULL,
        TeacherID INT NOT NULL,
        PRIMARY KEY (ID),
        FOREIGN KEY (ClusterID) REFERENCES Clusters(ID)
        ON DELETE RESTRICT,
        FOREIGN KEY (TeacherID) REFERENCES Users(ID)
        ON DELETE RESTRICT
    );
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        INSERT INTO Courses
        (Name, ClusterID, TeacherID)
        VALUES
        ('{Name}', {ClusterID}, {TeacherID})
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
    return (True, "Course created successfully.")


def get_all_course_list():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = """
        SELECT Name, ClusterID, TeacherID, ID
        FROM Courses
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e))
    course_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Course list retrieved from db, successfully", course_list)


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


def get_student_course_list(StudentID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT c.Name AS 'Course Name', u.FirstName AS 'Teacher First Name',
        u.LastName AS 'Teacher Last Name', c.ID AS 'Course ID'
        FROM ((StudentCourse AS sc
            INNER JOIN Courses AS c ON sc.CourseID = c.ID)
            INNER JOIN Users AS u ON c.TeacherID = u.ID)
        WHERE sc.StudentID = {StudentID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    student_course_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Courses retrieved from db, successfully.", student_course_list)


def get_teacher_course_list(TeacherID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT c.Name AS 'Course Name', u.FirstName AS 'Teacher First Name',
        u.LastName AS 'Teacher Last Name', c.ID AS 'Course ID'
        FROM Courses AS c
            INNER JOIN Users AS u ON c.TeacherID = u.ID
        WHERE c.TeacherID = {TeacherID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    teacher_course_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Courses retrieved from db, successfully.", teacher_course_list)


def is_teacher(UserID, CourseID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT COUNT(1) AS is_teacher
        FROM Courses
        WHERE ID={CourseID} AND TeacherID={UserID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    teacher = cur.fetchone()
    cur.close()
    conn.close()
    return (
        True,
        "User checked for teacher successfully",
        bool(int(teacher["is_teacher"])),
    )

def get_course(CourseID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT ID AS 'Course ID', Name AS 'Course Name', TeacherID AS 'Teacher ID'
        FROM Courses
        WHERE ID = {CourseID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    course = cur.fetchone()
    cur.close()
    conn.close()
    return (True, "Course retrieved from db, successfully", course)

def remove_quiz(QuizID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
       # Start a transaction
        conn.start_transaction()

        # Delete associated responde first
        delete_questions_query = f"DELETE FROM quizresponses WHERE QuizID = {QuizID}"
        cur.execute(delete_questions_query)

        # Delete associated questions first
        delete_questions_query = f"DELETE FROM questions WHERE QuizID = {QuizID}"
        cur.execute(delete_questions_query)

        # Now, delete the quiz itself
        delete_quiz_query = f"DELETE FROM quizzes WHERE QuizID = {QuizID}"
        cur.execute(delete_quiz_query)

        # Commit the transaction
        conn.commit()

        print(f"Quiz with QuizID {QuizID} and its associated questions deleted successfully.")
    except Exception as e:
        # Handle any errors that may occur during the deletion
        print(f"Error deleting quiz and questions: {e}")
        conn.rollback()
    finally:
        # Close the database connection and cursor
        cur.close()
        conn.close()

    return True, "Success"

def get_question(QuizID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT QuestionID, QuestionText, QuestionType, Options, CorrectAnswer
        FROM questions
        WHERE QuizID = {QuizID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    questions = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Question retrieved from the database successfully", questions)

def get_quiz_list(CourseID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT QuizID, Title, CreatedAt, AllowStudents
        FROM quizzes
        WHERE CourseID = {CourseID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    quiz_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Quiz list retrieved from db, successfully", quiz_list)

def create_quizz(CourseID,Title,TeacherID,Max_tries):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    
    sql_str = f"""
        INSERT INTO quizzes
        (CourseID,TeacherID ,Title, Max_tries)
        VALUES
        ({CourseID}, '{TeacherID}', '{Title}', "{Max_tries}")
    """
    try:
        cur.execute(sql_str)
        cur.execute("SELECT LAST_INSERT_ID() AS QuizID")
        quizz_id = cur.fetchone()["QuizID"]
        conn.commit()
        
    except Error as e:
        cur.close()
        conn.close()
        return (0,False, str(e))
    cur.close()
    conn.close()
    return (quizz_id, True, "Content created successfully.",)

def view_quiz_responses(CourseID,quiz_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT
            qr.ResponseID,
            u.ID,
            u.UserName,
            qr.QuizID,
            qr.QuestionID,
            qr.Answer,
            qr.Score,
            qr.Tries,
            qr.TimeTaken
        FROM
            QuizResponses qr
        JOIN
            Users u ON qr.StudentID = u.ID
        WHERE
            qr.QuizID = {quiz_id};
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return (True, "User list retrieved from db, successfully", rows)

def add_question_to_quiz(quiz_id,question_data):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    for question in question_data:
        # Extract data from the question dictionary
        question_text = question['content']
        question_type = question['type']
        if question['options']:
            options = '*'.join(question['options'])
        else:
            options = None
        correct_answer = question['answer']

        # Insert the question into the database
        sql_str = f"""
            INSERT INTO questions
            ( QuizID, QuestionText, QuestionType, Options, CorrectAnswer)
            VALUES
            ({quiz_id}, '{question_text}', '{question_type}', '{options}', '{correct_answer}')
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
    return (True, "Content created successfully.")

def stop_students_viewing(QuizID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        UPDATE `lms`.`quizzes` SET `AllowStudents` = 0 WHERE (`QuizID` = {QuizID});"""
    try:
        cur.execute(sql_str)
        conn.commit()
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e))
    cur.close()
    conn.close()
    return (True, "Content created successfully.")

def allow_students_viewing(QuizID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        UPDATE `lms`.`quizzes` SET `AllowStudents` = 1 WHERE (`QuizID` = {QuizID});"""
    try:
        cur.execute(sql_str)
        conn.commit()
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e))
    cur.close()
    conn.close()
    return (True, "Content created successfully.")

def create_content(CourseID, Title, TextContent):
    """
    CREATE TABLE Contents (
        ID INT NOT NULL AUTO_INCREMENT,
        CourseID INT NOT NULL,
        Title VARCHAR(255) NOT NULL,
        TextContent LONGTEXT,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ID),
        FOREIGN KEY (CourseID) REFERENCES Courses(ID)
        ON DELETE RESTRICT
    );
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        INSERT INTO Contents
        (CourseID, Title, TextContent)
        VALUES
        ({CourseID}, '{Title}', '{TextContent}')
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
    return (True, "Content created successfully.")


def get_content_list(CourseID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT ID, Title, TextContent, CreatedAt
        FROM Contents
        WHERE CourseID = {CourseID}
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    content_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Contents retrieved from db, successfully", content_list)


def get_course_student_list(CourseID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT Username, FirstName AS 'First Name', LastName AS 'Last Name',
        PhoneNumber AS 'Phone Number', Email, Faculty
        FROM Users
        WHERE ID IN
        (SELECT StudentID FROM StudentCourse
        WHERE CourseID = {CourseID})
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    student_list = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Student list retrieved from db, successfully", student_list)

def find_tries(QuizID, QuestionID, StudentID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT MAX(Tries) AS Tries FROM quizresponses 
        WHERE QuizID = {QuizID} AND QuestionID = {QuestionID} AND StudentID = {StudentID};
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    tries = cur.fetchone()
    cur.close()
    conn.close()
    return (True, "Tries retrieved from the database successfully", tries)

def save_responses(QuizID, QuestionID ,StudentID, Tries, Answer,Score,Explanation):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = """
        INSERT INTO quizresponses
        (QuizID, QuestionID, StudentID, Tries, Answer, Score, Explanation)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
    """

    data = (QuizID, QuestionID, StudentID, Tries, Answer, Score, Explanation)
    try:
        cur.execute(sql_str, data)
        conn.commit()
        
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e))
    cur.close()
    conn.close()
    return (True, "Submited")
#-----------------------------END Duyen------------------------------

def quiz_result_teacher_list(QuizID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT q.StudentID, u.FirstName, u.LastName, MAX(q.TotalScore) AS MAXTotalScore
        FROM (
            SELECT StudentID, Tries, SUM(Score) AS TotalScore
            FROM quizresponses
            WHERE QuizID = {QuizID}
            GROUP BY StudentID, Tries
        ) q
        JOIN users u ON q.StudentID = u.ID
        GROUP BY q.StudentID;
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    result_teacher = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Result retrieved from the database successfully", result_teacher)

def quiz_result_student_list(QuizID,StudentID):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT q.StudentID, u.FirstName, u.LastName, q.Tries, SUM(q.Score) AS TotalScore
        FROM QuizResponses q
        JOIN Users u ON q.StudentID = u.ID
        WHERE q.QuizID = {QuizID} AND q.StudentID = {StudentID}
        GROUP BY q.StudentID, u.FirstName, u.LastName, q.Tries;
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    result_student = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Result retrieved from the database successfully", result_student)

def quiz_result_student(QuizID, StudentID, Tries):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql_str = f"""
        SELECT Q.QuestionText, QR.Score, QR.Answer, Q.CorrectAnswer, Q.QuestionID, QR.Explanation 
        FROM QuizResponses QR
        JOIN Questions Q ON QR.QuestionID = Q.QuestionID
        WHERE QR.QuizID = {QuizID} AND QR.StudentID = {StudentID} AND QR.Tries = {Tries}; 
    """
    try:
        cur.execute(sql_str)
    except Error as e:
        cur.close()
        conn.close()
        return (False, str(e), None)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return (True, "Result retrieved from the database successfully", results)