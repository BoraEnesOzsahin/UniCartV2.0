# UniCart — University Marketplace

## Table of Contents

* [🎯 About the Project]
* [✨ Features]
* [🏗️ App Structure]
* [🔧 Technologies]
* [⚙️ Setup & Installation]
* [🔗 Key URLs]

---

## About the Project

**UniCart** is a robust Django-based web application specifically designed for university students to buy and sell secondhand items. By providing a centralized campus marketplace, UniCart helps students save money, reduce waste, and build a stronger community.

### Core Objectives

* **Operational Efficiency:** Streamlined listing process for students on the go.
* **Campus Safety:** Secure authentication and profile management.
* **Accessibility:** User-friendly interface for browsing and posting items.
* **Sustainability:** Encouraging the circular economy within the university ecosystem.

---

## Features

### 📦 Listings Management (`listings/`)

* **Full CRUD Functionality:** Post, view, update, and delete your items with ease.
* **Item Discovery:** Browse all available listings in a centralized feed.
* **Visual Gallery:** Support for item images to increase trust and interest.

### 👤 User Management (`users/`)

* **Authentication:** Secure Sign-up and Login systems.
* **Profiles:** Personal user profiles to build credibility.
* **Personal Dashboard:** A dedicated space to track "My Items" and sales status.

### 📧 Communication & Security

* **Email Verification:** Integrated SMTP support for real-world email confirmation.
* **Fallback Backend:** Automatic console-based email logging for development environments without SMTP.
* **Admin Control:** Powerful administrative panel for platform moderation.

---

## App Structure

The project is divided into specialized modules to ensure scalability and clean code:

* **`listings/`**: Handles the core marketplace logic, including item categories, CRUD operations, and the browsing feed.
* **`users/`**: Manages user lifecycle, including authentication, registration, and the personal user dashboard.

---

## Technologies

* **Backend Framework:** Django (Python)
* **Environment Management:** Python Virtual Environments (`venv`)
* **Database:** Default SQLite (Development) / Compatible with PostgreSQL
* **Authentication:** Django Auth System
* **Environment Variables:** `python-dotenv` for sensitive configuration
* **Email Services:** SMTP Integration (Outlook/Custom)

---

## Setup & Installation

### Prerequisites

* Python 3.8 or higher
* Pip (Python package manager)

### Quick Start Guide

1. **Clone & Navigate**
```bash
git clone https://github.com/BoraEnesOzsahin/UniCartV2.0.git
cd UniCartV2.0

```


2. **Environment Setup**
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on Mac/Linux:
source venv/bin/activate

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Configuration**
* Create a `.env` file from `.env.example`.
* Fill in your SMTP credentials for email verification.


5. **Database Initialization**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

```


6. **Launch**
```bash
python manage.py runserver
# Access at http://127.0.0.1:8000/

```



---

## Key URLs

| Page | URL Path | Description |
| --- | --- | --- |
| **Home** | `/` | Landing page and featured items |
| **Browse** | `/listings/` | View all items for sale |
| **Post Item** | `/listings/create/` | Create a new advertisement |
| **Sign Up** | `/users/register/` | Create a new student account |
| **Login** | `/users/login/` | Access your account |
| **Dashboard** | `/users/dashboard/` | Manage your own listings |
| **Admin** | `/admin/` | Platform administration |

---

## Development Team
This project was developed by

* Bora Enes Özşahin
* Azra Sağdıç
