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
   chmod +x setup.sh
   ./setup.sh
   ```
   This script will guide you through the installation of Python and MySQL (if not already installed), the creation of the database, and the setup of required Python packages.

### Usage

#### Admin Application

The Admin Application (`admin-app.py`) provides administrative functionalities, including database initialization and user management. To use the admin application, run:
```bash
python admin-app.py --username [your_username] --password [your_password]
```

#### Client Application

The Client Application (`client-app.py`) allows users to query the "Jeopardy!" database and simulate quiz gameplay. To start the client application, execute:
```bash
python client-app.py --random --username [your_username] --password [your_password]
```

### Features

- **Database Setup and Configuration:** Automated scripts to initialize the database and configure permissions and routines.
- **Data Management:** Admin tools for managing the dataset, including updates, deletions, and reports.
- **Quiz Simulation:** A client-side application to interact with the database by playing a "Jeopardy!" styled game.

### Project Structure

- `setup.sh`: Bash script for setting up the project environment on macOS, Linux, and Windows (via WSL).
- `admin-app.py`: Python script for administrative functionalities.
- `client-app.py`: Python script for client-side interactions, including the quiz game.
- `sql_scripts/`: Directory containing SQL scripts for database setup and initial data loading.
- `README.md`: This file, containing setup instructions and project information.

## Contributing

Contributions are welcome! If you have improvements or bug fixes, please open a pull request or issue in the project repository.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- "Jeopardy!" dataset provided for educational purposes.
- CS121 Course Staff for project guidelines and support.

### Contact

For any inquiries or support, please contact [project email/contact information].

---

*Please replace placeholder texts (e.g., `[repository-url]`, `[your_username]`, `[your_password]`, `[project email/contact information]`) with actual values relevant to your project.*