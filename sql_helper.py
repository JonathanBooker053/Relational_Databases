import mysql.connector
from mysql.connector import errorcode
import sys

DEBUG = False  # Set this to True if you want to print debug information


def get_conn(user='jbooker'):
    """
    Connects to the MySQL database and returns the connection object.
    """
    try:
        # Assuming there's a user 'jeopardy_user' who can access the 'jeopardydb' for playing the game
        conn = mysql.connector.connect(
            host='localhost',
            user=user,  # This should be either jeopardy_admin or jeopardy_client based on the role
            port='3306',  # Default port for MySQL is '3306
            password='',  # Prompt for the password or set as needed
            database="jeopardydb"
        )
        if DEBUG:
            print('Successfully connected to the database.')
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Incorrect username or password", file=sys.stderr)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist", file=sys.stderr)
        else:
            print(err, file=sys.stderr)
        sys.exit(1)


def run_sql(sql_command, params=None, fetch='all', user='jbooker'):
    """
    Executes a given SQL command (query or call to a function/UDF) with optional parameters
    using the database connection established by get_conn().

    :param sql_command: The SQL command to execute.
    :param params: A tuple of parameters for the SQL command, if any.
    :param fetch: Specifies how to fetch results ('all', 'one', or None).
    :return: The fetched results, if any, depending on the 'fetch' parameter.
    """
    global conn, cursor
    try:
        # Use get_conn() to establish database connection
        conn = get_conn()
        cursor = conn.cursor()

        # Execute the SQL command
        if params is None:
            cursor.execute(sql_command)
        else:
            cursor.execute(sql_command, params)

        # Determine how to fetch results based on the 'fetch' parameter
        if fetch == 'all':
            results = cursor.fetchall()
        elif fetch == 'one':
            results = cursor.fetchone()
        else:
            results = None

        # Commit the transaction if not a SELECT query
        if not sql_command.lower().strip().startswith('select'):
            conn.commit()

        return results
    except mysql.connector.Error as err:
        print(f"Error: {err}", file=sys.stderr)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()