#------------------------------------------------------------------------------------
# Developed by MalkasianGroup, LLC - Open Source server backup script for MacMini
# Free for personal use only – for enterprise or business use, please email malkasian(a)dsm.studio
#---------------------------------------------------------------------------------------

__version__ = "1.0"

#--------------------------------------IMPORTS------------------------------------------
import os
import shutil
from datetime import datetime
#--------------------------------------VARIABLES------------------------------------------

server_directory = "PATH_TO_FOLDER(S)_YOU_WANT_TO_BACK_UP"
backup_folder = "LOCATION_YOU_WANT_TO_SAVE_BACKUP_TO"

def backup_server():
    timestamp = datetime.now().strftime("%Y-%m-%d") 
    destination_folder = os.path.join(backup_folder, f"backup_{timestamp}")
    shutil.copytree(server_directory, destination_folder)
    shutil.make_archive(destination_folder, 'zip', destination_folder)
    print(f"Backup completed to {destination_folder}.zip")

backup_server()