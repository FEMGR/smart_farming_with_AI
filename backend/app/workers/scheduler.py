from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.user import User
from app.services import irrigation_service

scheduler = BackgroundScheduler()


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

        print("✅ Irrigation job executed")

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

