# 🏛️ Banquet Booking System

A **Flask-based web application** designed to simplify the process of booking banquet halls for events.  
It provides separate dashboards for **users** and **admins**, allowing easy booking management, confirmation, and status tracking.

---

## 🚀 Features

### 👥 User Features
- Register and log in to the system
- Browse available banquet halls with images, capacity, and price
- Book halls by selecting:
  - Date
  - Time slot
  - Number of guests
  - **Services** (Catering, Decoration, Lighting, Sound System, Photography)
- View booking history and current booking status (Pending / Confirmed / Rejected)
- Responsive and user-friendly interface

---

### 🧑‍💼 Admin Features
- Admin login with credentials
- Dashboard view showing:
  - Total bookings
  - Confirmed / Pending / Rejected counts
  - **Service usage statistics** (how many times each service was selected)
- View all user bookings with hall name and services selected
- Approve or reject bookings directly
- Clean, visual layout with summary cards and statistics

---

## 🧠 Tech Stack
- **Frontend:** HTML, CSS (custom responsive design)
- **Backend:** Flask (Python)
- **Database:** SQLite
- **Templates:** Jinja2
- **Password Security:** Werkzeug (hashed passwords)
- **Version Control:** Git & GitHub

---

## ⚙️ How to Run the Project

### Step 1 — Clone the Repository
```bash
git clone https://github.com/johnjoshua1502/banquet-booking-system.git
cd banquet-booking-system
