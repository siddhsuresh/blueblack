# Library Database Management System
## CSE2004 DBMS GROUP A11 Project using Django

## Important Files to view:
* **models.py** in library folder which holds all the tables [in form of python classes] with all the relations, pls check and inform if any improvements possible
* **views.py** in library folder does almost everything for the back-end
* **urls.py** in djang_project folder informs django on what view to do to for a given url
* **admin.py** holds the code to register the models to the admin page which is used to view and change the data in the database.
* **models.sql** holds the sql commands used by django to create the database in sqlite3 [just to see]

## Capabilites till now
* Login Logout System and username in navbar
* Can view all book from the website
* Can issue and return books
* Can view all issued books
* Can view all returned book in pdf form
* Can show book copy w.r.t respective book and book w.r.t author
* To view without downloading go to https://blueblack.pythonanywhere.com

## To Test It out
* Donwload the Code
* Put the location of pip which comes with python in your computer variables path. Check youtube
* In command prompt write
  * **pip install -r requirements.txt**
  * **If the above is not working just use pip install django and pip install xhtml2pdf**
* Then go to the location where you have saved the code and in that location in command prompt use 
  * **python manage.py makemigrations**
  * **python manage.py migrate**
  * **python manage.py runserver**
* This would start the local host server at http://127.0.0.1:8000/
* Use the http://127.0.0.1:8000/admin for the admin page

## THE DATABSE 
* The databse is stored in sqlite3 format and is in **db.sqlite3** file and can be viewed in an sqlite3 IDE like https://sqliteonline.com/

