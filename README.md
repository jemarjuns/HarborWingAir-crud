# HarborWing Air CRUD System
# Project Description
HarborWing Air is a PHP and MySQL database management system for managing flight reservation records. The application connects to the harborwing_air database and provides a web interface for performing Create, Read, Update, and Delete (CRUD) operations.

# Technologies Used
PHP
MySQL
MySQL Workbench
XAMPP
HTML
CSS
Git and GitHub
Database Tables
The application manages the following tables:

passengers
booking_agents
reservations
payments
airports
flight_schedules
flight_legs
flight_costs
The system also uses reservation_legs and reservation_payments to manage relationships between reservations, flight legs, and payments.

# Features
Add new records.
View existing records.
Update existing records.
Delete records when database relationships allow deletion.
Search records by keyword.
View a reservation with its passenger and booking agent.
Link existing flight legs to a reservation.
Unlink flight legs without deleting the original flight leg records.
Link existing payments to a reservation.
Unlink payments without deleting the original payment records.
Validate selected user inputs.
Use prepared SQL statements for database operations.
Display helpful error messages for invalid or restricted operations.
Installation and Setup
Install and open XAMPP.

Start Apache and MySQL from the XAMPP Control Panel.

Open MySQL Workbench and confirm that the harborwing_air schema and its tables exist.

Copy the project folder into the XAMPP htdocs directory.

Open db.php and confirm the database host, port, username, password, and database name.

If your database has a password, use your local database password in db.php. Do not commit passwords to GitHub.

Open a browser and visit:

http://localhost/harborwingair_crud/harborwingair_crud/index.php

Test adding, viewing, editing, deleting, searching, and managing reservation relationships.

# Project Files
db.php — database connection.
index.php — CRUD pages for the eight main tables.
reservation_view.php — reservation details and payment/flight-leg relationships.
style.css — website styling.
TESTING_GUIDE.md — manual testing checklist.
.gitignore — files excluded from version control.
Database Safety
Deleting a linked record may be blocked by database foreign-key constraints. This helps protect related data. To remove a payment or flight leg from a reservation, use the Unlink function on the reservation details page instead of deleting the original record.

# Limitations
This is an educational project. Before deployment in a real environment, it should be enhanced with authentication, authorization, CSRF protection, stronger validation, and production-safe error logging.

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=harborwing_db
DB_USER=harborwing_app_user
DB_PASSWORD=your_secure_password_here
APP_PORT=3000
