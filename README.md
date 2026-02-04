#  BusiBook: Nairobi Smart Transit System

**Live Demo:** https://busibook.onrender.com/
BusiBook is a full-stack booking application designed to streamline the commuter experience in Nairobi. It allows users to book seats on "Ordinary" or "Nganya" buses with instant PDF receipt generation.

## Features
- **Dynamic Fare Calculation:** Real-time price updates based on bus type (Ordinary vs. Nganya).
- **Automated Ticketing:** Instant PDF generation using ReportLab.
- **Production-Ready DB:** Remote MySQL integration for persistent data.
- **Responsive UI:** Mobile-first design optimized for Kenyan commuters.

## Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript (Mobile-Responsive)
- **Backend:** Python (Flask)
- **Server:** Gunicorn
- **Database:** Remote MySQL (FreeSQLDatabase)
- **Deployment:** Render (CI/CD via GitHub)

## Architecture
The app uses a **decoupled architecture**. The Flask server acts as a RESTful intermediary between the frontend and the cloud database, ensuring secure data handling and efficient processing.
