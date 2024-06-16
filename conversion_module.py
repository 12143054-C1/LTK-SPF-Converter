#############################
# Module name: conversion_module.py
# Description: This module defines a Converter class responsible for handling the conversion of files or folders 
#              from a source path to a destination path. The conversion process includes options for CPU generation 
#              and the use of ITPP comments. The progress of the conversion is updated via a callback function.
#############################

import os
import time
import subprocess
import spf2sv_converter

class Converter:
    def __init__(self, source_path, dest_path, cpu_gen, use_itpp, progress_callback=None, stop_callback=None, completion_callback=None):
        self.completion_callback = completion_callback
        self.source_path = source_path
        self.dest_path = dest_path
        self.cpu_gen = cpu_gen
        self.use_itpp = use_itpp
        self.progress_callback = progress_callback
        self.conversion_time = time.time()
        self.stop_callback = stop_callback

    def run_conversion(self):
        if not os.path.exists(self.dest_path):
            os.makedirs(self.dest_path)

        if os.path.isdir(self.source_path):
            files_ = os.listdir(self.source_path)
            files = [file for file in files_ if file.lower().endswith('.spf')]
            total_files = len(files)
            if total_files == 0:
                print(">>> Error: no valid files found!")
            else:
                for i, file in enumerate(files):
                    if self.stop_callback():
                        print("STOPPED !!!!")
                        ## Open the destination folder after conversion
                        if os.path.exists(self.dest_path):
                            self.dest_path = self.dest_path.replace("/","\\")
                            ## Open the folder using the default file manager
                        if os.name == "nt":  # Windows
                            subprocess.Popen(f'explorer "{self.dest_path}"')
                        elif os.name == "posix":  ## Linux or macOS
                            subprocess.Popen(["xdg-open", destination_entry.get()])
                        progress = 0
                        self.progress_callback(progress)
                        return
                    ## Folder conversion function here
                    spf2sv_converter.run(
                        direct_reg= self.use_itpp,
                        conversion_time= self.conversion_time,
                        log_file_path= os.path.join(self.dest_path, 'conversion_log.txt'),
                        _week_folder_en= False,
                        _input_dir= self.source_path,
                        _input_file = os.path.join(self.source_path,file),
                        _output_dir= self.dest_path,
                        CPUgen= self.cpu_gen
                    )
                    if self.progress_callback:
                        progress = int((i + 1) / total_files * 100)
                        self.progress_callback(progress)
        else:
            ## File conversion function here
            # Simulate conversion for a single file
            files = [file for file in [self.source_path] if file.lower().endswith('.spf')]
            if not files:
                print(">>> Error: Invalid file!")
            else:
                spf2sv_converter.run(
                        direct_reg= self.use_itpp,
                        conversion_time= self.conversion_time,
                        log_file_path= os.path.join(self.dest_path, 'conversion_log.txt'),
                        _week_folder_en= False,
                        _input_dir= os.path.dirname(self.source_path),
                        _input_file = self.source_path,
                        _output_dir= self.dest_path,
                        CPUgen= self.cpu_gen
                    )
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
        if self.completion_callback:
                self.completion_callback()  # Call the completion callback at the end of the conversion
