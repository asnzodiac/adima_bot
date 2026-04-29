from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()
scheduler.start()

def add_reminder(callback, chat_id, message, run_time):
    scheduler.add_job(
        callback,
        "date",
        run_date=run_time,
        args=[chat_id, message],
    )
