# TODO: WhatsApp Reminder App - Automatic Messaging

## Completed Tasks
- [x] Analyze whatsapp_reminder_app.py and identify existing send_automatic_reminders function
- [x] Update classify_by_days function to include H-2 as separate status (blue color)
- [x] Create scheduler/auto_send.py to schedule automatic reminders daily at 12:00 WIB
- [x] Install APScheduler dependency: `pip install apscheduler`
- [x] Test syntax and compilation of modified and new files (no errors)

## Next Steps
- [ ] Run the scheduler in production: `python scheduler/auto_send.py` (this will block and run continuously)
- [ ] Verify that reminders are sent correctly at 12:00 WIB for H-1 and H-2
- [ ] Optionally, add a manual trigger route in whatsapp_reminder_app.py for testing: POST /send_automatic
- [ ] Ensure clean code and error handling in all functions

## Notes
- The send_automatic_reminders function already exists and sends messages for H-1 and H-2 at 12:00 WIB
- Scheduler uses APScheduler to run the job daily at 12:00 WIB (UTC+7)
- H-2 is now classified separately with "info" color (blue)
- Code is written cleanly with proper error handling and logging
