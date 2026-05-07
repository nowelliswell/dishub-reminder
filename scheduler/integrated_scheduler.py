"""
Integrated Scheduler for Flask App
Runs in background without circular import
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import requests

def send_daily_reminders():
    """
    Fungsi yang dipanggil scheduler setiap hari jam 12:00 WIB
    Mengirim reminder untuk H-1 dan H-2
    """
    print(f"\n{'='*50}")
    print(f"🕐 SCHEDULER TRIGGERED: {datetime.now()}")
    print(f"{'='*50}\n")
    
    try:
        # Panggil endpoint /run_now
        response = requests.post('http://localhost:5000/run_now', json={})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scheduler berhasil kirim {len(data)} reminder")
            for item in data:
                print(f"   - {item['name']} ({item['vehicle_number']}) → {item['send_result']['status']}")
        else:
            print(f"❌ Scheduler error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Scheduler exception: {str(e)}")

def init_scheduler():
    """
    Inisialisasi scheduler dengan timezone WIB
    Returns scheduler object
    """
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Jakarta'))
    
    # Jadwalkan kirim reminder setiap hari jam 12:00 WIB
    scheduler.add_job(
        func=send_daily_reminders,
        trigger='cron',
        hour=12,
        minute=0,
        id='daily_reminder',
        name='Send Daily Reminders',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler initialized - Will send reminders daily at 12:00 WIB")
    
    return scheduler
