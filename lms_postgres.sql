CREATE TABLE Users (
        ID SERIAL NOT NULL,
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
--ALTER TABLE Users ADD CONSTRAINT check_phone_number CHECK (PhoneNumber ~ '[0-9]{1,13}');
    
CREATE TABLE Clusters (
        ID SERIAL NOT NULL,
        Name VARCHAR(64) NOT NULL UNIQUE,
        PRIMARY KEY (ID)
    );
    
CREATE TABLE ManagerCluster (
        ManagerID INT NOT NULL,
        ClusterID INT NOT NULL,
        PRIMARY KEY (ManagerID, ClusterID),
        FOREIGN KEY (ManagerID) REFERENCES Users(ID)
        ON DELETE RESTRICT,
        FOREIGN KEY (ClusterID) REFERENCES Clusters(ID)
        ON DELETE RESTRICT
);
CREATE TABLE CourseTemplates (
    ID SERIAL PRIMARY KEY NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Contents TEXT
);
    
CREATE TABLE Courses (
        ID SERIAL NOT NULL,
        Name VARCHAR(64) NOT NULL,
        ClusterID INT NOT NULL,
        TeacherID INT NOT NULL,
		TemplateID INT NOT NUll,
        PRIMARY KEY (ID),
        FOREIGN KEY (TemplateID) REFERENCES CourseTemplates(ID)
		ON DELETE RESTRICT,
        FOREIGN KEY (ClusterID) REFERENCES Clusters(ID)
        ON DELETE RESTRICT,
        FOREIGN KEY (TeacherID) REFERENCES Users(ID)
        ON DELETE RESTRICT
    );
    
CREATE TABLE StudentCourse (
        StudentID INT NOT NULL,
        CourseID INT NOT NULL,
        PRIMARY KEY (StudentID, CourseID),
        FOREIGN KEY (StudentID) REFERENCES Users(ID)
        ON DELETE RESTRICT,
        FOREIGN KEY (CourseID) REFERENCES Courses(ID)
        ON DELETE RESTRICT
		
        );
        
CREATE TABLE Contents (
        ID SERIAL NOT NULL,
        CourseID INT NOT NULL,
        Title VARCHAR(255) NOT NULL,
        TextContent TEXT,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ID),
        FOREIGN KEY (CourseID) REFERENCES Courses(ID)
        ON DELETE RESTRICT
);
    
CREATE TABLE Quizzes (
    QuizID SERIAL NOT NULL,
    TeacherID INT,
    CourseID INT,
    Title VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Max_tries INT,
    AllowStudents INT,
    PRIMARY KEY (QuizID),
    FOREIGN KEY (TeacherID) REFERENCES Users(ID),
    FOREIGN KEY (CourseID) REFERENCES Courses(ID),
	CHECK(AllowStudents IN (0, 1))
);

CREATE TYPE question_type AS ENUM ('multiple_choice', 'short_answer');

CREATE TABLE Questions (
    QuestionID SERIAL NOT NULL,
    QuizID INT,
    QuestionText TEXT NOT NULL,
    QuestionType question_type NOT NULL,
    Options TEXT,  -- For multiple-choice questions
    CorrectAnswer TEXT,  -- For short-answer questions
    PRIMARY KEY (QuestionID),
    FOREIGN KEY (QuizID) REFERENCES Quizzes(QuizID)
);

CREATE TABLE QuizResponses(
    ResponseID SERIAL NOT NULL,
    StudentID INT,
    QuestionID INT,
    QuizID INT,
    Explanation TEXT,
    Answer TEXT,
    Score INT DEFAULT -1,
    Tries INT,
    TimeTaken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ResponseID),
    FOREIGN KEY (QuizID) REFERENCES Quizzes(QuizID),
    FOREIGN KEY (StudentID) REFERENCES Users(ID),
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID) 
);

---ALTER TABLE QuizResponses DROP CONSTRAINT check_score;
ALTER TABLE QuizResponses ADD CONSTRAINT check_score CHECK (Score >= -1 AND Score <= 10);
ALTER TABLE Users ADD CONSTRAINT check_phone_number CHECK (PhoneNumber ~ '[0-9]{1,13}');
-----------------------------------------
CREATE OR REPLACE FUNCTION check_max_tries()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM QuizResponses 
        WHERE StudentID = NEW.StudentID AND QuestionID = NEW.QuestionID) >= 
       (SELECT Max_tries FROM Quizzes WHERE QuizID = NEW.QuizID) THEN
        RAISE EXCEPTION 'Student has exceeded the maximum number of tries for this question';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_max_tries_trigger
BEFORE INSERT ON QuizResponses
FOR EACH ROW
EXECUTE FUNCTION check_max_tries();
-----------------------------------------
CREATE OR REPLACE FUNCTION check_user_roles()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.is_student::int + NEW.is_teacher::int + NEW.is_manager::int + NEW.is_admin::int) > 1 THEN
        RAISE EXCEPTION 'A user cannot have more than one role';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_user_roles_trigger
BEFORE INSERT OR UPDATE ON Users
FOR EACH ROW
EXECUTE FUNCTION check_user_roles();
-------------------------------------
CREATE OR REPLACE FUNCTION check_student_course()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the student exists and is a student
    IF NOT EXISTS (
        SELECT 1 
        FROM Users 
        WHERE ID = NEW.StudentID AND is_student = TRUE
    ) THEN
        RAISE EXCEPTION 'Student ID % does not exist or is not a student', NEW.StudentID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_studentcourse
BEFORE INSERT ON StudentCourse
FOR EACH ROW
EXECUTE FUNCTION check_student_course();
-------------------------------------
CREATE OR REPLACE FUNCTION check_course_teacher()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the teacher exists and is a teacher
    IF NOT EXISTS (
        SELECT 1 
        FROM Users 
        WHERE ID = NEW.TeacherID AND is_teacher = TRUE
    ) THEN
        RAISE EXCEPTION 'Teacher ID % does not exist or is not a teacher', NEW.TeacherID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_courses
BEFORE INSERT ON Courses
FOR EACH ROW
EXECUTE FUNCTION check_course_teacher();
-------------------------------------
CREATE OR REPLACE FUNCTION check_manager_cluster()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the manager exists and is a manager
    IF NOT EXISTS (
        SELECT 1 
        FROM Users 
        WHERE ID = NEW.ManagerID AND is_manager = TRUE
    ) THEN
        RAISE EXCEPTION 'Manager ID % does not exist or is not a manager', NEW.ManagerID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_managercluster
BEFORE INSERT ON ManagerCluster
FOR EACH ROW
EXECUTE FUNCTION check_manager_cluster();
-------------------------------------
CREATE INDEX idx_users_username ON Users(Username);
CREATE INDEX idx_courses_name ON Courses(Name);
CREATE INDEX idx_quizzes_title ON Quizzes(Title);
CREATE INDEX idx_questions_questiontext ON Questions(QuestionText);
CREATE INDEX idx_quizresponses_score ON QuizResponses(Score);
---CREATE FUNCTION 
CREATE OR REPLACE FUNCTION get_students_in_course(course_id INT)
RETURNS TABLE (
    StudentID INT,
    Username VARCHAR(64),
    LastName VARCHAR(255),
    FirstName VARCHAR(255),
    Email VARCHAR(320)
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.ID AS StudentID, u.Username, u.LastName, u.FirstName, u.Email
    FROM Users u
    JOIN StudentCourse sc ON u.ID = sc.StudentID
    WHERE sc.CourseID = course_id
    AND u.ID IN (SELECT sc.StudentID FROM StudentCourse sc WHERE sc.CourseID = course_id); 
END;
$$ LANGUAGE plpgsql;

---------------------------------------
--DROP FUNCTION get_students_above_8(integer)
CREATE OR REPLACE FUNCTION get_students_above_8(course_id INT)
RETURNS TABLE (
    StudentID INT,
    Username VARCHAR(64),
    LastName VARCHAR(255),
    FirstName VARCHAR(255),
    Email VARCHAR(320),
    Score INT,
	quizid INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.ID AS StudentID, u.Username, u.LastName, u.FirstName, u.Email,
        qr.Score,
		qr.quizid
    FROM Users u
    JOIN QuizResponses qr ON u.ID = qr.StudentID
    WHERE qr.Score > 8
    AND qr.QuizID IN (SELECT q.QuizID FROM Quizzes q WHERE q.CourseID = course_id)
	ORDER BY qr.quizid;
END;
$$ LANGUAGE plpgsql;
--SELECT * FROM get_students_above_8(4)
--------------------------------
CREATE OR REPLACE FUNCTION get_students_between_5_and_8(course_id INT)
RETURNS TABLE (
    StudentID INT,
    Username VARCHAR(64),
    LastName VARCHAR(255),
    FirstName VARCHAR(255),
    Email VARCHAR(320),
    Score INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.ID AS StudentID, u.Username, u.LastName, u.FirstName, u.Email,
        qr.Score
    FROM Users u
    JOIN QuizResponses qr ON u.ID = qr.StudentID
    WHERE qr.Score >= 5 AND qr.Score <= 8
    AND qr.QuizID IN (SELECT q.QuizID FROM Quizzes q WHERE q.CourseID = course_id);
END;
$$ LANGUAGE plpgsql;
-------------------------------
CREATE OR REPLACE FUNCTION get_students_below_5(course_id INT)
RETURNS TABLE (
    StudentID INT,
    Username VARCHAR(64),
    LastName VARCHAR(255),
    FirstName VARCHAR(255),
    Email VARCHAR(320),
    Score INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.ID AS StudentID, u.Username, u.LastName, u.FirstName, u.Email,
        qr.Score
    FROM Users u
    JOIN QuizResponses qr ON u.ID = qr.StudentID
    WHERE qr.Score < 5 
	AND qr.QuizID IN (SELECT q.QuizID FROM Quizzes q WHERE q.CourseID = course_id);
END;
$$ LANGUAGE plpgsql;
-------------------------------
CREATE OR REPLACE FUNCTION get_students_with_score_minus_1(course_id INT)
RETURNS TABLE (
    StudentID INT,
    Username VARCHAR(64),
    LastName VARCHAR(255),
    FirstName VARCHAR(255),
    Email VARCHAR(320),
    Score INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.ID AS StudentID, u.Username, u.LastName, u.FirstName, u.Email,
        qr.Score
    FROM Users u
    JOIN QuizResponses qr ON u.ID = qr.StudentID
    WHERE qr.Score = -1
    AND qr.QuizID IN (SELECT q.QuizID FROM Quizzes q WHERE q.CourseID = course_id);
END;
$$ LANGUAGE plpgsql;
---------------------------------
CREATE OR REPLACE FUNCTION get_courses_for_student(student_id INT) RETURNS TABLE (
    course_id INT,
    course_name CHARACTER VARYING(64)
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.ID AS course_id, c.Name AS course_name
    FROM courses c
    JOIN studentcourse sc ON sc.courseid = c.ID
    WHERE sc.studentid = student_id;
END;
$$ LANGUAGE plpgsql;

-----------------------------------
ALTER TABLE CourseTemplates RENAME Name to TemplateName;
ALTER TABLE CourseTemplates RENAME ID to TemplateID;