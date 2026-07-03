# 🎬 Horizon Cinema Management System

A desktop cinema management system developed in **Python**, **Tkinter**, and **MySQL** that supports daily cinema operations through dedicated interfaces for **Staff**, **Administrators**, and **Managers**.

The application provides role-based access control, movie management, customer bookings, reporting, and cinema administration within a single system.

---

## ✨ Features

### 👤 Staff

- Secure login
- Browse available movies
- View showtimes
- Register new customers
- Book cinema tickets
- View available seats
- Generate booking receipts
- Cancel future bookings

### 🛠️ Administrator

- Add, edit and remove movies
- Manage showtimes
- Assign movies to cinema screens
- Generate booking reports
- Generate revenue reports

### 👔 Manager

- Add new cinemas
- Create staff and administrator accounts
- Manage multiple cinema locations
- Access administrator functionality
- View management reports

---

## 🛠️ Technologies Used

- Python
- Tkinter
- MySQL
- mysql-connector-python
- bcrypt

---

## 📂 Project Structure

```text
horizon-cinema-management-system/
│
├── src/
│   └── app.py
│
├── database/
│   └── Dump20250427.sql
│
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/amrrelbassiouni-ai/horizon-cinema-management-system.git
cd horizon-cinema-management-system
```

Install the required package:

```bash
pip install -r requirements.txt
```

Create a MySQL database named:

```
hcinema
```

Import:

```
database/Dump20250427.sql
```

Open:

```
src/app.py
```

Update the database connection:

```python
host="localhost"
user="root"
passwd="YOUR_MYSQL_PASSWORD"
database="hcinema"
```

Run the application:

```bash
python src/app.py
```

---

## 🔑 Default Login Accounts

### Staff

| City | Username | Password |
|------|----------|----------|
| Bristol | maro | 11 |
| London | m2248 | 11 |
| Cardiff | mivida | 11 |
| Birmingham | amr | 11 |

### Administrator

| City | Username | Password |
|------|----------|----------|
| Bristol | mady | 11 |
| London | maro | 11 |
| Cardiff | mivida | 11 |
| Birmingham | amr | 11 |

### Manager

| Username | Password |
|----------|----------|
| mady | 11 |

---

## 📝 Notes

- This application requires a local MySQL server.
- Import the provided SQL database before running the application.
- Update the database connection settings in `src/app.py` to match your local MySQL configuration.

---

## 📚 About

This project was developed as part of a university software development module and is shared for portfolio purposes to demonstrate experience with desktop application development, database integration, role-based access control, and object-oriented programming using Python.