DROP PROCEDURE IF EXISTS CreateGame;
DROP PROCEDURE IF EXISTS AddCategoryToGame;
DROP PROCEDURE IF EXISTS AddPlayerToGame;
DROP PROCEDURE IF EXISTS SetGameAdmin;
DROP PROCEDURE IF EXISTS StartGame;
DROP PROCEDURE IF EXISTS AddAnswer;
DROP TRIGGER IF EXISTS UpdateAnswerWhenAsked;
DROP FUNCTION IF EXISTS GetPlayerScore;
DROP FUNCTION IF EXISTS GetWinnerUserID;
DROP FUNCTION IF EXISTS GetNewestGameID;
DROP PROCEDURE IF EXISTS ChangeGameStatus;
DROP TRIGGER IF EXISTS AfterGameUpdate;
-- Creates a new game with a specified status.
CREATE PROCEDURE CreateGame()
BEGIN
    INSERT INTO Games (DatePlayed, Status) VALUES (NOW(), 'Not Started');
END;

-- Adds a question category to a specific game.
CREATE PROCEDURE AddCategoryToGame(IN gameID_ INT, IN category_ VARCHAR(255), IN airDate_ DATE)
BEGIN
    INSERT INTO GameQuestions (GameID, QuestionID)
    SELECT gameID_, QuestionID
    FROM Questions
    WHERE Category = category_ AND AirDate = airDate_;
END;

-- Adds a player to a specified game.
CREATE PROCEDURE AddPlayerToGame(IN gameID_ INT, IN userID_ INT)
BEGIN
    INSERT INTO GamePlayers (GameID, UserID) VALUES (gameID_, userID_);
END;

-- Assigns an admin to a game.
CREATE PROCEDURE SetGameAdmin(IN gameID_ INT, IN adminUserID INT)
BEGIN
    UPDATE Games
    SET Admin = adminUserID
    WHERE GameID = gameID_;
END;

-- Starts the game by setting its status to 'Jeopardy!'.
CREATE PROCEDURE StartGame(IN gameID_ INT)
BEGIN
    UPDATE Games SET Status = 'Jeopardy!' WHERE GameID = gameID_;
END;

-- Records a player's answer to a question.
CREATE PROCEDURE AddAnswer(IN gamePlayerID_ INT, IN gameQuestionID_ INT, IN userAnswer_ TEXT, IN isCorrect_ TINYINT, IN points__ INT)
BEGIN
    INSERT INTO Answer (GamePlayerID, GameQuestionID, UserAnswer, IsCorrect, Points_) VALUES (gamePlayerID_, gameQuestionID_, userAnswer_, isCorrect_, points__);
END;

-- Updates the score of a player based on correct answers.
CREATE TRIGGER UpdateAnswerWhenAsked AFTER INSERT ON Answer
FOR EACH ROW
BEGIN
    UPDATE GameQuestions gq JOIN Answer a ON gq.GameQuestionID = a.GameQuestionID
    SET gq.HasBeenAsked = 1
    WHERE a.GameQuestionID = NEW.GameQuestionID;
END;

CREATE FUNCTION GetPlayerScore(GamePlayerIDParam INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE finalScore INT DEFAULT 0;
    -- Ensure the calculation only includes questions that have been answered (IsCorrect is not NULL)
    SELECT SUM(CASE WHEN a.IsCorrect = 1 THEN q.Value_ WHEN a.IsCorrect = 0 THEN -q.Value_ ELSE 0 END) INTO finalScore
    FROM Answer a
    JOIN GameQuestions gq ON a.GameQuestionID = gq.GameQuestionID
    JOIN Questions q ON gq.QuestionID = q.QuestionID
    WHERE a.GamePlayerID = GamePlayerIDParam;
    RETURN finalScore;
END;

CREATE FUNCTION GetWinnerUserID(gameID_ INT) RETURNS INT DETERMINISTIC
BEGIN
    DECLARE winnerID INT;
    SELECT gp.UserID INTO winnerID
    FROM GamePlayers gp
    JOIN (
        SELECT GamePlayerID, GetPlayerScore(GamePlayerID) AS Score
        FROM GamePlayers
        WHERE GameID = gameID_
    ) AS scores ON gp.GamePlayerID = scores.GamePlayerID
    ORDER BY scores.Score DESC
    LIMIT 1;
    RETURN winnerID;
END;

CREATE PROCEDURE ChangeGameStatus(IN gameID_ INT, IN newStatus VARCHAR(255))
BEGIN
    UPDATE Games SET Status = newStatus WHERE GameID = gameID_;
END;

DELIMITER $$

CREATE TRIGGER AfterGameUpdate BEFORE UPDATE ON Games
FOR EACH ROW
BEGIN
    IF NEW.Status = 'Complete' AND OLD.Status <> 'Complete' THEN
        -- Temporary table to store scores for all players in the game
        CREATE TEMPORARY TABLE IF NOT EXISTS TempGameScores (
            GamePlayerID INT,
            Score INT
        );

        -- Insert scores into the temporary table
        INSERT INTO TempGameScores (GamePlayerID, Score)
        SELECT
            a.GamePlayerID,
            SUM(CASE WHEN a.IsCorrect = 1 THEN q.Value_ ELSE -q.Value_ END) AS TotalScore
        FROM Answer a
        JOIN GameQuestions gq ON a.GameQuestionID = gq.GameQuestionID
        JOIN Questions q ON gq.QuestionID = q.QuestionID
        WHERE gq.GameID = NEW.GameID
        GROUP BY a.GamePlayerID;

        -- Find the player with the highest score
        SET @MaxScorePlayerID := (
            SELECT GamePlayerID FROM TempGameScores
            ORDER BY Score DESC LIMIT 1
        );

        -- Update the score for the player with the highest score
        UPDATE Client c
        INNER JOIN GamePlayers gp ON c.UserID = gp.UserID
        SET c.Score = c.Score + (
            SELECT Score FROM TempGameScores WHERE GamePlayerID = @MaxScorePlayerID
        )
        WHERE gp.GamePlayerID = @MaxScorePlayerID;

        -- Drop the temporary table
        DROP TEMPORARY TABLE IF EXISTS TempGameScores;
    END IF;
END$$

DELIMITER ;