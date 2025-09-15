from django.apps import AppConfig
from django.core.cache import cache
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        from .utils import MailAutomation
        mailauto=MailAutomation()
        print("Data time:",datetime.now())
        # if settings.SCHEDULER_AUTOSTART:
        #             scheduler = BackgroundScheduler()
        #             scheduler.add_job(mailauto.mailExtraction, 'interval', seconds=5)
        #             scheduler.start()
        