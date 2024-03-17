-- This will give you a list of all users and their score, ordered by the score. If the score is the same, it will order by the username.
SELECT 
    Users.Username,
    Client.Score
FROM 
    Users
LEFT JOIN Client ON Users.UserID = Client.UserID
ORDER BY 
    Client.Score DESC, Users.Username;

-- Calculate the proportion of correctly answered questions for each player across all games
SELECT 
    Users.Username,
    COUNT(Answer.GameQuestionID) AS TotalQuestions,
    SUM(Answer.IsCorrect) AS CorrectAnswers,
    (SUM(Answer.IsCorrect) / COUNT(Answer.GameQuestionID)) * 100 AS ProportionCorrect
FROM 
    Users
JOIN GamePlayers ON Users.UserID = GamePlayers.UserID
JOIN Answer ON GamePlayers.GamePlayerID = Answer.GamePlayerID
GROUP BY 
    Users.Username
ORDER BY 
    ProportionCorrect DESC, Users.Username;

-- Find the highest scoring client for each game
SELECT 
    Games.GameID,
    Users.Username,
    MAX(Client.Score) AS HighestScore
FROM 
    Games
JOIN GamePlayers ON Games.GameID = GamePlayers.GameID
JOIN Client ON GamePlayers.UserID = Client.UserID
JOIN Users ON Client.UserID = Users.UserID
GROUP BY 
    Games.GameID
ORDER BY 
    HighestScore DESC;

-- Update the score of each clientUPDATE Client
UPDATE Client 
JOIN (
    SELECT 
        gp.UserID,
        MAX(game_score) AS max_score
    FROM (
        SELECT 
            GamePlayers.UserID,
            GamePlayers.GameID,
            SUM(CASE WHEN Answer.IsCorrect = 1 THEN CAST(Questions.Value AS SIGNED) ELSE 0 END) AS game_score
        FROM GamePlayers
        JOIN Answer ON GamePlayers.GamePlayerID = Answer.GamePlayerID
        JOIN Questions ON Answer.GameQuestionID = Questions.QuestionID
        JOIN Games ON GamePlayers.GameID = Games.GameID
        WHERE Games.Admin IS NOT NULL
        GROUP BY GamePlayers.GameID, GamePlayers.UserID
    ) AS gp
    GROUP BY gp.UserID
) AS max_scores ON Client.UserID = max_scores.UserID
SET Client.Score = max_scores.max_score;

-- Retrieves the set of questions for a particular game and round, ordered by the sequence they should be asked
SELECT 
    Questions.QuestionID,
    Questions.Question,
    Questions.Answer,
    Questions.Value,
    Questions.Category,
    Questions.Round,
    Questions.AirDate
FROM 
    Questions
JOIN Answer ON Questions.QuestionID = Answer.GameQuestionID
JOIN GamePlayers ON Answer.GamePlayerID = GamePlayers.GamePlayerID
JOIN Games ON GamePlayers.GameID = Games.GameID
WHERE 
    Games.GameID = 1 AND Questions.Round = 'Jeopardy!'
ORDER BY 
    Questions.AirDate, Questions.QuestionID;


-- Retrieves the set of questions for a particular game and round.
SELECT
    Question, Answer, Value, Category, Round
FROM
    Questions
JOIN GameQuestions ON Questions.QuestionID = GameQuestions.QuestionID
WHERE
    GameID = 43 AND Round = 'Jeopardy!';

