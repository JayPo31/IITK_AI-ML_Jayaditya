import json
import os
import hashlib

class TaskManager:
    def __init__(self, data_file="task_manager_data.json"):
        self.data_file = data_file
        self.users = {}   # {username: hashed_password}
        self.tasks = {}   # {username: [task_dicts]}
        self.current_user = None
        self.load_data()

    # --- FILE HANDLING ---
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.users = data.get("users", {})
                    self.tasks = data.get("tasks", {})
            except json.JSONDecodeError:
                print("⚠️ Storage file corrupted. Starting with an empty dataset.")
                self.users = {}
                self.tasks = {}

    def save_data(self):
        data_to_save = {"users": self.users, "tasks": self.tasks}
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4, ensure_ascii=False)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # --- AUTH ---
    def register(self):
        print("\n--- User Registration ---")
        username = input("Enter a new username: ").strip()
        if not username:
            print("❌ Username cannot be empty.")
            return
        if username in self.users:
            print("❌ Username already exists.")
            return
        password = input("Enter a password: ").strip()
        if not password:
            print("❌ Password cannot be empty.")
            return
        self.users[username] = self._hash_password(password)
        self.tasks.setdefault(username, [])
        self.save_data()
        print(f"✅ User '{username}' registered successfully!")

    def login(self):
        print("\n--- User Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        if username in self.users and self.users[username] == self._hash_password(password):
            self.current_user = username
            print(f"✅ Login successful! Welcome, {username}.")
            return True
        print("❌ Invalid username or password.")
        return False

    def logout(self):
        if self.current_user:
            print(f"\nLogging out '{self.current_user}'...")
            self.current_user = None
        else:
            print("No user currently logged in.")

    # --- TASKS ---
    def add_task(self):
        if not self.current_user:
            print("❌ You must be logged in to add tasks.")
            return
        print("\n--- Add New Task ---")
        description = input("Enter task description: ").strip()
        if not description:
            print("❌ Task description cannot be empty.")
            return
        user_tasks = self.tasks.get(self.current_user, [])
        next_id = (max((t["id"] for t in user_tasks), default=0) + 1)
        new_task = {"id": next_id, "description": description, "status": "Pending"}
        user_tasks.append(new_task)
        self.tasks[self.current_user] = user_tasks
        self.save_data()
        print(f"✅ Task #{next_id} added.")

    def view_tasks(self):
        if not self.current_user:
            print("❌ You must be logged in to view tasks.")
            return
        print("\n--- Your Tasks ---")
        user_tasks = self.tasks.get(self.current_user, [])
        if not user_tasks:
            print("📭 No tasks found.")
            return
        print(f"{'ID':<6}{'Description':<40}{'Status':<12}")
        print("-" * 60)
        for t in user_tasks:
            print(f"{t['id']:<6}{t['description'][:38]:<40}{t['status']:<12}")

    def mark_task_completed(self):
        if not self.current_user:
            print("❌ You must be logged in to modify tasks.")
            return
        try:
            tid = int(input("Enter task ID to mark completed: ").strip())
        except ValueError:
            print("❌ Invalid ID.")
            return
        user_tasks = self.tasks.get(self.current_user, [])
        for t in user_tasks:
            if t["id"] == tid:
                if t["status"].lower() == "completed":
                    print("ℹ️ Task already completed.")
                else:
                    t["status"] = "Completed"
                    self.save_data()
                    print(f"✅ Task #{tid} marked as completed.")
                return
        print("❌ Task ID not found.")

    def delete_task(self):
        if not self.current_user:
            print("❌ You must be logged in to delete tasks.")
            return
        try:
            tid = int(input("Enter task ID to delete: ").strip())
        except ValueError:
            print("❌ Invalid ID.")
            return
        user_tasks = self.tasks.get(self.current_user, [])
        for i, t in enumerate(user_tasks):
            if t["id"] == tid:
                confirm = input(f"Type 'YES' to delete task #{tid}: ").strip()
                if confirm == "YES":
                    user_tasks.pop(i)
                    self.tasks[self.current_user] = user_tasks
                    self.save_data()
                    print(f"✅ Task #{tid} deleted.")
                else:
                    print("Canceled.")
                return
        print("❌ Task ID not found.")

def main():
    mgr = TaskManager()
    while True:
        if mgr.current_user:
            print("\n--- Task Manager (logged in as: {}) ---".format(mgr.current_user))
            print("1. Add Task")
            print("2. View Tasks")
            print("3. Mark Task Completed")
            print("4. Delete Task")
            print("5. Logout")
            print("6. Exit")
            choice = input("Choose (1-6): ").strip()
            if choice == "1":
                mgr.add_task()
            elif choice == "2":
                mgr.view_tasks()
            elif choice == "3":
                mgr.mark_task_completed()
            elif choice == "4":
                mgr.delete_task()
            elif choice == "5":
                mgr.logout()
            elif choice == "6":
                print("Exiting... Goodbye!")
                break
            else:
                print("❌ Invalid choice.")
        else:
            print("\n--- Task Manager ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose (1-3): ").strip()
            if choice == "1":
                mgr.register()
            elif choice == "2":
                mgr.login()
            elif choice == "3":
                print("Exiting... Goodbye!")
                break
            else:
                print("❌ Invalid choice.")

if __name__ == "__main__":
    main()