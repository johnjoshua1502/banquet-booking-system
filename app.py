from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "replace_this_with_random_string_1234"
DB = "banquet.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Home ----------
@app.route("/")
def home():
    conn = get_db_connection()
    halls = conn.execute("SELECT * FROM halls").fetchall()
    conn.close()
    return render_template("home.html", halls=halls)

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        pw_hash = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                         (name, email, pw_hash))
            conn.commit()
            conn.close()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

# ---------- User Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = bool(user["is_admin"])
            flash("Logged in successfully.", "success")
            if user["is_admin"]:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

# ---------- User Dashboard ----------
@app.route("/user")
def user_dashboard():
    if not session.get("user_id"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    user_id = session["user_id"]
    conn = get_db_connection()
    bookings = conn.execute("SELECT b.*, h.name as hall_name FROM bookings b JOIN halls h ON b.hall_id=h.id WHERE b.user_id=? ORDER BY b.created_at DESC", (user_id,)).fetchall()
    conn.close()
    return render_template("user_dashboard.html", bookings=bookings)

# ---------- Book a hall ----------
@app.route("/book/<int:hall_id>", methods=["GET", "POST"])
def book(hall_id):
    # 1️⃣ Make sure user is logged in
    if not session.get("user_id"):
        flash("Please login to book a hall.", "warning")
        return redirect(url_for("login"))

    # 2️⃣ Get the hall details
    conn = get_db_connection()
    hall = conn.execute("SELECT * FROM halls WHERE id=?", (hall_id,)).fetchone()
    conn.close()

    if not hall:
        flash("Hall not found.", "danger")
        return redirect(url_for("home"))

    # 3️⃣ Handle form submission
    if request.method == "POST":
        date = request.form.get("date")
        time_slot = request.form.get("time_slot")
        guests = request.form.get("guests")

        # Read selected services (multiple checkboxes)
        services_selected = request.form.getlist("services")
        services_str = ", ".join(services_selected) if services_selected else ""

        # Validation checks
        if not date or not guests:
            flash("Please fill all required fields.", "danger")
            return render_template("book.html", hall=hall)

        try:
            guests_int = int(guests)
            if guests_int < 1:
                raise ValueError()
        except Exception:
            flash("Invalid number of guests.", "danger")
            return render_template("book.html", hall=hall)

        # 4️⃣ Insert into DB
        user_id = session["user_id"]
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO bookings (user_id, hall_id, date, time_slot, guests, services)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, hall_id, date, time_slot, guests_int, services_str)
        )
        conn.commit()
        conn.close()

        flash("Booking request submitted successfully!", "success")
        return redirect(url_for("user_dashboard"))

    # 5️⃣ Render form
    return render_template("book.html", hall=hall)


# ---------- Admin login page (same login used, but we can also have direct admin login) ----------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=? AND is_admin=1", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = True
            flash("Admin logged in.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "danger")
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html")

# ---------- Admin dashboard ----------
@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        flash("Admin access only.", "danger")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Get all bookings with joined user and hall data
    bookings = conn.execute("""
        SELECT b.*, u.name AS user_name, h.name AS hall_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN halls h ON b.hall_id = h.id
        ORDER BY b.created_at DESC
    """).fetchall()

    # Get main booking stats (total, pending, confirmed, rejected)
    stats_row = conn.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status='Confirmed' THEN 1 ELSE 0 END) AS confirmed,
            SUM(CASE WHEN status='Rejected' THEN 1 ELSE 0 END) AS rejected
        FROM bookings
    """).fetchone()

    conn.close()

    # Convert to dictionary
    stats = {
        "total": stats_row["total"],
        "pending": stats_row["pending"],
        "confirmed": stats_row["confirmed"],
        "rejected": stats_row["rejected"],
    }

    # ----------------------------
    # New section: Service statistics
    # ----------------------------
    service_counts = {}
    for booking in bookings:
        if booking["services"]:  # if services exist for this booking
            for service in booking["services"].split(","):
                service = service.strip()
                if service:
                    service_counts[service] = service_counts.get(service, 0) + 1

    stats["services"] = service_counts  # add to stats dictionary

    # ----------------------------
    # Render to template
    # ----------------------------
    return render_template("admin_dashboard.html", bookings=bookings, stats=stats)



# ---------- Admin update booking status ----------
@app.route("/admin/update/<int:booking_id>", methods=["POST"])
def admin_update(booking_id):
    if not session.get("is_admin"):
        flash("Admin access only.", "danger")
        return redirect(url_for("admin_login"))
    new_status = request.form["status"]
    conn = get_db_connection()
    conn.execute("UPDATE bookings SET status=? WHERE id=?", (new_status, booking_id))
    conn.commit()
    conn.close()
    flash("Booking updated.", "success")
    return redirect(url_for("admin_dashboard"))

# ---------- Run ----------
if __name__ == "__main__":
    # ensure DB exists
    if not os.path.exists(DB):
        print("Database missing. Run init_db.py first.")
    app.run(debug=True)