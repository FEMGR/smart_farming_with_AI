"""
Worker module for background scheduling (Irrigation).

Key Point:
Runs periodic background jobs to monitor plant conditions and trigger irrigation-related logic.

Responsibilities:
- Execute scheduled irrigation checks
- Iterate through all users and their plants
- Trigger irrigation logic and notifications

Architecture Role:
- Acts as a background worker outside the request-response cycle
- Enables automation of system tasks without user interaction

Layer Interaction:
- Communicates with: Services (irrigation_service), Models (user), Database
- Used by: Main application (startup event)

Data Flow:
Scheduler triggers job (interval or startup)
        ↓
Database session created
        ↓
All users retrieved
        ↓
For each user:
    irrigation service checks plant conditions
        ↓
Notifications triggered if needed
        ↓
Session closed after execution

Notes:
- Runs independently of API requests
- Should be started once during application startup
- Interval can be adjusted based on system needs
"""

#app.workers.scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.user import User
from app.services import irrigation_service
from app.core.logger import setup_logger

scheduler = BackgroundScheduler()
logger = setup_logger()

# ===============================
# JOB: CHECK ALL USERS
# ===============================
def irrigation_job():
    """
    Runs periodically:
    - loops all users
    - checks plants
    - triggers notifications
    """

    db: Session = SessionLocal()

    try:
        users = db.query(User).all()
        for user in users:
            irrigation_service.get_plants_needing_water(
                db=db,
                user_id=user.id
            )
        logger.info("Irrigation job executed")

    finally:
        db.close()

# ===============================
# START SCHEDULER
# ===============================
def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            irrigation_job,
            "interval",
            minutes=10,
            id="irrigation_interval",
            replace_existing=True
        )

        scheduler.add_job(
            irrigation_job,
            "date",
            id="irrigation_startup",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started.")

# ===============================
# STOP SCHEDULER
# ===============================
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
