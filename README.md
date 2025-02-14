# Event Management API

## Overview
This is a FastAPI-based Event Management API that allows users to create, manage, and track events and attendees. The API includes event scheduling, attendee registration, check-ins, and status management. It also supports bulk attendee check-ins via CSV upload and includes authentication for extra security.

## Features
- **Create, Update, and List Events**
- **Register and Check-in Attendees**
- **Automatic Event Status Updates** (e.g., completed if end time has passed)
- **Bulk Check-in Support** via CSV upload
- **JWT Authentication** (Optional Extra Credit)

## Technologies Used
- **FastAPI** (Web framework)
- **SQLAlchemy** (ORM for database handling)
- **SQLite** (Database)
- **Uvicorn** (ASGI server)

---

## Installation & Setup

### **Prerequisites**
- Python 3.8+
- Pip installed

### **1. Clone the Repository**
```bash
# Clone this repository
https://github.com/rajat-valecha200/event_management_api
cd event-management-api
```

### **2. Install Dependencies**
```bash
pip install fastapi uvicorn sqlalchemy
```

### **3. Run the API**
```bash
uvicorn event_management_api:app --reload
```
