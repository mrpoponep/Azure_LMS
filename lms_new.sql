CREATE DATABASE lms;
USE lms;
SHOW TABLES;
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
    
CREATE TABLE CourseTemplates (
    TemplateID VARCHAR(50) NOT NULL PRIMARY KEY,
    clusterID INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    FOREIGN KEY (clusterID) REFERENCES clusters(ID),
    Contents LONGTEXT
);

ALTER TABLE Courses ADD TemplateID VARCHAR(50);

ALTER TABLE Courses ADD FOREIGN KEY (TemplateID) REFERENCES CourseTemplates(TemplateID) ON DELETE SET NULL;
