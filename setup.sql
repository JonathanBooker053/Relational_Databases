USE jeopardydb;

DROP TABLE IF EXISTS Answer;
DROP TABLE IF EXISTS GamePlayers;
DROP TABLE IF EXISTS GameQuestions;
DROP TABLE IF EXISTS Client;
DROP TABLE IF EXISTS Games;
DROP TABLE IF EXISTS Questions;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Users;

-- Users Table
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(20) UNIQUE NOT NULL,
    PasswordHash BINARY(64) NOT NULL,
    Salt VARBINARY(8) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL
);

-- Admin Table
CREATE TABLE Admin (
    UserID INT PRIMARY KEY,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON UPDATE CASCADE
);

-- Games Table
CREATE TABLE Games (
    GameID INT AUTO_INCREMENT PRIMARY KEY,
    DatePlayed DATETIME,
    Status ENUM('Not Started', 'Jeopardy!', 'Double Jeopardy!', 'Final Jeopardy!', 'Pending', 'Complete') NOT NULL,
    Admin INT NULL,
    Winner INT NULL,
    FOREIGN KEY (Admin) REFERENCES Admin(UserID) ON UPDATE CASCADE
);

-- Questions Table
CREATE TABLE Questions (
    QuestionID INT AUTO_INCREMENT PRIMARY KEY,
    ShowNumber INT,
    AirDate DATE,
    Round VARCHAR(255),
    Category VARCHAR(255),
    Value_ INT,
    Question TEXT,
    Answer TEXT
);

-- Client Table
CREATE TABLE Client (
    UserID INT PRIMARY KEY,
    Score INT DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON UPDATE CASCADE
);

-- GamePlayers Table
CREATE TABLE GamePlayers (
    GamePlayerID INT AUTO_INCREMENT PRIMARY KEY,
    GameID INT,
    UserID INT,
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON UPDATE CASCADE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON UPDATE CASCADE
);

-- GameQuestions Table
CREATE TABLE GameQuestions (
    GameQuestionID INT AUTO_INCREMENT PRIMARY KEY,
    GameID INT,
    QuestionID INT,
    HasBeenAsked TINYINT DEFAULT 0,
    FOREIGN KEY (GameID) REFERENCES Games(GameID) ON UPDATE CASCADE,
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID) ON UPDATE CASCADE
);

-- Answer Table
CREATE TABLE Answer (
    AnswerID INT AUTO_INCREMENT PRIMARY KEY,
    GamePlayerID INT,
    GameQuestionID INT,
    UserAnswer TEXT,
    IsCorrect TINYINT,
    Points_ INT,
    FOREIGN KEY (GamePlayerID) REFERENCES GamePlayers(GamePlayerID) ON UPDATE CASCADE,
    FOREIGN KEY (GameQuestionID) REFERENCES GameQuestions(GameQuestionID) ON UPDATE CASCADE
);
