# import os
# from django.core.management import execute_from_command_line

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applovin_reports.settings')

# def main():
#     execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])

# if __name__ == "__main__":
#     main()
import os
import sys
import webbrowser

def start_django_server():
    # Set the Django settings module if needed
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_project.settings")

    # Start the Django server
    os.system("python manage.py runserver")

    # Open the browser at the app's homepage
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    start_django_server()
