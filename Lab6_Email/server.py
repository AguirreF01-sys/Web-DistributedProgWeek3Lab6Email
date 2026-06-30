"""
PyMail Server — Lab 6
---------------------
A multi-client email server.  Each connecting client identifies themselves
by email address and can view their inbox.

Users: john@email.com  |  beth@email.com

Run:  python server.py
"""

import socketserver
import threading
from datetime import date

HOST = "localhost"
PORT = 5001

VALID_USERS = {"john@email.com", "beth@email.com"}

# Sentinels the client watches for
READY   = "__READY__"    # server is waiting for one line of keyboard input
COMPOSE = "__COMPOSE__"  # client should collect a full email and send it

# ── Pre-seeded inboxes ────────────────────────────────────────────────────────

message_store = {
    "john@email.com": [
        {
            "from": "beth@email.com",
            "date": "2026-06-07",
            "subject": "Weekend plans",
            "body": "Hey John, are you free this Saturday for the hike?",
        },
        {
            "from": "beth@email.com",
            "date": "2026-06-06",
            "subject": "Project review",
            "body": "Looked over the report — great work! A few minor edits needed.",
        },
    ],
    "beth@email.com": [
        {
            "from": "john@email.com",
            "date": "2026-06-05",
            "subject": "Project report draft",
            "body": "Hey Beth, I uploaded the draft. Let me know what you think.",
        },
    ],
}

# Lock protects message_store from concurrent writes by multiple clients
store_lock = threading.Lock()


# ── Request handler ───────────────────────────────────────────────────────────

class MailHandler(socketserver.StreamRequestHandler):
    """Manages one client's session from login to logout."""

    # -- Helpers ---------------------------------------------------------------

    def write(self, text=""):
        """Send one line of text to the client."""
        self.wfile.write((text + "\n").encode())
        self.wfile.flush()

    def prompt(self, label):
        """
        Display a prompt then pause until the client sends a line back.
        The READY sentinel tells the client it is time to send input.
        """
        self.write(label)
        self.write(READY)
        return self.rfile.readline().decode().strip()

    # -- Session ---------------------------------------------------------------

    def handle(self):
        print(f"[+] Connected: {self.client_address}")
        try:
            self.write("=== PyMail ===")
            email = self.prompt("Email address: ")

            if email not in VALID_USERS:
                self.write(f"Unknown user '{email}'. Disconnecting.")
                return

            self.write(f"Welcome, {email}!")

            while True:
                self.write("")
                self.write("  1. View Inbox")
                self.write("  2. Send Email")
                self.write("  3. Quit")
                choice = self.prompt("Choice: ")

                if choice == "1":
                    self.show_inbox(email)
                elif choice == "2":
                    self.send_email(email)
                elif choice == "3":
                    self.write("Goodbye!")
                    break
                else:
                    self.write("Invalid choice — enter 1, 2, or 3.")

        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            print(f"[-] Disconnected: {self.client_address}")

    # -- Features --------------------------------------------------------------

    def show_inbox(self, email):
        with store_lock:
            inbox = list(message_store.get(email, []))

        self.write(f"\n=== Inbox: {email} ({len(inbox)} message(s)) ===")
        if not inbox:
            self.write("  (empty)")
            return

        for i, msg in enumerate(inbox, 1):
            self.write(f"\n  [{i}] From:    {msg['from']}")
            self.write(f"      Date:    {msg['date']}")
            self.write(f"      Subject: {msg['subject']}")
            self.write(f"      Body:    {msg['body']}")

    def send_email(self, sender):
        # ------------------------------------------------------------------ #
        # LAB EXERCISE — implement this method (server side).                 #
        #                                                                     #
        # Sending an email is split across two files:                         #
        #   • client.py  compose_email()  — collects the data from the user  #
        #   • server.py  send_email()     — receives and stores the message   #
        #                                                                     #
        # The COMPOSE sentinel tells the client to run compose_email().       #
        # compose_email() sends exactly three lines to the server:            #
        #   Line 1 — recipient email address                                  #
        #   Line 2 — subject                                                  #
        #   Line 3 — message body                                             #
        #                                                                     #
        # Steps:                                                              #
        #   1. Send the COMPOSE sentinel so the client starts composing.      #
        #        self.write(COMPOSE)                                          #
        #   2. Read the three lines the client sends:                         #
        #        recipient = self.rfile.readline().decode().strip()           #
        #        subject   = self.rfile.readline().decode().strip()           #
        #        body      = self.rfile.readline().decode().strip()           #
        #   3. If the recipient is not in VALID_USERS, tell the sender        #
        #      and return early.                                              #
        #   4. Build a message dict:                                          #
        #        {                                                            #
        #            "from":    sender,                                       #
        #            "date":    str(date.today()),                            #
        #            "subject": subject,                                      #
        #            "body":    body,                                         #
        #        }                                                            #
        #   5. Append it to message_store[recipient]                         #
        #      — do this inside  with store_lock:  for thread safety.         #
        #   6. Confirm to the sender that the message was delivered.          #
        # ------------------------------------------------------------------ #

        self.write(COMPOSE)

        recipient = self.rfile.readline().decode().strip()
        subject = self.rfile.readline().decode().strip()
        body = self.rfile.readline().decode().strip()

        if recipient not in VALID_USERS:
            self.write(f"Unknown user: {recipient}")
            return

        message = {
            "from": sender,
            "date": str(date.today()),
            "subject": subject,
            "body": body,
        }

        with store_lock:
            message_store[recipient].append(message)

        self.write(f"Delivered to {recipient}!")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # ThreadingTCPServer spawns a new thread for each client so john and beth
    # can be connected at the same time.
    server = socketserver.ThreadingTCPServer((HOST, PORT), MailHandler)
    server.daemon_threads = True
    print(f"[SERVER] PyMail listening on {HOST}:{PORT} ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
