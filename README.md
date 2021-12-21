# MTP

The app itself will track everything I feel like keeping track of in the future.

At the moment there are several modules implemented that are still a work in progress.
1. **Budgeting app**:
   1. Track Expenses;
   2. Track Savings;
   3. Track Revenue;
   4. Track Cards & Accounts;
   5. Reporting module Statistics & Forecasting.
2. **Micro-blog app**:
   1. Small prototype that is a twitter clone but with some personal touches;
   2. Just for fun. Doesn't have any real usage.
3. **Health Tracking app**:
   1. Weight tracker;
   2. Training tracker;
   3. Strength and performance tracker.
4. **Media Collection**:
   1. Seen Movies and TV Shows;
   2. Seen Anime;
   3. Read Books;
   4. Games played.
5. **Marketing Tools**:
   1. GTM Container Spy;
      1. _this might end up being a module itself_.
   2. Google Geolocation feed manipulator;
      1. _an example of this was created in sheets_ (not efficient enough though).
   3. ***Others will be added***

There are several smaller functionalities that are to be implemented for ease of usage.

_Based on the difficulty of the implementation some functionalities will be implemented as modules._
1. **Data flow import & export**:
   1. Adds the functionality to import & export data from the Database.
2. **Database Manager**:
   1. Automatically backups the database at set intervals.
      1. _could end up as a module_.
3. **Tester**:
   1. Clone the current app and all of its functionalities;
   2. [x] Populate a database with fake data;
4. **Logger**:
   1. Log data coming in and out of the app using the builtin loggers.
5. **URL Shorter**;
6. [x] **URL Parser/Encode-Decode**;
7. **URL Checker**
   1. Checks a URL HTTP response;
      1. can be given a list, if list return a dictionary of URLs and their HTTP Response;
      2. if list: generate result in a copy-paste pop-up;
   2. Generate a URL Preview;
   3. Print the OpenGraph Snippet and Preview for multiple social media accounts;
      1. if chosen preview should be in a prompt;
   4. Print JSON-LD schema and the schema name, if exists.
8. **Work Tools** - such as Catalog Management and Automations;
9. **Google Sheets and Excel Integrations**;
10. **E-book Manager** that connects to Calibre and sends books to kindle;
11. Besides DB backup, **export everything as CSV files** as hard backups;
    1. These could be made with the logic to export them as ready queries that when added in a DB Manager they would autopopulate everything.
12. Given a list of products and their attributes & sale date create **Related, Up and Cross Sells** associations;
13. **Recommended products' algorithm** connected to the above sub-app.
14. **User profile** They can see blog posts, privileges etc.

General App Wide TODOs:
1. [x] **Revamp the templating**:
   1. [x] There should be a base template that contains the elements general to every app;
   2. [x] Other templates dedicated to each app;
   3. [x] Any other templates needed

Templating revamping is necessary to reduce cohesion and coupling. At the moment
the need to remove a button means that you have to modify almost all existing html templates.

2. Make sure **SQLAlchemy is implemented everywhere** a database connection is needed.
3. **Basic Multiple Users** Have databases populated with details from the currently logged-in user. Show data accordingly.
4. **Add permissions**. What can a standard user do and what can an admin do?
   1. _Admin_: Can see and do everything;
   2. _Spectator_: Can only view;
   3. _Editor_: Can't see and use unit tests, dataflow;
5. **Revamp the authentication logic**.
   1. User login;
   2. User logout;
   3. User forgot password;
   4. User Registering.
6. **E-mail notifications** and e-mail management (for authentication purposes and newsletters)
7. Try implementing **class abstraction** where necessary.
8. Add a "help me/about" section in the menu with general info.


# App Structure

The app is structured using Flask Factory with Blueprints for the possibility to seamlessly create new apps.
Using Blueprints also improves portability. 

The disadvantage is that it more than often has circular import issues.
More than often, circular imports can be fixed by not calling a package or functionality before it has been successfully loaded
(this is more likely to throw a `app out of context` error).

In certain cases (more often that necessary) imports can be added at the end of the file.
(this is not a PEP recommendation, but it is accepted when absolutely necessary)

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
```