"""
Automatic Reminder Scheduler
Schedules the send_automatic_reminders function to run daily at 12:00 WIB.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Add the parent directory to the path to import from whatsapp_reminder_app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whatsapp_reminder_app import send_automatic_reminders, init_db

def job_send_reminders():
    """
    Job function that calls send_automatic_reminders.
    This is scheduled to run daily at 12:00 WIB.
    """
    print(f"🕐 [{datetime.now(timezone(timedelta(hours=7))).isoformat()}] Starting automatic reminder job...")
    try:
        result = send_automatic_reminders()
        print(f"✅ Job completed: {result}")
    except Exception as e:
        print(f"❌ Job failed: {str(e)}")

def main():
    """
    Main function to start the scheduler.
    """
    # Initialize database
    init_db()
    print("📅 Database initialized for scheduler.")

    # Create scheduler
    scheduler = BlockingScheduler()

    # Schedule the job to run daily at 12:00 WIB (UTC+7)
    # Cron expression: minute=0, hour=12, day=*, month=*, day_of_week=*
    # Since WIB is UTC+7, and APScheduler uses system timezone by default,
    # we need to specify the timezone
    wib_timezone = timezone(timedelta(hours=7))
    trigger = CronTrigger(hour=12, minute=0, timezone=wib_timezone)

    scheduler.add_job(
        job_send_reminders,
        trigger=trigger,
        id='send_automatic_reminders',
        name='Send Automatic Reminders at 12:00 WIB',
        replace_existing=True
    )

    print("🚀 Scheduler started. Automatic reminders will be sent daily at 12:00 WIB.")
    print("Press Ctrl+C to stop the scheduler.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user.")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
