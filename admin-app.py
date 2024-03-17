"""
Student Name: Jonathan Booker
Student Email: jbooker@caltech.edu

This is the Jeopardy Game Admin Application. It allows administrators to manage Jeopardy! games and users.

To run the application, use the following command:
    python admin-app.py -u <username> -p <password>

    -u: Username for automatic login
    -p: Password for automatic login
"""

import sys
import argparse
from sql_helper import run_sql

USERNAME = None  # Placeholder for the admin's username


def parse_arguments():
    """
    Parses command-line arguments for automatic login.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Jeopardy! Admin CLI Tool')
    parser.add_argument('-u', '--username', type=str, help='Username for automatic login')
    parser.add_argument('-p', '--password', type=str, help='Password for automatic login')
    return parser.parse_args()


def username_to_id(username):
    """
    Returns the user ID for a given username.

    Args:
        username (str): The username.

    Returns:
        int: The user ID.
    """
    result = run_sql("SELECT UserID FROM Users WHERE Username = %s", (username,), user='jeopardy_admin')
    return result[0][0] if result else None


def approve_pending_games():
    """
    Allows the admin to approve pending games.
    """
    pending_games = run_sql("SELECT GameID, Status FROM Games WHERE Status = 'Pending'", user='jeopardy_admin')
    if not pending_games:
        print("No pending games to approve.")
        return

    print("Pending Games:")
    for game in pending_games:
        print(f"Game ID: {game[0]}, Status: {game[1]}")

    game_id = input("Enter Game ID to approve: ")
    run_sql("UPDATE Games SET Status = 'Complete', Winner = GetWinnerUserID(%s) WHERE GameID = %s", (game_id, game_id), user='jeopardy_admin')
    print(f"Game {game_id} approved and status set to Not Started.")


def add_client():
    """
    Adds a new client to the database.
    """
    usernames = run_sql("SELECT Username FROM Users WHERE UserID NOT IN (SELECT UserID FROM Client)", user='jeopardy_admin')

    for i, user in enumerate(usernames):
        print(f"{i + 1}. {user[0]}")
    num = int(input("Enter the number of the user you want to add as a client: "))
    username = usernames[num - 1][0]
    # You would need a stored procedure or a direct INSERT statement here
    run_sql("CALL add_client(%s)", (username_to_id(username),), user='jeopardy_admin')
    print("Client added successfully.")


def add_admin():
    """
    Adds a new admin to the database.
    """
    # Similar to add_client(), but for adding a new admin
    usernames = run_sql("SELECT Username FROM Users WHERE UserID NOT IN (SELECT UserID FROM Admin)", user='jeopardy_admin')

    for i, user in enumerate(usernames):
        print(f"{i + 1}. {user[0]}")
    num = int(input("Enter the number of the user you want to add as an admin: "))
    username = usernames[num - 1][0]
    run_sql("CALL add_admin(%s)", (username_to_id(username),), user='jeopardy_admin')
    print("Admin added successfully.")


def show_options():
    """
    Modifies the show options function to include new admin functionalities.
    """
    print("Welcome to the Jeopardy! Admin Application")
    print("Options:")
    print("  (1) - Approve Pending Games")
    print("  (2) - Add Client")
    print("  (3) - Add Admin")
    print("  (4) - Add User")
    print("  (5) - Run Custom Query (Advanced)")
    print("  (q) - Quit")
    option = input("Select an option: ")
    return option


def authenticate_user(username, password):
    """
    Authenticates a user against the 'Users' table in the database.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """
    result = run_sql("SELECT authenticate(%s, %s);", [username, password], user='jeopardy_admin')
    return bool(result[0]) if result else False


def is_admin(username):
    """
    Checks if a user is an admin.

    Args:
        username (str): The username.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    result = run_sql("SELECT u.Username, c.UserID FROM Users u JOIN Admin c ON u.UserID = c.UserID WHERE u.Username "
                     "= %s", (username,), user='jeopardy_admin')
    return bool(result) if result else False


def quit_ui():
    """
    Quits the application.
    """
    print("Thank you for playing Jeopardy! Goodbye!")
    sys.exit(0)


def log_in():
    """
    Logs in the user to the application.
    """
    while True:
        choice = input("1. Log in\n2. Quit\n")
        if choice == '2':
            quit_ui()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if authenticate_user(username, password) and is_admin(username):
            global USERNAME
            USERNAME = username
            print(f"Welcome, {USERNAME}!")
            return
        else:
            print("Invalid username or password. Please try again.")


def custom_query():
    """
    Allows the admin to run a custom query.
    """
    query = input("Enter the SQL query to run: ")
    result = run_sql(query, None, user='jeopardy_admin')
    if result:
        print("Results:")
        for row in result:
            print(row)
    else:
        print("No results returned.")


def add_user():
    """
    Adds a new user to the database.
    """
    username = input("Enter the username of the new user: ")
    password = input("Enter the password for the new user: ")
    email = input("Enter the email for the new user: ")
    run_sql("CALL add_user(%s, %s, %s)", (username, password, email), user='jeopardy_admin')


def main():
    """
    The main function that integrates new functionalities and automatic login via command-line arguments.
    """
    args = parse_arguments()

    # Automatic login if username and password are provided via command-line arguments
    if args.username and args.password:
        if authenticate_user(args.username, args.password) and is_admin(args.username):
            global USERNAME
            USERNAME = args.username
            print(f"Welcome, {USERNAME}!")
        else:
            print("Invalid username or password. Please try again.")
            sys.exit(1)
    else:
        log_in()

    while True:
        option = show_options()
        if option == '1':
            approve_pending_games()
        elif option == '2':
            add_client()
        elif option == '3':
            add_admin()
        elif option == '4':
            add_user()
        elif option == '5':
            custom_query()
        elif option.lower() == 'q':
            quit_ui()
        else:
            print("Invalid option. Please try again.")


if __name__ == '__main__':
    main()
