import requests
import json

BASE_URL = "http://localhost:5000/timer"


def test_remind():
    response = requests.get(f"{BASE_URL}/remind")
    print("Test remind endpoint:")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_log_choice(reminder_time, choice):
    data = {
        "reminder_time": reminder_time,
        "choice": choice
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/log_choice", data=json.dumps(data), headers=headers)
    print("Test log_choice endpoint:")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}\n")


if __name__ == "__main__":
    # Test the remind endpoint
    test_remind()

    # Test the log_choice endpoint with 'delay' choice
    test_log_choice("22:00", "delay")

    # Test the log_choice endpoint with 'on-time' choice
    test_log_choice("23:00", "on-time")
