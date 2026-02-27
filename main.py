import requests
import json
import threading
import time
from colorama import init, Fore, Style, Back

init(autoreset=True)

EMAILS_FILE = "emails.txt"
TOKENS_FILE = "tokens.txt"
LOCK = threading.Lock()
emails_to_make = 0
emails_created = 0
stop_flag = False
stop_lock = threading.Lock()

def save_to_files(email, token):
    with LOCK:
        with open(EMAILS_FILE, "a") as f:
            f.write(f"{email}\n")
        with open(TOKENS_FILE, "a") as f:
            f.write(f"{email}:{token}\n")

def generate_emails():
    global emails_created, stop_flag
    url = "https://api.internal.temp-mail.io/api/v3/email/new"
    payload = {
        "min_name_length": 10,
        "max_name_length": 10
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    while True:
        with stop_lock:
            if stop_flag:
                break
            if emails_created >= emails_to_make:
                stop_flag = True
                break

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                email = data.get("email")
                token = data.get("token")
                if email and token:
                    save_to_files(email, token)
                    with stop_lock:
                        if not stop_flag and emails_created < emails_to_make:
                            emails_created += 1
                            print(f"{Fore.GREEN}[+] created: {email}|{token}{Style.RESET_ALL}")
        except:
            pass

def main():
    global emails_to_make, emails_created, stop_flag

    emails_to_make = int(input("emails to make: "))
    threads_count = int(input("threads: "))

    emails_created = 0
    stop_flag = False

    with open(EMAILS_FILE, "w") as f:
        f.write("")
    with open(TOKENS_FILE, "w") as f:
        f.write("")

    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=generate_emails)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"{Fore.CYAN}[*] done! created {emails_created} emails{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
