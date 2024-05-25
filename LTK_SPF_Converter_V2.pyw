import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, subprocess
import csv
from datetime import datetime
import threading
from conversion_module import Converter

class Converter_GUI():
    def __init__(self, root):
        self.history_file = "ltk_spf_history.csv"
        self.create_history_file()
        self.read_history()

        ## window top bar title
        self.root = root
        self.root.title("LTK SPF Converter")
        self.root.minsize(1200, 260)  # Set the minimum window size

        ## create the menu
        self.create_menu()

        ## source frame
        self.source_frame = tk.LabelFrame(root, text='Source')
        self.source_frame.pack(fill='x', pady=10, padx=5)
        ## source text
        source_label = tk.Label(self.source_frame, text="Input:")
        source_label.pack(side='left', padx=0)
        ## source radiobuttons
        self.source_type = tk.StringVar(value='file')  # Variable to hold the source type
        self.source_file_radiobutton = tk.Radiobutton(self.source_frame, text="File", variable=self.source_type, value='file', command=self.update_combobox)
        self.source_file_radiobutton.pack(side='left')
        self.source_folder_radiobutton = tk.Radiobutton(self.source_frame, text="Folder", variable=self.source_type, value='folder', command=self.update_combobox)
        self.source_folder_radiobutton.pack(side='left')
        ## select button
        self.select_button = tk.Button(self.source_frame, text="Select File / Folder", command=self.select_file_folder)
        self.select_button.pack(side='left', padx=2, pady=5)
        ## source select combobox
        self.source_select_combobox = ttk.Combobox(self.source_frame)
        self.source_select_combobox.pack(fill='x', expand=True, padx=2)
        ## initially populate the combobox with file history
        self.update_combobox()

        ## destination frame
        self.dest_frame = tk.LabelFrame(root, text='Destination')
        self.dest_frame.pack(fill='x', pady=10, padx=5)
        ## default output folder button
        self.default_output_button = tk.Button(self.dest_frame, text="Default Output Folder", command=self.set_default_output_folder)
        self.default_output_button.pack(side='left', padx=3, pady=5)
        ## destination select button
        self.dest_select_button = tk.Button(self.dest_frame, text="Select Output Folder", command=self.select_output_folder)
        self.dest_select_button.pack(side='left', padx=2, pady=5)
        ## destination select combobox
        self.dest_select_combobox = ttk.Combobox(self.dest_frame)
        self.dest_select_combobox.pack(fill='x', expand=True, padx=2)
        ## initially populate the combobox with destination history
        self.update_dest_combobox()

        ## Bottom Frame
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(fill='x', pady=5, padx=5)

        ## Bottom Left frame - Options
        self.options_frame = tk.LabelFrame(self.bottom_frame, text="Options")  # make it a LabelFrame with the title 'Options'
        self.options_frame.pack(fill='x', padx=5, side='left', anchor='w')
        ## CPU GEN combobox
        self.spu_gen_frame = tk.Frame(self.options_frame)
        self.spu_gen_frame.pack()
        self.cpu_gen_label = tk.Label(self.spu_gen_frame, text="CPU Gen:")
        self.cpu_gen_label.pack(side='left', padx=5)
        self.cpu_gen = ttk.Combobox(self.spu_gen_frame, values=["PTL", "LNL", "MTL-P", "MTL1"])
        self.cpu_gen.pack(padx=5)
        self.cpu_gen.set("PTL")
        ## add 'Use itpp Comments' tick button to options frame
        self.use_itpp = tk.IntVar()
        self.use_itpp_checkbutton = tk.Checkbutton(self.options_frame, text="Use itpp Comments", variable=self.use_itpp)
        self.use_itpp_checkbutton.pack(anchor='w')

        ## Bottom right frame
        self.buttons_frame = tk.Frame(self.bottom_frame)
        self.buttons_frame.pack(side='right', padx=10)
        self.convert_button = tk.Button(self.buttons_frame, text="Convert", command=self.convert)
        self.convert_button.pack(side='right', padx=10)

        ## Progress Bar
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=5)

        ## Floor Frame
        self.floor_frame = tk.Frame(root)
        self.floor_frame.pack(fill='x', pady=5, padx=5, side='bottom', anchor='s')

        ## Software Version
        self.version_label = tk.Label(self.floor_frame, text="2.0.0b1")
        self.version_label.pack(side='left')

        ## Copyright
        self.copyright_label = tk.Label(self.floor_frame, text="© 2024 Sivan Zusin")
        self.copyright_label.pack(side='right')

    def progress_callback(self, value):
        self.progress.set(value)

    def create_history_file(self):
        # Create history file named ltk_spf_history.csv if it does not exist
        if not os.path.exists(self.history_file):
            with open(self.history_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([])  # File source history
                writer.writerow([])  # Folder source history
                writer.writerow([])  # Destination history

    def read_history(self):
        # Read the history into self.source_history and self.dest_history
        self.source_file_history = []
        self.source_folder_history = []
        self.dest_history = []

        with open(self.history_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if len(rows) > 0:
                self.source_file_history = rows[0]
            if len(rows) > 1:
                self.source_folder_history = rows[1]
            if len(rows) > 2:
                self.dest_history = rows[2]

    def create_menu(self):
        # Create the top menu with 'LTK' button
        menubar = tk.Menu(self.root)
        ltk_menu = tk.Menu(menubar, tearoff=0)
        ltk_menu.add_command(label="Help", command=self.show_help)
        ltk_menu.add_command(label="Clear History", command=self.clear_history)
        ltk_menu.add_separator()
        ltk_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="Menu", menu=ltk_menu)
        self.root.config(menu=menubar)

    def show_help(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Search for a .chm file in the directory
        chm_files = [f for f in os.listdir(script_dir) if f.endswith('.chm')]
        
        if chm_files:
            # If there are multiple .chm files, choose the first one
            chm_file = os.path.join(script_dir, chm_files[0])
            # Open the CHM file using the default CHM viewer
            subprocess.Popen(["hh.exe", chm_file])
        else:
            messagebox.showerror("Error", "Help file not found!")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the history?"):
            with open(self.history_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([])  # Clear file source history
                writer.writerow([])  # Clear folder source history
                writer.writerow([])  # Clear destination history
            self.read_history()
            self.update_combobox()
            self.update_dest_combobox()

    def update_dest_based_on_source(self, event):
        source_path = self.source_select_combobox.get()
        if source_path:
            if self.source_type.get() == 'file':
                base_path = os.path.dirname(source_path)
            else:
                base_path = source_path

            timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
            default_folder = os.path.join(base_path, f"LTK_{timestamp}")
            self.update_history(self.dest_history, default_folder)
            self.update_dest_combobox()
            self.dest_select_combobox.set(default_folder)

    def select_file_folder(self):
        # Function to handle file/folder selection
        if self.source_type.get() == 'file':
            file_path = filedialog.askopenfilename()
            if file_path:
                self.source_file_history.insert(0, file_path)  # Update source file history
                self.update_combobox()
                self.source_select_combobox.set(file_path)
                base_path = os.path.dirname(file_path)
        else:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.source_folder_history.insert(0, folder_path)  # Update source folder history
                self.update_combobox()
                self.source_select_combobox.set(folder_path)
                base_path = folder_path

        if base_path:
            # Automatically set the default output folder after source selection
            timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
            default_folder = os.path.join(base_path, f"LTK_{timestamp}")
            self.dest_history.insert(0, default_folder)  # Update destination folder history
            self.update_dest_combobox()
            self.dest_select_combobox.set(default_folder)

    def select_output_folder(self):
        # Function to handle output folder selection
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.update_history(self.dest_history, folder_path)
            self.update_dest_combobox()
            self.dest_select_combobox.set(folder_path)
            self.save_history()

            # Automatically set the default output folder after destination selection
            timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
            default_folder = os.path.join(folder_path, f"LTK_{timestamp}")
            self.update_history(self.dest_history, default_folder)
            self.update_dest_combobox()
            self.dest_select_combobox.set(default_folder)
            self.save_history()



    def set_default_output_folder(self):
        # Function to handle setting the default output folder
        source_path = self.source_select_combobox.get()
        if not source_path:
            messagebox.showerror("Error", "Source not selected!")
            return

        if self.source_type.get() == 'file':
            base_path = os.path.dirname(source_path)
        else:
            base_path = source_path

        timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        default_folder = os.path.join(base_path, f"LTK_{timestamp}")

        self.update_history(self.dest_history, default_folder)
        self.update_dest_combobox()
        self.dest_select_combobox.set(default_folder)
        self.save_history()

    def update_history(self, history, item):
        # Update the history to behave like a stack
        if item in history:
            history.remove(item)
        history.insert(0, item)

    def save_history(self):
        # Save the updated histories to the CSV file only when 'Convert' button is pressed
        with open(self.history_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.source_file_history)
            writer.writerow(self.source_folder_history)
            writer.writerow(self.dest_history)

    def update_combobox(self):
        # Update the combobox items based on the selected source type (file or folder)
        if self.source_type.get() == 'file':
            self.source_select_combobox['values'] = self.source_file_history
        else:
            self.source_select_combobox['values'] = self.source_folder_history
        self.save_history()

    def update_dest_combobox(self):
        # Update the combobox items for the destination history
        self.dest_select_combobox['values'] = self.dest_history

    def convert(self):
        # Check if source and destination are selected, if not raise an error
        source_path = self.source_select_combobox.get()
        dest_path = self.dest_select_combobox.get()
        if not source_path:
            messagebox.showerror("Error", "Source not selected!")
            return
        if not dest_path:
            messagebox.showerror("Error", "Destination not selected!")
            return
        
        # save history
        self.save_history()

        # Gather conversion details
        cpu_gen = self.cpu_gen.get()
        use_itpp = self.use_itpp.get()

        # Create an instance of the Converter class
        converter = Converter(source_path, dest_path, cpu_gen, use_itpp, self.progress_callback)
        
        # Run the conversion in a separate thread
        conversion_thread = threading.Thread(target=converter.run_conversion)
        conversion_thread.start()

        # Display conversion details
        messagebox.showinfo("Convert",  f"Convert button clicked.\n"
                                        f"Source: {source_path}\n"
                                        f"Destination: {dest_path}\n"
                                        f"CPU Gen: {cpu_gen}\n"
                                        f"Use itpp Comments: {'Yes' if use_itpp else 'No'}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Converter_GUI(root)
    root.mainloop()
