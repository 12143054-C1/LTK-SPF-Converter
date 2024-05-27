#############################
# Module name: conversion_module.py
# Description: This module defines a Converter class responsible for handling the conversion of files or folders 
#              from a source path to a destination path. The conversion process includes options for CPU generation 
#              and the use of ITPP comments. The progress of the conversion is updated via a callback function.
#############################

import os
import time
import subprocess
import USE_EXAMPLE as ue

class Converter:
    def __init__(self, source_path, dest_path, cpu_gen, use_itpp, progress_callback=None):
        self.source_path = source_path
        self.dest_path = dest_path
        self.cpu_gen = cpu_gen
        self.use_itpp = use_itpp
        self.progress_callback = progress_callback
        self.conversion_time = time.time()

    def run_conversion(self):
        try:
            if not os.path.exists(self.dest_path):
                os.makedirs(self.dest_path)

            if os.path.isdir(self.source_path):
                files = os.listdir(self.source_path)
                total_files = len(files)
                # for i, file in enumerate(files):   ############### loop disabled in beta 1 release
                for i in [0]:
                    ## Folder conversion function here
                    ue.use_example(
                        self.use_itpp,
                        self.source_path,
                        self.dest_path,
                        False,
                        os.path.join(self.dest_path, 'conversion_log.txt'),
                        self.conversion_time,
                        self.cpu_gen)
                    if self.progress_callback:
                        progress = int((i + 1) / total_files * 100)
                        self.progress_callback(progress)
            else:
                ## File conversion function here
                # Simulate conversion for a single file
                time.sleep(0.1)  # Simulating a long-running process
                if self.progress_callback:
                    self.progress_callback(100)
            
            with open(os.path.join(self.dest_path, 'conversion_log.txt'), 'a') as f:
                f.write(f"Source: {self.source_path}\n")
                f.write(f"Destination: {self.dest_path}\n")
                f.write(f"CPU Gen: {self.cpu_gen}\n")
                f.write(f"Use ITPP Comments: {'Yes' if self.use_itpp else 'No'}\n")
            print(f"Conversion completed for {self.source_path} to {self.dest_path}")

            ## Open the destination folder after conversion
            if os.path.exists(self.dest_path):
                self.dest_path = self.dest_path.replace("/","\\")
                ## Open the folder using the default file manager
                if os.name == "nt":  # Windows
                    subprocess.Popen(f'explorer "{self.dest_path}"')
                elif os.name == "posix":  ## Linux or macOS
                    subprocess.Popen(["xdg-open", destination_entry.get()])

        except Exception as e:
            print(f"Error during conversion: {e}")
