# bd-anote

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

<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/5e12ff7e-82a5-45cf-9a5f-93c6726f353c">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/a9b6cb0c-3ffc-422e-8ecc-526682a4f375">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/3288c27b-8b18-4974-a474-bab79d783c4e">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/e133c3df-3afd-48db-a142-b3148f8a94a6">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/eab6d102-0a24-46b3-96a3-1ae09f5e6fee">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/896b73fd-a817-44fe-b0ba-e21438652218">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/fff8aa54-b7b4-47c3-adae-e91cb6a05cb6">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/9a46e1e9-e273-40f0-bbc6-7c30cf7edff9">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/fe0c7b82-1acc-42bc-9985-93312abaca21">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/e6dec14f-8e16-4149-b598-ef917d5fa611">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/e343e756-375a-4f1a-830f-1d00a2545f5f">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/bddc5864-b9a1-4b16-964c-dab8fc2f2918">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/730f02c5-95f1-447b-b99d-ecd2ad66bf6b">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/3a323dad-608e-4603-b723-21c9a17ddc32">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/f0f9514b-bc52-4e8d-804d-4aca341e3212">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/c4cbe4f6-f27a-4637-91be-f732ede4d388">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/cc2018e1-f953-4f8f-ac22-3d24a06fffa8">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/54a92459-7a68-450e-9f2e-ca5bef378b8c">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/3f146d62-45f1-479b-b0bc-0a07eb29f2df">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/1cc92b9b-47a1-474f-ab43-615ade382cae">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/ce06ebbd-70a4-4199-8cc5-59281392850d">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/13d995ac-e314-41ef-99f0-96a73d02a6dc">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/c3d1cf99-765c-4b73-81cd-fc9d754d5564">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/52b38c24-3c01-4bdc-a8bf-78bd22dd56e4">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/384afbf7-09f4-44ee-9ec6-cffbe6cb3d38">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/2ba1d01d-1ad3-4f0d-8c86-50cc12edcab9">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/d1cf0d74-17bc-4d57-a22d-3b62fdcc91ab">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/fe550965-5b27-498b-9d40-d9c4959bbb64">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/cda8c3df-17e6-45c3-85da-20f621466954">
<img width="15%" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/7ccf2f8f-d042-4bb4-a61e-146db853231c">

---

### Conceptual model

<img width="1155" src="https://github.com/MarcinBrojek/bd-anote/assets/73189722/413d1864-ab07-447e-8ead-cd653f1932ba">

