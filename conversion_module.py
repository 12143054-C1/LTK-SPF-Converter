# conversion_module.py
import os
import time

class Converter:
    def __init__(self, source_path, dest_path, cpu_gen, use_itpp, progress_callback=None):
        self.source_path = source_path
        self.dest_path = dest_path
        self.cpu_gen = cpu_gen
        self.use_itpp = use_itpp
        self.progress_callback = progress_callback

    def run_conversion(self):
        try:
            if not os.path.exists(self.dest_path):
                os.makedirs(self.dest_path)

            if os.path.isdir(self.source_path):
                files = os.listdir(self.source_path)
                total_files = len(files)
                for i, file in enumerate(files):
                    # Simulating conversion for each file
                    time.sleep(0.1)  # Simulating a long-running process
                    if self.progress_callback:
                        progress = int((i + 1) / total_files * 100)
                        self.progress_callback(progress)
            else:
                # Simulate conversion for a single file
                time.sleep(0.1)  # Simulating a long-running process
                if self.progress_callback:
                    self.progress_callback(100)
            
            with open(os.path.join(self.dest_path, 'conversion_log.txt'), 'w') as f:
                f.write(f"Source: {self.source_path}\n")
                f.write(f"Destination: {self.dest_path}\n")
                f.write(f"CPU Gen: {self.cpu_gen}\n")
                f.write(f"Use ITPP Comments: {'Yes' if self.use_itpp else 'No'}\n")
            print(f"Conversion completed for {self.source_path} to {self.dest_path}")
        except Exception as e:
            print(f"Error during conversion: {e}")
