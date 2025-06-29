import asyncio
import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

from main import main

load_dotenv()


hours = os.environ.get("HOUR")
mins = os.environ.get("MINUTE")


app = Celery("check_in", broker="redis://redis:6379/0")

app.conf.beat_schedule = {
    'daily-checki-in': {
        'task': 'celeryconfig.do_checkin',
        'schedule': crontab(day_of_week="1-5", hour=hours, minute=mins),
    },
}
app.conf.timezone = 'Asia/Karachi'
app.conf.enable_utc = False


@app.task
def do_checkin():
    asyncio.run(main({}))
