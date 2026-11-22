# HarborWingAir
HarborWing Operations & Reservation CRUD System

A database-driven CRUD application built for HarborWing employees to manage passenger bookings, flight schedules, legs, payments, and airport records without writing raw SQL. This application connects directly to the relational MySQL database established in the HarborWing Midterm Drill, preserving all existing foreign-key relationships, constraints, and business rules.

Features

Core Entity Management (CRUD)

Full Create, Read, Update, and Delete capabilities for:

Passengers

Booking Agents

Reservations

Payments

Airports

Flight Schedules

Flight Legs

Flight Costs

Relational Linking & Views

Reservation-Payment Linking: Associate or disassociate payments with specific reservations. Removing a link preserves the underlying payment record.

Reservation-Flight Leg Linking: Attach or detach multiple flight legs to build multi-leg itineraries. Removing a link preserves the underlying flight leg record.

Unified Reservation View: Inspect a single reservation alongside its linked passenger, booking agent, attached flight legs, flight costs, and payment history.

Search & Filtering: Query and filter records across entities using targeted parameters.

Reference & Calendar Views: Read-only views for supporting reference data and calendar schedules seeded from the Midterm Drill.

Security & Data Integrity

SQL Injection Prevention: All database interactions use parameterized queries / prepared statements (or ORM equivalents).

Transaction Management: Multi-table operations (such as creating linked records or cascading updates) execute inside atomic database transactions (BEGIN / COMMIT / ROLLBACK).

Referential Integrity Protection: Deletion of referenced records (e.g., an airport actively tied to a flight schedule) is intercepted and prevented with user-friendly error explanations.

Duplicate Link Prevention: Enforces uniqueness on junction/associative records so the same payment or flight leg cannot be linked twice to the same reservation.

Input Validation & Error Handling: Validates data types, required fields, and missing record IDs prior to database execution.

Database Dependency

This application relies on the schema and synthetic dataset created in the HarborWing Midterm Drill.

Midterm Repository / Source: [Insert Link to Midterm Drill Repository or /database folder]

Database Version / Commit: [Insert Commit Hash or Release Tag, e.g., v1.0.0-midterm]

Schema Changes: None (or list any updated SQL scripts and MySQL Workbench .mwb diagrams located in the /database directory if modifications were required).

Installation

Prerequisites

Database: MySQL Server 8.0 or higher

Runtime/Environment: [Specify your language/runtime, e.g., Node.js v18+ / Python 3.11+ / PHP 8.2+ / Java 17+]

Package Manager: [Specify package manager, e.g., npm / pip / composer / maven]

Setup Steps

Clone this repository to your local machine:

git clone https://github.com/your-username/harborwing-crud-app.git
cd harborwing-crud-app


Install application dependencies:

# Replace with your stack's installation command, e.g.:
npm install
# or: pip install -r requirements.txt


Database Connection

1. Initialize the Midterm Database

Ensure your local MySQL service is running, then execute the Midterm Drill SQL scripts to build the schema and load the synthetic dataset:

mysql -u root -p < database/01_schema.sql
mysql -u root -p < database/02_seed_data.sql


(Note: If any schema updates were made for this phase, run database/03_schema_updates.sql as well.)

2. Configure Environment Credentials

Database credentials are kept outside of version control. Copy the provided example configuration file and populate it with your local MySQL credentials:

cp .env.example .env


Open .env and update the following parameters:

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=harborwing_db
DB_USER=harborwing_app_user
DB_PASSWORD=your_secure_password_here
APP_PORT=3000


(Ensure .env is listed in your .gitignore file and never committed to GitHub.)

Startup Instructions

Verify that MySQL is active and reachable using the credentials defined in .env.

Start the application server:

# Replace with your stack's start command, e.g.:
npm start
# or: python app.py


Open your browser (or launch the desktop client) and navigate to:

http://localhost:3000


Developer Guide: How Actions Map to Queries

To maintain data integrity and prevent SQL injection, user actions follow a strict layered flow:

UI / Controller Layer: Captures form input (e.g., linking a flight_leg_id to a reservation_id) and validates required fields and data types.

Service / Transaction Layer: Opens a database transaction, checks if the target reservation and flight leg exist, and verifies that the link does not already exist.

Data Access Layer (Parameterized Query): Executes a prepared statement against MySQL:

INSERT INTO reservation_flight_legs (reservation_id, flight_leg_id)
VALUES (?, ?);


Error & Commit Handling: If MySQL throws a foreign-key constraint error (errno 1452) or duplicate key error (errno 1062), the transaction rolls back and returns a clear, human-readable error message to the UI. Otherwise, the transaction commits and displays a confirmation banner.

Known Limitations

Reference & Calendar Tables: Supporting reference lookup tables and calendar records are read-only within the UI and must be updated via the Midterm Drill SQL seed/maintenance scripts.

No Cascading Force-Deletes: By design, parent records (such as Airports, Passengers, or Flight Schedules) with active child dependencies cannot be force-deleted from the UI; dependent links or child records must be removed first.

Single-Instance Authentication: Role-based user login/authentication for individual HarborWing employees is not implemented in this version; the application connects via a single configured service account.

Local Timezone Handling: Flight schedule departure and arrival timestamps are stored and displayed in the database's configured timezone without automatic passenger local-time conversion.
