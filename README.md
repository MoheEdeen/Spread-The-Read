# Spread the Read

## Project Overview

**Spread the Read** is a web application designed to assist users in determining the appropriate grade level for a piece of text. This is particularly useful for educators who need to ensure their materials are suitable for their students' reading levels. The application employs advanced techniques, supplemented by traditional readability algorithms, to provide accurate and reliable grade level assessments.

## Features

- **Readability Analysis**: The core feature of Spread the Read is its advanced readability analysis, leveraging data from previously assessed texts to determine the grade level of new texts. This approach ensures more accurate and context-aware evaluations.

- **Backup Readability Algorithms**: In cases where the system cannot confidently assess a text, the application falls back on established readability algorithms, including:
  - Automated Readability Index
  - Gunning Fog Index
  - Flesch-Kincaid Reading Ease
  - Coleman-Liau Index

## Technology Stack

The project utilizes the following:

### Frontend

- HTML
- CSS

### Backend

- Python (Flask)

### Database

- Sqlite3

## Setup Instructions

1. **Create the Database File**:  
   Ensure that a new file named `ReadableDB.db` is created in the project directory.

2. **Install SQLite3**:  
   Verify that you have `sqlite3` installed on your system to manage and query the database.

3. **Run the Database Queries**:  
   Navigate to the file `tables.sql` and execute all the SQL queries provided in it to set up the necessary tables in the database.

4. **Run the Application**:  
   Use the following command to start the web application:
   ```bash
   flask run
   ```
