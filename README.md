# HarborWingAir

Harborwing is a lightweight maritime logistics and port traffic management service designed to track vessel arrivals, berth assignments, and cargo manifests in real time.

FEATURES
Real-Time Vessel Tracking: Monitors incoming and outgoing ships via AIS data feeds.

Automated Berth Allocation: Assigns dock spaces based on vessel draft, length, and cargo type.

Cargo Manifest Management: Processes, validates, and indexes digital bills of lading.

Port Congestion Alerts: Sends automated notifications when terminal capacity exceeds 85 percent.

Role-Based Access Control: Supports distinct permissions for Harbor Masters, Dock Operators, and Customs Agents.

INSTALLATION
Ensure Python 3.11 or higher and PostgreSQL 15 or higher are installed on your host machine.

Clone the repository to your local environment:
git clone https://github.com/example/harborwing.git

Navigate into the project directory:
cd harborwing

Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate

Install the required dependencies:
pip install -r requirements.txt

DATABASE CONNECTION
Create a dedicated PostgreSQL database and user for the application:
CREATE DATABASE harborwing_db;
CREATE USER harborwing_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE harborwing_db TO harborwing_user;

Copy the example environment configuration file:
cp .env.example .env

Open the .env file and update the database connection string and secret key:
DATABASE_URL=postgresql://harborwing_user:your_secure_password@localhost:5432/harborwing_db
SECRET_KEY=replace_with_a_random_32_character_string
AIS_FEED_TIMEOUT=30

Run the initial database migrations to generate the schema:
python manage.py migrate

STARTUP INSTRUCTIONS
Start the background worker for processing incoming vessel telemetry:
python manage.py run_telemetry_worker

In a separate terminal session (with the virtual environment activated), launch the main web server:
python manage.py runserver 0.0.0.0:8080

Access the operational dashboard via your browser at http://localhost:8080.

For production deployments, serve the application using Gunicorn behind a reverse proxy such as Nginx:
gunicorn harborwing.wsgi:application --bind 0.0.0.0:8080 --workers 4

KNOWN LIMITATIONS
Offline Sync: The system requires a continuous internet connection for live AIS telemetry; cached offline playback is not yet supported.

Single-Port Scope: The current database schema supports managing one port facility per instance. Multi-port federation is planned for v2.0.

Legacy EDI Formats: Only UN/EDIFACT D95B and JSON formats are supported for cargo manifests. Older flat-file formats must be converted prior to upload.

High-Concurrency Reporting: Generating custom PDF port-activity reports for date ranges exceeding 90 days may cause temporary API latency.
