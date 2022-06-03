# MTP

The app itself will track everything I feel like keeping track of in the future.

At the moment there are several modules implemented that are still a work in progress.
There are several smaller functionalities that are to be implemented for ease of usage.

# App Structure

The app is structured using Flask Factory with Blueprints for the possibility to seamlessly create new apps.
Using Blueprints also improves portability. 

The project is structured the following way:
* Project folder-
  * app folder
    * contains static, templates and app folders;
  * config file;
  * main app file which initializes the app
  * setup file;
  * readme file;
  * migrations folder
    * keeps track fo database versions;
  * instance folder
    * holds database, design and sqlite info.
* Every app itself contains:
  * An `init.py` file that contains the BluePrint initialization
  * `forms.py` file - if needed - holds form declarations;
  * `routes.py` file - logic and view functionality;
  * Any other file that is related to that certain app.
  
```bash
Project folder
├───app
│   ├───api\
│   ├───auth\
│   ├───static\
│   ├───templates\
│   └───other apps\
├───instance\
├───migrations\
├───config.py
├───app_name.py
├───setup.py
├───README.md
├───Other files...
```
