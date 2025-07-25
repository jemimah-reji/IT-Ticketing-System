import json
import os
from datetime import datetime

TICKETS_FILE = "tickets.json"

# Load tickets from file if exists
def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    return []

# Save tickets to file
def save_tickets(tickets):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

# Create a new ticket
def create_ticket():
    name = input("Enter your name: ")
    issue = input("Describe the issue: ")
    ticket = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "name": name,
        "issue": issue,
        "status": "open",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tickets.append(ticket)
    save_tickets(tickets)
    print("✅ Ticket created successfully!")

# View all tickets
def view_tickets():
    if not tickets:
        print("No tickets found.")
        return
    for t in tickets:
        print(f"\nID: {t['id']}\nUser: {t['name']}\nIssue: {t['issue']}\nStatus: {t['status']}\nTime: {t['timestamp']}\n")

# Mark a ticket as resolved
def resolve_ticket():
    ticket_id = input("Enter ticket ID to resolve: ")
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "resolved"
            save_tickets(tickets)
            print("✅ Ticket marked as resolved.")
            return
    print("❌ Ticket ID not found.")

# Main Menu
tickets = load_tickets()

while True:
    print("\n--- IT Support Ticketing System ---")
    print("1. Create Ticket")
    print("2. View Tickets")
    print("3. Resolve Ticket")
    print("4. Exit")

    choice = input("Choose an option (1-4): ")

    if choice == "1":
        create_ticket()
    elif choice == "2":
        view_tickets()
    elif choice == "3":
        resolve_ticket()
    elif choice == "4":
        print("👋 Exiting...")
        break
    else:
        print("❌ Invalid choice.")
