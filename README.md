# CS121 Relational Databases Final Project

## Overview

My final project for the CS121 Relational Databases course showcases an application designed to interact with a "Jeopardy!" quiz show database. 

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.6 or later
- MySQL Server 5.7 or later
- Git (optional, for cloning the repository)

### Installation

1. **Clone the Repository (Optional):** If you have Git installed, you can clone the repository using the following command:
   ```bash
   git clone [repository-url]
   ```
   Alternatively, you can download the ZIP file of the project and extract it to your desired location.

2. **Setup Script:** Navigate to the project directory and run the setup script to install necessary dependencies, set up the MySQL database, and prepare the environment. Open your terminal or command prompt and execute:
   ```bash
   mysql
   CREATE DATABASE jeopardydb;
   USE jeopardydb;
   source setup.sql;
   source load-data.sql;
   source setup-passwords.sql;
   source setup-routines.sql;
   \q;
   ```
   This script will guide you through the installation of Python and MySQL (if not already installed), the creation of the database, and the setup of required Python packages.

### Usage

#### Admin Application

The Admin Application (`admin-app.py`) provides administrative functionalities, including database initialization and user management. To use the admin application, run:
```bash
python3 admin-app.py -u --username [your_username] -p --password [your_password]
```
* Replace `[your_username]` and `[your_password]` with your MySQL username and password, respectively.
* `--username` `-u` flags are used to specify the admin username.
* `--password` `-p` flags are used to specify the admin password.
* The admin application will prompt you to enter your admin username and password if you do not provide them as command-line arguments.
* Admins will be prompted to choose from a list of administrative functionalities:
```angular2html
  (1) - Approve Pending Games
  (2) - Add Client
  (3) - Add Admin
  (4) - Add User
  (5) - Run Custom Query (Advanced)
  (q) - Quit
```
Note: You must add a user before adding a client or admin.


When the database is first initialized, the following usernames and passwords are created:
```angular2html
    Username: jbooker
    Password: 1618
    Username: hovik
    Password: 1234
```
Use one of these admin account credentials to log in and create additional users, clients, and admins.
#### Client Application

The Client Application (`client-app.py`) allows users to query the "Jeopardy!" database and simulate quiz gameplay. To start the client application, execute:
```bash
python3 client-app.py --random -r --username -u [your_username] --password -p [your_password]
```
* Replace `[your_username]` and `[your_password]` with your MySQL username and password, respectively.
* `--random` `-r` flags are used to specify that the clients decisions when creating and playing a game will be randomized. The use of this feature is to create user data for the database.
* `--username` `-u` flags are used to specify the client username.
* `--password` `-p` flags are used to specify the client password.
* The client application will prompt you to enter your client username and password if you do not provide them as command-line arguments.
* Clients will be prompted to choose from a list of client functionalities:
```angular2html
  (1) - Play Jeopardy!
  (2) - Create a Game
  (3) - View Leaderboard
  (4) - Settings
  (q) - Quit
```
When the database is first initialized, the following client usernames and passwords are created:
```
Username: jbooker
Password: 1618

Username: jdoe
Password: 1234

Username: blank
Password: 0000

Username: hovik
Password: 1111

Username: vanier
Password: 10987
```
### Features

### Project Structure

- `admin-app.py`: Python script for administrative functionalities.
- `client-app.py`: Python script for client-side interactions, including the quiz game.
- `.sql`: Files containing SQL scripts for database setup and initial data loading.
- `README.md`: This file, containing setup instructions and project information.
- `JEOPARDY.csv`: "Jeopardy!" dataset that includes real questions. This file was modified to fit the project requirements. The link to the original dataset [here](https://www.kaggle.com/datasets/tunguz/200000-jeopardy-questions).

---