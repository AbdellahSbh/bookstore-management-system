# Book Inventory Management System

This project is a comprehensive digital representation system for a bookstore's book inventory management system, allowing for the management of books.

## Project Overview

The Virtual Safari system is designed to be a web application ran by using commands in the URL bar.
- Python (Django) backend for business logic
- SQLite database for data storage

## Project Overview

Abdellah Sabhi

Laurent Bialylew

## Software Dependencies

### Git
* Git https://git-scm.com/downloads

### Backend (Django)
* Python 3.11 or higher
* Django 4.x or higher

### Database (SQLite)
* SQLite 3.31.0 and later

## Setup Instructions

### Step 1: Clone the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/Laurent-B2002/DigitalZooManagementSystem.git
cd bookstore-management-system
```

### Step 2: System Setup
Run the following command to set up and initialize the system

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Access the Webpage
Open your browser and visit:

```
http://localhost:8000
```

## Project Structure

```
bookstore-management-system/
├── inventory/               # App content
├── readers_haven/           # Django app settings
├── manage.py                # To run the program
├── UML Diagrams             # UML Diagrams of this project
├── Slides                   # Weekly presentations on the project
└── README.md                # This file
```

## Features

### Book Inventory Management System
- Adding, updating, deleting books, and viewing from the inventory

### Author Management
- Adding, updating, deleting, and viewing authors from the inventory

### Listing Inventory Content
- Sort authors and books by specific criteria

### Bulk Operations
- Bulk add and bulk delete books

### Adding Books Through Available APIs
- Bulk add books using online library APIs
