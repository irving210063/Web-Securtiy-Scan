import os
from werkzeug.utils import secure_filename
import shutil
import threading 
import sys
name = sys.argv[1]
def delete_folder(deleted_folder):
    shutil.rmtree(deleted_folder)

