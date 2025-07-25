from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime

app = Flask(__name__)
TICKETS_FILE = "tickets.json"

app.secret_key = "super_secret_key"  # needed for session handling

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Load tickets from file
def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    return []

# Save tickets to file
def save_tickets(tickets):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        issue = request.form["issue"]
        category = request.form["category"]
        priority = request.form["priority"]
        location = request.form.get("location")

        # Auto-assign team
        if category == "Incident" and priority == "High":
            assigned_to = "Tier-2 Team"
        else:
            assigned_to = "Tier-1 Team"

        ticket = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "name": name,
            "email": email,
            "issue": issue,
            "category": category,
            "priority": priority,
            "location": location,
            "assigned_to": assigned_to,
            "status": "Open",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": ""
        }

        tickets = load_tickets()
        tickets.append(ticket)
        save_tickets(tickets)

        # 👇 This is the fix: redirect somewhere instead of reloading the form
        return redirect(url_for("index"))

    # 👇 Only GET request renders the form
    return render_template("create_ticket.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    tickets = load_tickets()

    # Filtering logic
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")
    category_filter = request.args.get("category")

    if status_filter:
        tickets = [t for t in tickets if t["status"] == status_filter]
    if priority_filter:
        tickets = [t for t in tickets if t["priority"] == priority_filter]
    if category_filter:
        tickets = [t for t in tickets if t["category"] == category_filter]

    return render_template("admin.html", tickets=tickets)

@app.route("/update/<id>", methods=["POST"])
def update_ticket(id):
    tickets = load_tickets()
    for t in tickets:
        if t["id"] == id:
            t["status"] = request.form["status"]
            t["notes"] = request.form["notes"]
            save_tickets(tickets)
            break
    return redirect(url_for("admin_dashboard"))

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_ticket(id):
    tickets = load_tickets()
    for t in tickets:
        if t["id"] == id:
            if request.method == "POST":
                t["status"] = request.form["status"]
                t["notes"] = request.form["notes"]
                t["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if t["status"] == "Resolved" else None
                save_tickets(tickets)
                return redirect(url_for("admin_dashboard"))
            return render_template("edit.html", ticket=t)
    return "Ticket not found", 404

@app.route("/dashboard")
def dashboard():
    tickets = load_tickets()
    total = len(tickets)

    # Count tickets by status
    status_counts = {"Open": 0, "In Progress": 0, "Resolved": 0}
    for t in tickets:
        status = t["status"]
        if status in status_counts:
            status_counts[status] += 1

    # Calculate average resolution time
    total_resolution_time = 0
    resolved_count = 0
    for t in tickets:
        if t["status"] == "Resolved" and "resolved_at" in t and t["resolved_at"]:
            created = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S")
            resolved = datetime.strptime(t["resolved_at"], "%Y-%m-%d %H:%M:%S")
            diff = (resolved - created).total_seconds()
            total_resolution_time += diff
            resolved_count += 1

    avg_resolution_minutes = (total_resolution_time / resolved_count / 60) if resolved_count else 0

    return render_template("dashboard.html", total=total, status_counts=status_counts, avg_time=avg_resolution_minutes)

from flask import session

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
