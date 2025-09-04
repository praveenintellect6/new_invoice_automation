from datetime import datetime
from django.conf import settings
import os 


class PurchaseReportClass:
    def __init__(self):
        pass

    def createFolderByDate(self,date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        folder_path = os.path.join(settings.MEDIA_ROOT,str(dt.year),dt.strftime("%b"),date_str)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path




