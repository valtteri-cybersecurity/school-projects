import subprocess
import os
import time

def clear_screen() -> None:
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "cls"], check=True)
    else:
        subprocess.run(["clear"], check=True)

def print_line():
    line = 60 * "#"
    print(line)

def print_empty_line(count_of_empty_lines: int):
    for i in range(count_of_empty_lines):
        print()

def wait_user_read():
    time.sleep(2.5)