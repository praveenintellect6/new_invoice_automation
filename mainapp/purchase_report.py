from datetime import datetime
from django.conf import settings
import os 
import shutil
import time

class PurchaseReportClass:
    def __init__(self):
        pass

    def createFolderByDate(self,date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        folder_path = os.path.join(settings.MEDIA_ROOT,str(dt.year),dt.strftime("%b"),date_str)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    

    def copy_folder_contents(source_folder, destination_folder=None, retries=5, delay=0.5):
   
        if not os.path.exists(source_folder):
            print(f"❌ Source folder does not exist: {source_folder}")
            return
        relative_path = os.path.relpath(source_folder)
        destination_folder=rf"\\system26\D\Jijo\newmedia\{relative_path}"
        print("destination_folder",destination_folder)
        os.makedirs(destination_folder, exist_ok=True)

        for root, dirs, files in os.walk(source_folder):
            # Compute corresponding destination folder
            relative_path = os.path.relpath(root, source_folder)
            dest_root = os.path.join(destination_folder, relative_path)
            os.makedirs(dest_root, exist_ok=True)

            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_root, file)

                for attempt in range(retries):
                    try:
                        shutil.copy2(src_file, dst_file)  
                        print(f"✅ Copied: {src_file} -> {dst_file}")
                        break
                    except PermissionError:
                        print(f"⚠️ Locked, retrying ({attempt+1}/{retries}): {src_file}")
                        time.sleep(delay)
                else:
                    print(f"❌ Skipped locked file: {src_file}")



