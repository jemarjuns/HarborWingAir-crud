import os
import flask # type: ignore
import mysql.connector # pyright: ignore[reportMissingImports]
from db import get_db_connection, format_db_error

app = flask.Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Entity configurations mapped to your Midterm Drill schema
ENTITIES = {
    "passengers": {
        "title": "Passengers",
        "pk": "passenger_id",
        "columns": ["first_name", "last_name", "email", "phone"],
        "types": {"first_name": "text", "last_name": "text", "email": "email", "phone": "text"}
    },
    "booking_agents": {
        "title": "Booking Agents",
        "pk": "agent_id",
        "columns": ["agent_name", "agency_name", "email"],
        "types": {"agent_name": "text", "agency_name": "text", "email": "email"}
    },
    "reservations": {
        "title": "Reservations",
        "pk": "reservation_id",
        "columns": ["passenger_id", "agent_id", "reservation_date", "status"],
        "types": {"passenger_id": "number", "agent_id": "number", "reservation_date": "date", "status": "text"}
    },
    "payments": {
        "title": "Payments",
        "pk": "payment_id",
        "columns": ["amount", "payment_date", "payment_method", "status"],
        "types": {"amount": "number", "payment_date": "date", "payment_method": "text", "status": "text"}
    },
    "airports": {
        "title": "Airports",
        "pk": "airport_code",
        "manual_pk": True,  # e.g., 'MNL', 'PPS'
        "columns": ["airport_code", "airport_name", "city", "country"],
        "types": {"airport_code": "text", "airport_name": "text", "city": "text", "country": "text"}
    },
    "flight_schedules": {
        "title": "Flight Schedules",
        "pk": "schedule_id",
        "columns": ["flight_number", "origin_airport", "destination_airport", "departure_time", "arrival_time"],
        "types": {"flight_number": "text", "origin_airport": "text", "destination_airport": "text", "departure_time": "text", "arrival_time": "text"}
    },
    "flight_legs": {
        "title": "Flight Legs",
        "pk": "leg_id",
        "columns": ["schedule_id", "flight_date", "leg_number", "aircraft_code"],
        "types": {"schedule_id": "number", "flight_date": "date", "leg_number": "number", "aircraft_code": "text"}
    },
    "flight_costs": {
        "title": "Flight Costs",
        "pk": "cost_id",
        "columns": ["schedule_id", "cabin_class", "base_fare", "currency"],
        "types": {"schedule_id": "number", "cabin_class": "text", "base_fare": "number", "currency": "text"}
    }
}

# 1. HOME: Dashboard, Search/Filter, & Supporting Calendar Reference Records
@app.route("/")
def index():
    q = flask.request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Search reservations by passenger name or status
        if q:
            like_q = f"%{q}%"
            cursor.execute("""
                SELECT r.reservation_id, r.reservation_date, r.status,
                       p.first_name, p.last_name, a.agent_name
                FROM reservations r
                JOIN passengers p ON r.passenger_id = p.passenger_id
                LEFT JOIN booking_agents a ON r.agent_id = a.agent_id
                WHERE p.first_name LIKE %s OR p.last_name LIKE %s OR r.status LIKE %s
                ORDER BY r.reservation_id DESC
            """, (like_q, like_q, like_q))
        else:
            cursor.execute("""
                SELECT r.reservation_id, r.reservation_date, r.status,
                       p.first_name, p.last_name, a.agent_name
                FROM reservations r
                JOIN passengers p ON r.passenger_id = p.passenger_id
                LEFT JOIN booking_agents a ON r.agent_id = a.agent_id
                ORDER BY r.reservation_id DESC LIMIT 20
            """)
        reservations = cursor.fetchall()

        # Supporting Reference Records (Read-Only Calendar View)
        cursor.execute("SELECT * FROM calendar ORDER BY calendar_date ASC LIMIT 30")
        calendar_rows = cursor.fetchall()
    except mysql.connector.Error as e:
        flask.flash(format_db_error(e), "danger")
        reservations, calendar_rows = [], []
    finally:
        cursor.close()
        conn.close()

    return flask.render_template("index.html", entities=ENTITIES, reservations=reservations, calendar_rows=calendar_rows, q=q)

# 2. GENERIC CRUD: Read + Create for all 8 Entities
@app.route("/manage/<entity>", methods=["GET", "POST"])
def manage_entity(entity):
    if entity not in ENTITIES:
        flask.flash("Invalid entity requested.", "danger")
        return flask.redirect(flask.url_for("index"))

    meta = ENTITIES[entity]
    pk = meta["pk"]
    cols = meta["columns"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # CREATE
    if flask.request.method == "POST":
        values = [flask.request.form.get(col, "").strip() for col in cols]
        if any(v == "" for v in values):
            flask.flash("All fields are required. Please check your input.", "warning")
        else:
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            sql = f"INSERT INTO {entity} ({col_names}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, tuple(values))
                conn.commit()
                flask.flash(f"Successfully created record in {meta['title']}.", "success")
                return flask.redirect(flask.url_for("manage_entity", entity=entity))
            except mysql.connector.Error as e:
                conn.rollback()
                flask.flash(format_db_error(e), "danger")

    # READ (with optional filter)
    filter_val = flask.request.args.get("filter", "").strip()
    try:
        if filter_val:
            where_clause = " OR ".join([f"CAST({c} AS CHAR) LIKE %s" for c in cols])
            params = tuple([f"%{filter_val}%"] * len(cols))
            cursor.execute(f"SELECT * FROM {entity} WHERE {where_clause}", params)
        else:
            cursor.execute(f"SELECT * FROM {entity}")
        rows = cursor.fetchall()
    except mysql.connector.Error as e:
        flask.flash(format_db_error(e), "danger")
        rows = []
    finally:
        cursor.close()
        conn.close()

    return flask.render_template("crud.html", entity=entity, meta=meta, rows=rows, filter_val=filter_val, edit_row=None, entities=ENTITIES)

# 3. GENERIC CRUD: Update
@app.route("/manage/<entity>/edit/<record_id>", methods=["GET", "POST"])
def edit_entity(entity, record_id):
    if entity not in ENTITIES:
        return flask.redirect(flask.url_for("index"))

    meta = ENTITIES[entity]
    pk = meta["pk"]
    cols = [c for c in meta["columns"] if c != pk]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if flask.request.method == "POST":
        values = [flask.request.form.get(col, "").strip() for col in cols]
        if any(v == "" for v in values):
            flask.flash("Validation error: All fields must be filled.", "warning")
        else:
            set_clause = ", ".join([f"{c} = %s" for c in cols])
            sql = f"UPDATE {entity} SET {set_clause} WHERE {pk} = %s"
            try:
                cursor.execute(sql, tuple(values + [record_id]))
                if cursor.rowcount == 0:
                    flask.flash("Record not found or no changes made.", "warning")
                else:
                    conn.commit()
                    flask.flash(f"Updated {meta['title']} record #{record_id}.", "success")
                return flask.redirect(flask.url_for("manage_entity", entity=entity))
            except mysql.connector.Error as e:
                conn.rollback()
                flask.flash(format_db_error(e), "danger")

    cursor.execute(f"SELECT * FROM {entity} WHERE {pk} = %s", (record_id,))
    edit_row = cursor.fetchone()
    if not edit_row:
        cursor.close()
        conn.close()
        flask.flash(f"Record #{record_id} does not exist.", "danger")
        return flask.redirect(flask.url_for("manage_entity", entity=entity))

    cursor.execute(f"SELECT * FROM {entity}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return flask.render_template("crud.html", entity=entity, meta=meta, rows=rows, filter_val="", edit_row=edit_row, entities=ENTITIES)

# 4. GENERIC CRUD: Safe Delete
@app.route("/manage/<entity>/delete/<record_id>", methods=["POST"])
def delete_entity(entity, record_id):
    if entity not in ENTITIES:
        return flask.redirect(flask.url_for("index"))

    meta = ENTITIES[entity]
    pk = meta["pk"]
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {entity} WHERE {pk} = %s", (record_id,))
        if cursor.rowcount == 0:
            flask.flash("Record not found; nothing deleted.", "warning")
        else:
            conn.commit()
            flask.flash(f"Safely deleted record #{record_id} from {meta['title']}.", "success")
    except mysql.connector.Error as e:
        conn.rollback()
        # Triggers cleanly when FK constraint blocks deleting referenced Airport/Passenger/etc.
        flask.flash(format_db_error(e), "danger")
    finally:
        cursor.close()
        conn.close()
    return flask.redirect(flask.url_for("manage_entity", entity=entity))

# 5. VIEW COMPLETE RESERVATION & RELATED LINKS
@app.route("/reservations/<int:res_id>")
def reservation_detail(res_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, p.first_name, p.last_name, p.email, a.agent_name
            FROM reservations r
            JOIN passengers p ON r.passenger_id = p.passenger_id
            LEFT JOIN booking_agents a ON r.agent_id = a.agent_id
            WHERE r.reservation_id = %s
        """, (res_id,))
        reservation = cursor.fetchone()
        if not reservation:
            flask.flash(f"Reservation #{res_id} not found.", "danger")
            return flask.redirect(flask.url_for("index"))

        # Linked Flight Legs
        cursor.execute("""
            SELECT fl.*, fs.flight_number, fs.origin_airport, fs.destination_airport
            FROM reservation_legs rl
            JOIN flight_legs fl ON rl.leg_id = fl.leg_id
            JOIN flight_schedules fs ON fl.schedule_id = fs.schedule_id
            WHERE rl.reservation_id = %s
        """, (res_id,))
        linked_legs = cursor.fetchall()

        # Linked Payments
        cursor.execute("""
            SELECT pay.*
            FROM reservation_payments rp
            JOIN payments pay ON rp.payment_id = pay.payment_id
            WHERE rp.reservation_id = %s
        """, (res_id,))
        linked_payments = cursor.fetchall()

        # Dropdown options for linking
        cursor.execute("SELECT fl.leg_id, fs.flight_number, fl.flight_date FROM flight_legs fl JOIN flight_schedules fs ON fl.schedule_id = fs.schedule_id")
        all_legs = cursor.fetchall()

        cursor.execute("SELECT * FROM payments")
        all_payments = cursor.fetchall()

    except mysql.connector.Error as e:
        flask.flash(format_db_error(e), "danger")
        return flask.redirect(flask.url_for("index"))
    finally:
        cursor.close()
        conn.close()

    return flask.render_template(
        "reservation_detail.html",
        reservation=reservation,
        linked_legs=linked_legs,
        linked_payments=linked_payments,
        all_legs=all_legs,
        all_payments=all_payments,
        entities=ENTITIES
    )

# 6. LINK FLIGHT LEG (Prevents duplicates via composite PK / explicit check)
@app.route("/reservations/<int:res_id>/link-leg", methods=["POST"])
def link_leg(res_id):
    leg_id = flask.request.form.get("leg_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Explicit duplicate check before insert
        cursor.execute("SELECT 1 FROM reservation_legs WHERE reservation_id = %s AND leg_id = %s", (res_id, leg_id))
        if cursor.fetchone():
            flask.flash(f"Flight Leg #{leg_id} is already linked to Reservation #{res_id}.", "warning")
            return flask.redirect(flask.url_for("reservation_detail", res_id=res_id))

        cursor.execute("INSERT INTO reservation_legs (reservation_id, leg_id) VALUES (%s, %s)", (res_id, leg_id))
        conn.commit()
        flask.flash(f"Linked Flight Leg #{leg_id} to Reservation #{res_id}.", "success")
    except mysql.connector.Error as e:
        conn.rollback()
        flask.flash(format_db_error(e), "danger")
    finally:
        cursor.close()
        conn.close()
    return flask.redirect(flask.url_for("reservation_detail", res_id=res_id))

# 7. UNLINK FLIGHT LEG (Removes junction row ONLY; does NOT delete flight_legs row)
@app.route("/reservations/<int:res_id>/unlink-leg/<int:leg_id>", methods=["POST"])
def unlink_leg(res_id, leg_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservation_legs WHERE reservation_id = %s AND leg_id = %s", (res_id, leg_id))
        conn.commit()
        flask.flash(f"Unlinked Flight Leg #{leg_id} from Reservation #{res_id} (Flight Leg record preserved).", "info")
    except mysql.connector.Error as e:
        conn.rollback()
        flask.flash(format_db_error(e), "danger")
    finally:
        cursor.close()
        conn.close()
    return flask.redirect(flask.url_for("reservation_detail", res_id=res_id))

# 8. TRANSACTIONAL: Create Payment AND Link to Reservation atomically
@app.route("/reservations/<int:res_id>/create-and-link-payment", methods=["POST"])
def create_and_link_payment(res_id):
    amount = flask.request.form.get("amount", "").strip()
    payment_date = flask.request.form.get("payment_date", "").strip()
    payment_method = flask.request.form.get("payment_method", "").strip()
    status = flask.request.form.get("status", "Completed").strip()

    if not amount or float(amount) <= 0 or not payment_date:
        flask.flash("Payment amount must be greater than 0 and date is required.", "warning")
        return flask.redirect(flask.url_for("reservation_detail", res_id=res_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Multi-statement transaction: both succeed or both roll back
        cursor.execute(
            "INSERT INTO payments (amount, payment_date, payment_method, status) VALUES (%s, %s, %s, %s)",
            (amount, payment_date, payment_method, status)
        )
        new_payment_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO reservation_payments (reservation_id, payment_id) VALUES (%s, %s)",
            (res_id, new_payment_id)
        )
        conn.commit()
        flask.flash(f"Created Payment #{new_payment_id} and linked it to Reservation #{res_id}.", "success")
    except mysql.connector.Error as e:
        conn.rollback()
        flask.flash(format_db_error(e), "danger")
    finally:
        cursor.close()
        conn.close()
    return flask.redirect(flask.url_for("reservation_detail", res_id=res_id))

# 9. UNLINK PAYMENT (Removes junction row ONLY; does NOT delete payments row)
@app.route("/reservations/<int:res_id>/unlink-payment/<int:payment_id>", methods=["POST"])
def unlink_payment(res_id, payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservation_payments WHERE reservation_id = %s AND payment_id = %s", (res_id, payment_id))
        conn.commit()
        flask.flash(f"Unlinked Payment #{payment_id} from Reservation #{res_id} (Payment record preserved).", "info")
    except mysql.connector.Error as e:
        conn.rollback()
        flask.flash(format_db_error(e), "danger")
    finally:
        cursor.close()
        conn.close()
    return flask.redirect(flask.url_for("reservation_detail", res_id=res_id))

if __name__ == "__main__":
    app.run(debug=True)