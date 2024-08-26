import os
import subprocess
import sys

def run_command(command):
    """Run a shell command."""
    result = subprocess.run(command, shell=True, check=True, text=True)
    return result

def main():
    # Determine the operating system
    is_windows = os.name == 'nt'

    # Step 1: Install modules via virtual environment
    if is_windows:
        run_command("python -m venv venv")
        run_command("venv\\Scripts\\activate.bat && pip install -r requirements.txt")
    else:
        run_command("python3 -m venv venv")
        run_command("source venv/bin/activate && pip install -r requirements.txt")

    # Step 2: Set up Database
    db_name = "OneTrackV2"
    db_user = input("Enter your PostgreSQL username: ")
    db_password = input("Enter your PostgreSQL password: ")

    # Update persistence settings
    settings_file = "core/settings.py"
    with open(settings_file, 'r') as file:
        settings = file.read()

    settings = settings.replace("YOUR_DB_NAME", db_name)
    settings = settings.replace("YOUR_DB_USER", db_user)
    settings = settings.replace("YOUR_DB_PASSWORD", db_password)

    with open(settings_file, 'w') as file:
        file.write(settings)

    # Run Django migrations
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")

    # Step 3: Start the app
    run_command("python manage.py runserver")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
