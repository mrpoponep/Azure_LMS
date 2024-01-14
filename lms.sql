create database lms;
use lms;
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
    
    CREATE TABLE Clusters (
        ID INT NOT NULL AUTO_INCREMENT,
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
        ID INT NOT NULL AUTO_INCREMENT,
        CourseID INT NOT NULL,
        Title VARCHAR(255) NOT NULL,
        TextContent LONGTEXT,
        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ID),
        FOREIGN KEY (CourseID) REFERENCES Courses(ID)
        ON DELETE RESTRICT
    );
    
CREATE TABLE Quizzes (
    QuizID INT NOT NULL AUTO_INCREMENT,
    TeacherID INT,
    CourseID INT,
    Title VARCHAR(255) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    Max_tries INT,
    AllowStudents TINYINT(1),
    PRIMARY KEY (QuizID),
    FOREIGN KEY (TeacherID) REFERENCES Users(ID),
    FOREIGN KEY (CourseID) REFERENCES Courses(ID)
);

CREATE TABLE Questions (
    QuestionID INT NOT NULL AUTO_INCREMENT,
    QuizID INT,
    QuestionText TEXT NOT NULL,
    QuestionType ENUM('multiple_choice', 'short_answer') NOT NULL,
    Options TEXT,  -- For multiple-choice questions
    CorrectAnswer TEXT,  -- For short-answer questions
    PRIMARY KEY (QuestionID),
    FOREIGN KEY (QuizID) REFERENCES Quizzes(QuizID)
);

CREATE TABLE QuizResponses (
    ResponseID INT NOT NULL AUTO_INCREMENT,
    StudentID INT,
    QuestionID INT,
    QuizID INT,
    Explanation TEXT,
    Answer TEXT,
    Score INT,
    Tries INT,
    TimeTaken DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ResponseID),
    FOREIGN KEY (QuizID) REFERENCES Quizzes(QuizID),
    FOREIGN KEY (StudentID) REFERENCES Users(ID),
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID)
);