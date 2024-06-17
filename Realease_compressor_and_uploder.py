import os
import re
import zipfile
import shutil
from packaging import version

def compress_subfolders_to_zip(release_folder_path, output_folder_path):
    if not os.path.isdir(release_folder_path):
        raise NotADirectoryError(f"The provided path '{release_folder_path}' is not a valid directory.")
    if not os.path.isdir(output_folder_path):
        os.makedirs(output_folder_path)
    
    version_pattern = r'^\d+\.\d+\.\d+[a-z]?\d*$'
    
    latest_version = None
    latest_version_folder = None
    zip_files = []
    
    for item in os.listdir(release_folder_path):
        item_path = os.path.join(release_folder_path, item)
        
        if os.path.isdir(item_path) and re.search(version_pattern, item.split('_')[-1]):
            current_version = item.split('_')[-1]
            
            if (latest_version is None or version.parse(current_version) > version.parse(latest_version)):
                latest_version = current_version
                latest_version_folder = item_path
            
            zip_file_path = os.path.join(output_folder_path, f"{item}.zip")
            zip_files.append(zip_file_path)
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, release_folder_path))
    
    if latest_version_folder:
        latest_zip_file_path = os.path.join(output_folder_path, "Latest.zip")
        zip_files.append(latest_zip_file_path)
        with zipfile.ZipFile(latest_zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(latest_version_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, release_folder_path))
    
    print(f"All subfolders in '{release_folder_path}' have been compressed into zip files in '{output_folder_path}', including the latest version as 'Latest.zip'.")
    return zip_files

def copy_subfolders(release_folder_path, output_folder_path):
    if not os.path.isdir(release_folder_path):
        raise NotADirectoryError(f"The provided path '{release_folder_path}' is not a valid directory.")
    if not os.path.isdir(output_folder_path):
        os.makedirs(output_folder_path)
    
    version_pattern = r'^\d+\.\d+\.\d+[a-z]?\d*$'
    
    latest_version = None
    latest_version_folder = None
    
    for item in os.listdir(release_folder_path):
        item_path = os.path.join(release_folder_path, item)
        
        if os.path.isdir(item_path) and re.search(version_pattern, item.split('_')[-1]):
            current_version = item.split('_')[-1]
            
            if (latest_version is None or version.parse(current_version) > version.parse(latest_version)):
                latest_version = current_version
                latest_version_folder = item_path
            
            output_item_path = os.path.join(output_folder_path, item)
            if os.path.exists(output_item_path):
                shutil.rmtree(output_item_path)
            shutil.copytree(item_path, output_item_path)
    
    if latest_version_folder:
        latest_folder_path = os.path.join(output_folder_path, "Latest")
        if os.path.exists(latest_folder_path):
            # Delete the content of the 'Latest' folder
            for root, dirs, files in os.walk(latest_folder_path):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
        else:
            os.makedirs(latest_folder_path)
        
        # Copy the new content into the 'Latest' folder
        for item in os.listdir(latest_version_folder):
            s = os.path.join(latest_version_folder, item)
            d = os.path.join(latest_folder_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    
    print(f"All subfolders in '{release_folder_path}' have been copied to '{output_folder_path}', including the latest version as 'Latest'.")

# Example usage:
release_folder_path = r'Release'
output_folder_path = r'C:\Users\szusin\OneDrive - Intel Corporation\LTK Converter'

# Compress subfolders to zip files
#zip_files = compress_subfolders_to_zip(release_folder_path, output_folder_path)

# Copy subfolders and update 'Latest' folder
copy_subfolders(release_folder_path, output_folder_path)