from cx_Freeze import setup, Executable
import os

# Check if the Python script and icon file exist
script_path = r"C:\\home\\symbio\\Documents\\3RD YEAR\\1ST SEMESTER\\SUBJECTS\\CY1\\PC14\\ACTIVITIES\\OCTOBER\\October 23, 2024\\Spotiscrape\\gui.py"
icon_path = r"C:\\home\\symbio\\Documents\\3RD YEAR\\1ST SEMESTER\\SUBJECTS\\CY1\\PC14\\ACTIVITIES\\OCTOBER\\October 23, 2024\\Spotiscrape\\icon.ico"

assert os.path.isfile(script_path), "Python script not found!"
assert os.path.isfile(icon_path), "Icon file not found!"

# Set the base for the executable
base = None
if os.name == 'nt':
    base = "Win32GUI"  # Use "Console" if you want a console window

# Define the executables list
executables = [
    Executable(
        script_path,
        base=base,
        icon=icon_path
    )
]

# Setup function
setup(
    name="spotiscrape",
    version="1.0",
    description="Spotify Charts - Philippines Webscraper",
    options={
        "build_exe": {
            "includes": [
                "requests",
                "bs4",
                "pandas",
                "matplotlib",
                "re",
                "scikit-learn",
                "numpy",
                "tkinter",
                "customtkinter",
                "sys",
                "shutil",
                "openpyxl",  # Corrected from "openpyx" to "openpyxl"
                "datetime"    # Corrected from "ldatetime" to "datetime"
            ],
            "build_exe": "build_output"  # Specify the output build directory
        }
    },
    executables=executables
)
