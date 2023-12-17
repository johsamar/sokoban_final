
import os

def delete_files(folder_path = "states"):
    files = os.listdir(folder_path)

    # Iterate over the list and delete each file
    for file_name in files:
        full_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(full_path):
                os.unlink(full_path)
            elif os.path.isdir(full_path):
                os.rmdir(full_path)
        except Exception as e:
            print(f"Failed to delete {full_path}. Error: {e}")