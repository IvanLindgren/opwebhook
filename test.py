# test.py
from main import get_all_notifications

def print_notifications():
    notifications = get_all_notifications()
    for n in notifications:
        print(f"\n--- Notification ID: {n['id']} ---")
        print(f"Event Type: {n['event_type']}")
        print(f"Created At: {n['created_at']}")
        print("Data:")
        for key, value in n['data'].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    print_notifications()