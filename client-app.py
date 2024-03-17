"""
Student Name: Jonathan Booker
Student Email: jbooker@caltech.edu

This is the Jeopardy Game Client Application. It allows players to facilitate Jeopardy! gameplay.

To run the application, use the following command:
    python client-app.py -u <username> -p <password> -r

    -u: Username for automatic login
    -p: Password for automatic login
    -r: Enable random mode. Don't include this flag to disable random mode
"""


import sys
import argparse
from random import randint
from sql_helper import run_sql

# Debugging flag
USERNAME = None
RANDOM = False


# Add command-line argument parsing
def parse_arguments():
    """
    Parse command line arguments for the Jeopardy Game Client Application.

    Returns:
        argparse.Namespace: An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Jeopardy Game Client Application')
    parser.add_argument('-r', '--random', action='store_true', help='Enable random mode for game play')
    parser.add_argument('-u', '--username', type=str, help='Username for automatic login')
    parser.add_argument('-p', '--password', type=str, help='Password for automatic login')
    return parser.parse_args()


def authenticate_user(username, password):
    """
    Authenticates a user against the 'Users' table in the database.

    Parameters:
    - username (str): The username of the user.
    - password (str): The password of the user.

    Returns:
    - bool: True if the user is authenticated, False otherwise.
    """
    result = run_sql("SELECT authenticate(%s, %s);", [username, password], user='jeopardy_client')
    return bool(result[0]) if result else False


def username_to_id(username):
    """
    Returns the user ID for a given username.

    Parameters:
    - username (str): The username for which to retrieve the user ID.

    Returns:
    - int or None: The user ID associated with the given username, or None if no user is found.
    """
    result = run_sql("SELECT UserID FROM Users WHERE Username = %s", (username,), user='jeopardy_client')
    return result[0][0] if result else None


def create_jeopardy_game():
    """
    Creates a game of Jeopardy! in the database.

    This function creates a new game of Jeopardy! in the database. It prompts the user to enter the number of players
    and selects players from the available list. It then selects categories for each round of the game and sets an admin
    for the game. Finally, it prints a message indicating that the game has been created.

    Parameters:
        None

    Returns:
        None
    """
    run_sql("CALL CreateGame()", user='jeopardy_client')
    game = run_sql("SELECT GameID FROM Games ORDER BY DatePlayed DESC LIMIT 1")[0][0]
    num_players = 3 if RANDOM else int(input("Enter the number of players: "))
    user_i = run_sql("SELECT u.Username FROM Client c JOIN Users u ON c.UserID = u.UserID;", user='jeopardy_client')
    user_list = [user[0] for user in user_i]
    total_clients = len(user_list)
    for j in range(num_players):
        print("Available players:")
        for i, user in enumerate(user_list, start=1):
            print(f"{i}. {user}")
        print("Enter the number by the username of the player:")
        choice = randint(1, total_clients) if RANDOM else int(input())
        print("Choice: ", choice)
        username = user_list[choice - 1]
        uid = username_to_id(username)
        run_sql("CALL AddPlayerToGame(%s, %s)", (str(game), str(uid)), user='jeopardy_client')
        user_list.remove(username)
        total_clients -= 1

    rounds = ["Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"]

    for round_i in rounds:
        categories = run_sql(" SELECT DISTINCT Category, AirDate FROM Questions WHERE Round = %s;", (round_i,), user='jeopardy_client')
        category_list = [category[0] + " - " + str(category[1]) for category in categories]
        count = len(category_list)
        if round_i == "Final Jeopardy!":
            for i, category in enumerate(category_list, start=1):
                print(f"{i}. {category}")
            src = randint(1, count) if RANDOM else int(input("Select Question Category for " + round_i))
            category_string = category_list[src - 1]
            category_list.remove(category_string)
            run_sql("CALL AddCategoryToGame(%s, %s, %s)",
                    (str(game), str(categories[src - 1][0]), str(categories[src - 1][1])), user='jeopardy_client')
        else:
            for _ in range(6):
                count = len(category_list)
                for i, category in enumerate(category_list):
                    print(f"{i + 1}. {category}")
                src = randint(1, count) if RANDOM else int(input("Select Question Categories for " + round_i + ": "))
                category_string = category_list[src - 1]
                category_list.remove(category_string)
                run_sql("CALL AddCategoryToGame(%s, %s, %s)",
                        (str(game), str(categories[src - 1][0]), str(categories[src - 1][1])), user='jeopardy_client')
    admin_i = run_sql("SELECT u.Username FROM Admin a JOIN Users u ON a.UserID = u.UserID;", user='jeopardy_client')
    admin_list = [admin[0] for admin in admin_i]
    admin_count = len(admin_list)
    print("Available admins:")
    for i, admin in enumerate(admin_list, start=1):
        print(f"{i}. {admin}")
    print("Enter the number by the username of the admin:")
    choice = randint(1, admin_count) if RANDOM else int(input()) - 1
    username = admin_list[choice - 1]
    uid = username_to_id(username)
    run_sql("CALL SetGameAdmin(%s, %s)", (str(game), str(uid)), user='jeopardy_client')
    print("Game Created!")


def game_to_string(game_id):
    """
    Converts a game's information into a string representation.

    Args:
        game_id (int): The ID of the game.

    Returns:
        str: A string representation of the game, showing each player's username and score (or $0 if no score is available).
    """
    game = run_sql(
        "SELECT u.Username, GetPlayerScore(gp.GamePlayerID) FROM Users u JOIN GamePlayers gp ON u.UserID = gp.UserID "
        "WHERE gp.GameID = %s;",
        (game_id,), user='jeopardy_client')
    game_string = ""
    for player in game:
        if player[1] is not None:
            game_string += f"{player[0]}: {player[1]};\t"
        else:
            game_string += f"{player[0]}: $0;\t"
    return game_string


def get_game_status(game_id):
    """
    Returns the status of a game.

    Parameters:
    game_id (int): The ID of the game.

    Returns:
    str or None: The status of the game, or None if the game doesn't exist.
    """
    result = run_sql("SELECT Status FROM Games WHERE GameID = %s", (game_id,), user='jeopardy_client')
    return result[0][0] if result else None


def print_jeopardy_board(categories, questions, round_="Jeopardy!"):
    """
    Prints the Jeopardy! board with the given categories and questions.

    Args:
        categories (list): A list of strings representing the categories.
        questions (list): A list of tuples representing the questions. Each tuple should have the format:
                          (category, question, answer, value, answered).
        round_ (str, optional): The round of the game. Defaults to "Jeopardy!".

    Returns:
        None
    """
    # Print the categories
    header = "-" * (len(categories) * 31 + 1) + "\n|"
    for category in categories:
        header += category.center(30) + '|'
    print(header)
    point_values = [100, 200, 300, 400, 500] if round_ == "Jeopardy!" else [200, 400, 600, 800, 1000]
    # Fetch the questions for each category and print them
    for value in point_values:  # Jeopardy! values range from 200 to 1000
        print("-" * (len(categories) * 31 + 1))
        for category in categories:
            for question in questions:
                if question[0] == category and question[3] == value:
                    if not question[4]:
                        print("|" + f"${value}".center(30), end='')
                    else:
                        print("|" + " " * 30, end='')
        print("|")
    print("-" * (len(categories) * 31 + 1))


def check_all_questions_asked(game_id, round_):
    """
    Checks if all questions have been asked in a game.

    Parameters:
    - game_id (int): The ID of the game.
    - round_ (int): The round number.

    Returns:
    - bool: True if all questions have been asked, False otherwise.
    """
    total_questions = run_sql(
        "SELECT COUNT(*) FROM GameQuestions gq JOIN Questions q ON gq.QuestionID = q.QuestionID WHERE GameID = %s AND "
        "Round = %s",
        (game_id, round_), user='jeopardy_client')[0][0]
    asked_questions = run_sql(
        "SELECT COUNT(*) FROM GameQuestions gq JOIN Questions q ON gq.QuestionID = q.QuestionID WHERE GameID = %s AND "
        "Round = %s AND HasBeenAsked= %s",
        (game_id, round_, 1), user='jeopardy_client')[0][0]

    return total_questions == asked_questions


def choose_player(game_id):
    """
    Chooses a player to play the game.

    Args:
        game_id (int): The ID of the game.

    Returns:
        int: The ID of the chosen player.
    """
    players = run_sql(
        "SELECT u.Username, gp.GamePlayerID FROM Users u JOIN GamePlayers gp ON u.UserID = gp.UserID WHERE gp.GameID "
        "= %s",
        (game_id,), user='jeopardy_client')
    for i, player in enumerate(players, start=1):
        print(f"{i}. {player[0]}")
    choice = int(input("Enter the number by the player to play: ")) if not RANDOM else randint(1, len(players))
    return players[choice - 1][1]


def choose_category(categories, game_id):
    """
    Prompts the user to choose a category to play from a list of available categories.

    Args:
        categories (list): A list of available categories.
        game_id (int): The ID of the game.

    Returns:
        str: The chosen category.

    Raises:
        ValueError: If the user enters an invalid category number.

    """
    while True:
        prompt = "Enter the number by the category to play: "
        for i, category in enumerate(categories, start=1):
            prompt += f"{i}. {category}".center(20)
        src = int(input(prompt)) if not RANDOM else randint(1, len(categories))
        category = categories[src - 1]
        res = run_sql(
            "SELECT COUNT(*) FROM GameQuestions gq JOIN Questions q ON gq.QuestionID = q.QuestionID WHERE "
            "q.Category=%s AND gq.GameID=%s AND HasBeenAsked=0",
            (category, game_id), user='jeopardy_client')
        if res[0][0] > 0:
            return category
        print("No questions available for this category. Please choose another.")


def choose_value(category, game_id, round_):
    """
    Selects a value for the question to play based on the given category, game ID, and round.

    Args:
        category (str): The category of the question.
        game_id (int): The ID of the game.
        round_ (int): The round number.

    Returns:
        str: The selected value of the question to play.
    """
    values = run_sql("SELECT DISTINCT Value_ FROM Questions q JOIN GameQuestions gq ON q.QuestionID = gq.QuestionID "
                     "WHERE Category = %s AND GameID = %s AND Round = %s AND gq.HasBeenAsked = 0", (category,
                                                                                                    game_id, round_), user='jeopardy_client')
    prompt = "Enter the value of the question to play: "
    for i, value in enumerate(values, start=1):
        prompt += f"{i}. ${value[0]}".center(20)
    return values[int(input(prompt)) - 1][0] if not RANDOM else values[randint(1, len(values)) - 1][0]


def ask_question(question, game_player_id):
    """
    Asks a question to the user and records the answer.

    Args:
        question (list): A list containing the question and its details.
        game_player_id (int): The ID of the game player.

    Returns:
        None
    """
    print("Question: " + question[0][0])
    answer = input("Answer: " + question[0][1]) if not RANDOM else "Random Answer"
    is_correct = randint(0, 1) if RANDOM else 1 if int(input("Was the answer correct? 1 - Yes\t2 - No: ")) == 1 else 0
    run_sql("CALL AddAnswer(%s, %s, %s, %s, %s)",
            (game_player_id, question[0][2], answer, is_correct, int(question[0][3])), user='jeopardy_client')
    print("Answer recorded.")


def jeopardy(game_id):
    """
    Plays the Jeopardy round of the game.

    Args:
        game_id (int): The ID of the game.

    Returns:
        None
    """
    if check_all_questions_asked(game_id, "Jeopardy!"):
        run_sql("CALL ChangeGameStatus(%s,%s);", (game_id, "Double Jeopardy!"), user='jeopardy_client')
        return

    print("Choose a category to play:")
    categories = [c[0] for c in run_sql("SELECT DISTINCT q.Category "
                                        "FROM GameQuestions gq "
                                        "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                                        "WHERE q.Round = 'Jeopardy!' AND gq.GameID = %s;", (game_id,), user='jeopardy_client')]
    questions = run_sql("SELECT q.Category, q.Question, q.Answer, q.Value_, gq.HasBeenAsked "
                        "FROM GameQuestions gq "
                        "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                        "WHERE q.Round = 'Jeopardy!' AND gq.GameID = %s "
                        ";", (game_id,), user='jeopardy_client')

    print_jeopardy_board(categories, questions)
    print(game_to_string(game_id))
    game_player_id = choose_player(game_id)
    category = choose_category(categories, game_id)
    value = choose_value(category, game_id, "Jeopardy!")

    question = run_sql("SELECT q.Question, q.Answer, gq.GameQuestionID, q.Value_ "
                       "FROM GameQuestions gq "
                       "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                       "WHERE q.Category = %s AND q.Value_ = %s AND q.Round = 'Jeopardy!' AND gq.GameID = %s;",
                       (category, value, game_id), user='jeopardy_client')
    ask_question(question, game_player_id)
    play_game(game_id)


def double_jeopardy(game_id):
    """
    Play the Double Jeopardy round of the game.

    Args:
        game_id (int): The ID of the game.

    Returns:
        None
    """
    if check_all_questions_asked(game_id, "Double Jeopardy!"):
        run_sql("CALL ChangeGameStatus(%s,%s);", (game_id, "Final Jeopardy!"), user='jeopardy_client')
        return

    print("Choose a category to play:")
    categories = [c[0] for c in run_sql("SELECT DISTINCT q.Category "
                                        "FROM GameQuestions gq "
                                        "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                                        "WHERE q.Round = 'Double Jeopardy!' AND gq.GameID = %s;", (game_id,), user='jeopardy_client')]
    questions = run_sql("SELECT q.Category, q.Question, q.Answer, q.Value_, gq.HasBeenAsked "
                        "FROM GameQuestions gq "
                        "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                        "WHERE q.Round = 'Double Jeopardy!' AND gq.GameID = %s;", (game_id,), user='jeopardy_client')

    print_jeopardy_board(categories, questions, "Double Jeopardy!")
    print(game_to_string(game_id))
    game_player_id = choose_player(game_id)
    category = choose_category(categories, game_id)
    value = choose_value(category, game_id, "Double Jeopardy!")

    question = run_sql("SELECT q.Question, q.Answer, gq.GameQuestionID, q.Value_ "
                       "FROM GameQuestions gq "
                       "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                       "WHERE q.Category = %s AND q.Value_ = %s AND q.Round = 'Double Jeopardy!' AND gq.GameID = %s;",
                       (category, value, game_id), user='jeopardy_client')
    ask_question(question, game_player_id)
    play_game(game_id)


def final_jeopardy(game_id):
    """
    Runs the Final Jeopardy round for a given game.

    Args:
        game_id (int): The ID of the game.

    Returns:
        None
    """
    print("Final Jeopardy!")
    category = run_sql("SELECT DISTINCT q.Category "
                       "FROM GameQuestions gq "
                       "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                       "WHERE q.Round = 'Final Jeopardy!' AND gq.GameID = %s;", (game_id,), user='jeopardy_client')[0][0]
    print("Category: " + category)
    players = run_sql("SELECT u.Username, gp.GamePlayerID, GetPlayerScore(gp.GamePlayerID) "
                      "FROM Users u JOIN GamePlayers gp ON u.UserID = gp.UserID WHERE gp.GameID = %s", (game_id,), user='jeopardy_client')
    wagers = {}
    for player in players:
        wager = int(input(f"{player[0]}, enter your wager (0 - {player[2]}): ")) if not RANDOM else (
            randint(0, player[2])) if player[2] > 0 else 0
        wagers[player[1]] = wager
        print(f"{player[0]} wagered ${wager}.")

    question = run_sql("SELECT q.Question, q.Answer, gq.GameQuestionID "
                       "FROM GameQuestions gq "
                       "JOIN Questions q ON gq.QuestionID = q.QuestionID "
                       "WHERE q.Category = %s AND q.Round = 'Final Jeopardy!' AND gq.GameID = %s;",
                       (category, game_id), user='jeopardy_client')[0]
    print("Question: " + question[0])
    print("Answer: " + question[1])
    for player in players:
        answer = input(f"{player[0]}, write your answer: ") if not RANDOM else "Random Answer"
        is_correct = randint(0, 1) if RANDOM else 1 if int(
            input("Was the answer correct? 1 - Yes\t2 - No: ")) == 1 else 0
        run_sql("CALL AddAnswer(%s, %s, %s, %s, %s)",
        print("Answer recorded."), user='jeopardy_client')

    run_sql("CALL ChangeGameStatus(%s,%s);", (game_id, "Pending"), user='jeopardy_client')
    print("Game Complete!")
    print(game_to_string(game_id))


def play_game(game_id):
    """
    Plays a game of Jeopardy!.

    Args:
        game_id (int): The ID of the game to be played.

    Returns:
        None

    Raises:
        None
    """
    status = get_game_status(game_id)
    if status == "Complete":
        return
    elif status == "Pending":
        return
    elif status == "Not Started":
        run_sql("CALL StartGame(%s)", (game_id,), user='jeopardy_client')
        play_game(game_id)
    elif status == "Jeopardy!":
        jeopardy(game_id)
    elif status == "Double Jeopardy!":
        double_jeopardy(game_id)
    elif status == "Final Jeopardy!":
        final_jeopardy(game_id)
    else:
        print("Invalid game status.")
        return
    play_game(game_id)


def play_jeopardy():
    """
    Handles the logic for playing a game of Jeopardy!.

    This function retrieves a list of available games from the database and allows the user to choose a game to play.
    If there are no available games, it displays a message indicating that there are no games to play.
    Once a game is chosen, it calls the `play_game` function to start or continue playing the selected game.

    Parameters:
        None

    Returns:
        None
    """
    games = run_sql(
        "SELECT GameID, Status FROM Games WHERE Status != 'Complete' AND Status != 'Pending' AND Admin IS NOT NULL", user='jeopardy_client')

    if not games:
        print("No games available to play.")
        return

    print("Playing Jeopardy!")
    print("Choose a game to start or continue playing:")

    game_list = [game for game in games]
    for i, game in enumerate(game_list, start=1):
        print(f"{i}. {game_to_string(game[0])} - {game[1]}")
    print("Enter the number by the game to play:")
    choice = int(input()) - 1
    game = game_list[choice][0]
    play_game(game)


def show_options():
    """
    Displays the command-line options for the application.

    Returns:
        str: The selected option.
    """
    print("Welcome to the Jeopardy! Text UI Application")
    print("Options:")
    print("  (1) - Play Jeopardy!")
    print("  (2) - Create a Game")
    print("  (3) - View Leaderboard")
    print("  (4) - Settings")
    print("  (q) - Quit")
    option = input("Select an option: ")
    return option


def view_leaderboard():
    """
    Displays the player rankings and scores in descending order.

    This function retrieves the player rankings and scores from the database
    and prints them in the console. The rankings are based on the scores in
    descending order.

    Parameters:
        None

    Returns:
        None
    """
    print("Player Rankings")
    rankings = run_sql(
        "SELECT u.Username, Score FROM Client c Join Users u ON c.UserID = u.UserID ORDER BY Score DESC;", user='jeopardy_client')
    for i, rank in enumerate(rankings, start=1):
        print(f"{i}. {rank[0]} - ${rank[1]}")


def manage_account():
    """
    Allows the user to manage their account by providing options to change their password or go back.

    Returns:
        None
    """
    choice = input("1. Change Password\n2. Back\n")
    if choice == '1':
        new_password = input("Enter your new password: ")
        run_sql("CALL change_pw(%s, %s)", (USERNAME, new_password), user='jeopardy_client')
        print("Password changed successfully.")
        manage_account()
    elif choice == '2':
        return
    else:
        print("Invalid option. Please try again.")
        manage_account()


def quit_ui():
    """
    Prints a farewell message and exits the program.

    This function is called when the user chooses to quit the Jeopardy game.
    It prints a thank you message and then exits the program with a status code of 0.
    """
    print("Thank you for playing Jeopardy! Goodbye!")
    sys.exit(0)


def is_client(username):
    """
    Check if a user is a client.

    Args:
        username (str): The username of the user to check.

    Returns:
        bool: True if the user is a client, False otherwise.
    """
    result = run_sql("SELECT u.Username, c.UserID FROM Users u JOIN Client c ON u.UserID = c.UserID WHERE u.Username "
                     "= %s", (username,), user='jeopardy_client')
    return bool(result) if result else False


def log_in():
    """
    Prompts the user to log in by entering their username and password.
    If the authentication is successful and the user is a client, it sets the global USERNAME variable and prints a welcome message.
    If the authentication fails, it displays an error message and prompts the user to try again.
    """
    while True:
        choice = input("1. Log in\n2. Quit\n")
        if choice == '2':
            quit_ui()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if authenticate_user(username, password) and is_client(username):
            global USERNAME
            USERNAME = username
            print(f"Welcome, {USERNAME}!")
            return
        else:
            print("Invalid username or password. Please try again.")


def main():
    """
    The main function of the client application.

    This function handles the main logic of the client application. It parses command line arguments,
    authenticates the user if provided with a username and password, and presents a menu of options
    for the user to choose from. The user's choice is then processed accordingly.

    If the user is already logged in, the function shows the options menu directly. Otherwise, it prompts
    the user to log in before showing the options menu.

    Returns:
        None
    """
    args = parse_arguments()

    # Set global variables based on arguments
    global RANDOM, USERNAME
    RANDOM = args.random

    # If username and password are provided, log in automatically
    if args.username and args.password:
        if authenticate_user(args.username, args.password) and is_client(args.username):
            USERNAME = args.username
            print(f"Welcome, {USERNAME}!")
        else:
            print("Invalid username or password. Please try again.")
            sys.exit(1)

    while True:
        if USERNAME is not None:
            option = show_options()
            if option == '1':
                play_jeopardy()
            elif option == '2':
                create_jeopardy_game()
            elif option == '3':
                view_leaderboard()
            elif option == '4':
                manage_account()
            elif option.lower() == 'q':
                quit_ui()
            else:
                print("Invalid option. Please try again.")
        else:
            log_in()


if __name__ == '__main__':
    main()
