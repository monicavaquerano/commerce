from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_closing


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        schedule_closing, "interval", seconds=10
    )  # In a real scenario it would be every day
    scheduler.start()
