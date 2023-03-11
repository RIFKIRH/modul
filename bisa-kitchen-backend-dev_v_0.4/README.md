# APP NAME Backend

## Description

<b>Struktur dasar backend Bisa AI (Python Flask)</b>

Perubahan dapat dilihat pada changelog.md

## How To Use?

### NOTE:
* Never delete .gitignore files
* This backend server run with Python 3.7
* If Possible, use python virtualenvironment (Very Recommended)

###  HOW TO DEPLOY TO NEW SERVER:
* Pull this repo to new server
* Go to main application folder (folder that contain __init__.py and blueprint folder)
* Copy and paste config_git_safe.py in the same directory and change the name of copied file to config.py
* Open config.py and adjust the values to new server (config for database, url-url, etc.)
* MAKE SURE THE DATABASE IS CORRECT
* MAKE SURE THE UPLOAD FOLDER PATH IS CORRECT
* MAKE SURE THE LOGS FOLDER PATH IS CORRECT
* If upload folder use symlink to another folder create the link
* Install all needed python module/library/package (see pip_req.txt) (use python virtualenvironment if possible)
    * CREATE PYTHON VIRTUALENVIRONMENT: (If use virtualenvironment)
        * Virtualenvironment folder must start with venv_ (so it invlude in gitignore)
        * Virtualenvironment folder location is in main folder (beside Readme and changelog)
        * Create virtualenvironment with python 3.6
        * Install all needed package/library in new virtualenvironment (see pip_req.txt)
        * Run the backend server with installed virtualenvironment (Either in Apache or Nginx)
* Try to run the program
* Check upload folder structure and logs folder structure
* Test the application if work normally (test upload file too)
* Check if uploaded file in the correct directory
* Check if logs is created in the correct directory

### CRONTAB:
* Make sure all the crontab needed is installed. There is two ways to add crontab list to new server
1. Traditional way:
    * Check all crontab list from crontab -e from old server
    * Copy all crontab list to new server
    * Make sure path to the crontab file is correct

2. Script way:
    * Go to crontab folder (crontab folder now inside application folder, same folder as blueprint folder)
    * Run crontab_list_generator.py
    * If error check what python file cause the error, open the  crontab_list_generator.py and edit the crontab list
    * If not error, copy all printed string in terminal to crontab -edit
    * Make sure all crontab file is correctly installed (compare with old server is a good way to make sure :))

