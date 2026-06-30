"""
PyMail Client — Lab 6
---------------------
Connects to the PyMail server, logs in, and lets the user interact with
their inbox via a menu.

Run:  python client.py [server-ip]
      Default server-ip is 127.0.0.1 (localhost)
"""

import socket
import sys

HOST = "localhost"
PORT = 5001

# Must match the sentinels in server.py
READY   = "__READY__"    # server wants one line of keyboard input
COMPOSE = "__COMPOSE__"  # server wants us to collect and send a full email


def compose_email(wfile):
    """
    Collect a new email from the user and send it to the server.

    The server is waiting for exactly three lines (in this order):
      Line 1 — recipient email address
      Line 2 — subject line
      Line 3 — message body

    After sending all three lines the server will reply with a
    confirmation (or error) message that the main loop will print.

    ------------------------------------------------------------------ #
    LAB EXERCISE — implement this function (client side).               #
                                                                         #
    Steps:                                                               #
      1. Prompt the user for each field:                                 #
           recipient = input("To: ")                                     #
           subject   = input("Subject: ")                                #
           body      = input("Body: ")                                   #
      2. Send each value as its own line using wfile:                    #
           wfile.write((recipient + "\n").encode())                      #
           ... (repeat for subject and body)                             #
           wfile.flush()                                                 #
    ------------------------------------------------------------------ #
    """
    # Placeholder — sends blank lines so the server does not hang.
    # Replace this entire block once you start implementing.
    print("[TODO] compose_email() is not implemented yet.")
    for _ in range(3):
        wfile.write(b"\n")
    wfile.flush()


def main():
    server_ip = sys.argv[1] if len(sys.argv) > 1 else HOST

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((server_ip, PORT))
        except ConnectionRefusedError:
            print(f"Could not connect to {server_ip}:{PORT}. Is the server running?")
            return

        # makefile() wraps the socket in file-like objects for easy line I/O
        rfile = s.makefile("rb")
        wfile = s.makefile("wb")

        while True:
            line = rfile.readline()
            if not line:
                # Server closed the connection
                break

            text = line.decode().rstrip("\n")

            if text == READY:
                # Server is waiting for one line of input
                try:
                    user_input = input()
                except EOFError:
                    break
                wfile.write((user_input + "\n").encode())
                wfile.flush()
            elif text == COMPOSE:
                # Server wants a full email — collect and send it
                compose_email(wfile)
            else:
                print(text)


if __name__ == "__main__":
    main()
