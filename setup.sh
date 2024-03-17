#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python
install_python() {
    echo 'Python not found. Attempting to install Python...'
    if command_exists brew; then
        brew install python
    elif command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install python3
    else
        echo 'Package manager not supported. Please install Python manually.'
        exit 1
    fi
}

# Function to install MySQL
install_mysql() {
    echo 'MySQL not found. Attempting to install MySQL...'
    if command_exists brew; then
        brew install mysql
        brew services start mysql
    elif command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install mysql-server
        sudo systemctl start mysql
        sudo systemctl enable mysql
    else
        echo 'Package manager not supported. Please install MySQL manually.'
        exit 1
    fi
}

# Check for Python and install if necessary
if command_exists python3; then
    echo 'Python found.'
else
    install_python
fi

# Check for MySQL and install if necessary
if command_exists mysql; then
    echo 'MySQL found.'
else
    install_mysql
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
pip3 install mysql-connector-python

echo 'Setup completed. You can now run the Python applications.'
