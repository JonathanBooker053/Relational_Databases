-- Loads the question data into the Questions table
LOAD DATA LOCAL INFILE 'JEOPARDY.csv' INTO TABLE Questions
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 LINES
(ShowNumber, AirDate, Round, Category, @Value_, Question, Answer)
SET Value_ = IF(@Value_ = 'None', NULL, @Value_);

-- Add the admin and client users
CALL add_user('jbooker', '1618', 'jbooker@caltech.edu');
CALL add_user('jdoe', '1234', 'jdoe@caltech.edu');
CALL add_user('blank', '0000', 'blank@caltech.edu');
CALL add_user('hovik', '1111', 'hovik@caltech.edu');
CALL add_user('vanier', '10987', 'mvanier@cms.caltech.edu');

-- Add the admin and client roles
SET @userID = (SELECT UserID FROM Users WHERE Username = 'jbooker');
CALL add_admin(@userID);
CALL add_client(@userID);
SET @userID = (SELECT UserID FROM Users WHERE Username = 'jdoe');
CALL add_client(@userID);
SET @userID = (SELECT UserID FROM Users WHERE Username = 'blank');
CALL add_client(@userID);
SET @userID = (SELECT UserID FROM Users WHERE Username = 'hovik');
CALL add_admin(@userID);
CALL add_client(@userID);
SET @userID = (SELECT UserID FROM Users WHERE Username = 'vanier');
CALL add_client(@userID);