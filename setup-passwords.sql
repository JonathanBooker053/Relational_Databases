DROP FUNCTION IF EXISTS make_salt;
DROP PROCEDURE IF EXISTS add_user;
DROP FUNCTION IF EXISTS authenticate;
DROP PROCEDURE IF EXISTS authenticate_client;
DROP PROCEDURE IF EXISTS change_pw;
DROP PROCEDURE IF EXISTS add_client;
DROP PROCEDURE IF EXISTS add_admin;

-- Function to generate a random salt
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;

-- Procedure to add a new user
DELIMITER $$
CREATE PROCEDURE add_user(
    IN new_username VARCHAR(20),
    IN new_password VARCHAR(64),
    IN new_email VARCHAR(255)
) NOT DETERMINISTIC
BEGIN
    DECLARE salt VARBINARY(8);
    SET salt = (SELECT make_salt(8));

    INSERT INTO Users (Username, PasswordHash, Salt, Email) 
    VALUES (new_username, SHA2(CONCAT(new_password, salt), 256), salt, new_email);
END$$
DELIMITER ;

-- Function to authenticate a user
DELIMITER !
CREATE FUNCTION authenticate(username_ VARCHAR(20), password VARCHAR(255))
RETURNS TINYINT DETERMINISTIC
BEGIN
    DECLARE pass_hash BINARY(64);
    DECLARE stored_salt VARCHAR(8);
    DECLARE user_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO user_exists FROM Users WHERE username = username_;

    IF user_exists = 0 THEN
        -- User does not exist
        RETURN 0;
    ELSE
        SELECT salt, pass_hash INTO stored_salt, pass_hash FROM Users WHERE username = username_ LIMIT 1;

        IF SHA2(CONCAT(stored_salt, password), 256) = pass_hash THEN
            -- Password matches
            RETURN 1;
        ELSE
            -- Password does not match
            RETURN 0;
        END IF;
    END IF;
END !
DELIMITER ;

-- Procedure to change a user's password
DELIMITER $$
CREATE PROCEDURE change_pw(
    IN username_ VARCHAR(20),
    IN new_password VARCHAR(255)
)
BEGIN
    -- Generate a new salt of 8 characters
    DECLARE new_salt VARCHAR(8);
    SET new_salt = (SELECT make_salt(8));
    
    -- Update the user's password hash and salt in the database
    UPDATE Users SET Salt = new_salt, PasswordHash = SHA2(CONCAT(new_salt, new_password), 256)
    WHERE username = username_;
END$$
DELIMITER ;

-- Procedure to add an existing user as a client if the user is not already a client
DELIMITER $$
CREATE PROCEDURE add_client(
    IN user_id INT
)
BEGIN
    IF NOT EXISTS (SELECT * FROM Client WHERE UserID = user_id) THEN
        INSERT INTO Client (UserID) VALUES (user_id);
    END IF;
END$$
DELIMITER ;

-- Procedure to add an existing user as an admin if the user is not already a admin
DELIMITER $$
CREATE PROCEDURE add_admin(
    IN UserID_ VARCHAR(255)
)
BEGIN
    -- Check if the user is already an admin
    IF NOT EXISTS (SELECT * FROM Admin WHERE UserID = UserID_) THEN
        INSERT INTO Admin (UserID)
        VALUES (UserID_);
    END IF;
END$$
DELIMITER ;




