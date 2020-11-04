import os
import platform
from zipfile import ZipFile


def extraction(file_with_path):
    
    system_os = platform.system()
    path = os.getcwd()
    print("curr path is", path)
    if system_os == "Windows":
        new_path = os.path.join(path, r"storage\content\zips")
        # print("new path is", new_path)
    else:
        new_path = os.path.join(path, "storage/content/zips")
        # print("new path is", new_path)
    index = ''
    with ZipFile(file_with_path, 'r') as zip1:
        zip1.extractall(new_path)
        index_files = zip1.namelist()

        for s in index_files:
            if 'index.html' in s:
                index = s
                return index
            else:
                continue

# extraction(r"C:\contentservermech\contentserver\pos\static\storage\content\extractions\Pictionary_L1_HI.zip")
