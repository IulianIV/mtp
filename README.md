# MTP

The app itself will track everything I feel like keeping track of in the future.

At the moment there are several modules implemented that are still a work in progress.
1. **Budgeting app**:
   1. [x] Track Expenses;
   2. [x] Track Savings;
   3. [x] Track Revenue;
   4. Track Cards & Accounts;
   5. Reporting module Statistics & Forecasting.
2. **Micro-blog app**:
   1. Just for fun. Doesn't have any real usage.
3. **Health Tracking app**:
   1. Weight tracker;
   2. Training tracker;
   3. Strength and performance tracker.
4. **Media Collection**:
   1. Seen Movies & TV Shows;
   2. Read Books;
   3. Games played.
5. **Marketing Tools**:
   1. GTM Container Spy;
   2. Google Geolocation feed manipulator;
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
9. **Google Sheets and Excel Integrations**;
10. **E-book Manager** that connects to Calibre and sends books to kindle;
11. Besides DB backup, **export everything as CSV files** as hard backups;
    1. These could be made with the logic to export them as ready queries that when added in a DB Manager they would autopopulate everything.
12. Given a list of products and their attributes & sale date create **Related, Up and Cross-Sells** associations;
13. **Recommended products' algorithm** connected to the above sub-app.
14. **User profile** They can see blog posts, privileges etc.
15. **Marketing UTM Analyzer** based on the URLs parsed by the URL parser.
    1. a URL is parsed there and checked if you want to add it to the UTm analyzer. Upon "yes" it will get passed to a database.
    This analysis should be done only on URLs that contain UTM tags. The stats reporting for URL reports a general overview, this will be more specific.
    2. Eventually, a module that handles custom marketing parameters should be added (maybe if the user selects if a UTL is deemed as marketing

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
