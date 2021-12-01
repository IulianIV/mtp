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

There are several app-specific functionalities that are to be implemented for ease of usage.
1. **Data flow import & export**:
   1. Adds the functionality to import & export data from the Database.
2. **Database Manager**:
   1. Automatically backups the database at set intervals.
3. **Tester**:
   1. Clone the current app and all of its functionalities;
   2. Populate a database with fake data;
4. **Logger**:
   1. Log data coming in and out of the app using the builtin loggers.
5. **URL Shorter**;
6. **Work Tools** - such as Catalog Management and Automations;
7. **Google Sheets and Excel Integrations**;
8. **E-book Manager** that connects to Calibre and sends books to kindle;
9. Besides DB backup, **export everything as CSV files** as hard backups;
   1. These could be made with the logic to export them as ready queries that when added in a DB Manager they would autopopulate everything.
10. Given a list of products and their attributes & sale date create **Related, Up and Cross Sells** associations;
11. **Recommended products' algorithm** connected to the above sub-app.

General App Wide TODOs:
1. **Revamp the templating**:
   1. There should be a base template that contains the elements general to every app;
   2. Other templates dedicated to each app;
   3. Any other templates needed

Templating revamping is necessary to reduce cohesion and coupling. At the moment
the need to remove a button means that you have to modify almost all existing html templates.

2. Make sure **SQLAlchemy is implemented everywhere** a database connection is needed.
3. **Add permissions**. What can a standard user do and what can an admin do?
4. **Revamp the authentication logic**.
   1. User login;
   2. User logout;
   3. User forgot password;
   4. User Registering.
5. **E-mail notifications** and e-mail management (for authentication purposes and newsletters)
6. Try implementing **class abstraction and type hinting**.
