#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}


# Check for Python and install if necessary
if command_exists python3; then
    echo 'Python found.'
else
    echo "Python not found. Please install Python 3 before proceeding."
fi

# Check for MySQL and install if necessary
if command_exists mysql; then
    echo 'MySQL found.'
else
    echo "MySQL not found. Please install MySQL before proceeding."
fi

# Continue with the rest of the setup
echo 'Continuing with database setup and Python package installation...'

# Setup database and install Python packages as per the previous instructions
# Prompt for MySQL username and password
read -p 'Enter your MySQL username: ' mysql_username
read -sp 'Enter your MySQL password: ' mysql_password
echo

# Define MySQL database name
database_name="jeopardy_db"

# Setup MySQL database (execute SQL scripts)
echo 'Setting up MySQL database...'
mysql -u "$mysql_username" -p"$mysql_password" -e "CREATE DATABASE IF NOT EXISTS $database_name;"
mysql -u "$mysql_username" -p"$mysql_password" $database_name < setup.sql
mysql -u "$mysql_username" -p"$mysql_password" $database_name < set-permissions.sql
mysql -u "$mysql_username" -p"$mysql_password" $database_name < setup-passwords.sql
mysql -u "$mysql_username" -p"$mysql_password" $database_name < setup-routines.sql
mysql -u "$mysql_username" -p"$mysql_password" $database_name < load-data.sql
echo 'Database setup completed.'

# Install Python dependencies
echo 'Installing Python dependencies...'
pip3 install argparse mysql mysql-connector-python

echo 'Setup completed. You can now run the Python applications.'
