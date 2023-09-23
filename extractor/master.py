import os
import subprocess

def main():
    while True:  # Keeps the loop running
        print("Welcome to the Event & Labor Management System.")
        choice = input("Would you like to manage 'Events' or 'Labor'? (Enter 'Events' or 'Labor', or 'Exit' to quit): ").strip().lower()

        if choice == 'events':
            script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'events.py')
            subprocess.run(["python", script_path])
        elif choice == 'labor':
            script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'labor.py')
            subprocess.run(["python", script_path])
        elif choice == 'exit':
            print("Exiting the system. Goodbye!")
            break  # Exits the loop and ends the program
        else:
            print("Invalid choice. Please enter 'Events' or 'Labor', or 'Exit' to quit.")

        print("\n")  # Adds a new line for readability

if __name__ == "__main__":
    main()
