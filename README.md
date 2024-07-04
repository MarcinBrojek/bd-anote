# bd-anote

#Database
#Django
#HTML
#Python

aNote is a web application designed for managing notes related to university courses. It functions as a kind of social portal with two distinct types of users: regular users (students) and authorized users (instructors). Authorized users can add new subjects and create new class blocks, as well as perform all the actions available to regular users, such as creating notes for these class blocks. The application offers the following features:

- Allows a regular user to become responsible for notes related to a specific class block.

- Enables regular users, except authorized users and at most one regular user who has gained rights to a particular note, to propose edits to notes.

---

### Set up

Run in main catalog - create environment:
```
python3 -m venv venv
pip install -r requirements.txt
source venv/bin/activate
```

Start the app:
```
./manage.py runserver
```

The database is completed with sample data - some subjects / lesson blocks.

There are also two accounts:
1. email: No@na.me password: Fly1ngDutchman (regular user - student)
2. email: Captain@lect.urer password: BlackPearl (authorized user - e.g. lecturer)

There is superuser account (access via link: 127.0.0.1:8000/admin):
username: admin password: admin

---

### App preview

---

### Vision Doc

---

### Conceptual model

---

### Logical model
