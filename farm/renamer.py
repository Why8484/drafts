import os

def remove_prefix(folder_path, prefix):
    # Ensure the folder path exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    # Loop through all items in the given directory
    for filename in os.listdir(folder_path):
        # Full path to check if it's a file (skips subfolders)
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and filename.startswith(prefix):
            # Remove the prefix from the filename
            new_name = filename[len(prefix):]
            new_path = os.path.join(folder_path, new_name)
            
            # Rename the file
            os.rename(file_path, new_path)
            print(f"Renamed: '{filename}' -> '{new_name}'")

remove_prefix(r"assets\\progressBar2","pixil-frame-")