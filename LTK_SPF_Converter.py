#############################
# Module name: LTK_SPF_Converter.pyw
# Description: This module provides a graphical user interface for converting LTK SPF files using various options. 
#              The GUI includes functionalities for selecting source files or folders, choosing destination folders, 
#              setting CPU generation options, and enabling or disabling ITPP comments. The conversion process is 
#              handled in a separate thread, and progress is shown via a progress bar. The module also maintains 
#              a history of source and destination paths for convenience.
#############################

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter.font as tkFont
import os
import sys
import subprocess
import csv
from datetime import datetime
import threading
from conversion_module import Converter

VERSION = '2.1.0'


def send_email_with_attachments(to_email, subject, body, attachment_paths):
    # Convert the list of attachment paths to a semicolon-separated string
    attachments = ";".join(attachment_paths)

    # Build the command to run the VBScript
    command = [
        'cscript.exe',
        '//Nologo',  # Suppress script engine logo
        'compose_email.vbs',  # Path to the VBScript
        to_email,
        subject,
        body,
        attachments
    ]
    # Run the command
    subprocess.run(command)

class CustomErrorDialog(simpledialog.Dialog):
    def __init__(self, parent, title, text):
        self.text = text
        super().__init__(parent, title)
    def body(self, master):
        tk.Label(master, text=self.text).pack(pady=10)
        return master
    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="Send Log", width=10, command=self.send_log).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Help", width=10, command=self.help).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Cancel", width=10, command=self.cancel).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.send_log)
        self.bind("<Escape>", self.cancel)
        box.pack()
    def send_log(self, event=None):
        self.result = "send_log"
        self.destroy()
    def help(self, event=None):
        self.result = "help"
        self.destroy()
    def cancel(self, event=None):
        self.result = None
        self.destroy()

class TextRedirector:
        def __init__(self, text_widget, tag="stdout"):
            self.text_widget = text_widget
            self.tag = tag
        def write(self, str):
            self.text_widget.configure(state='normal')
            self.text_widget.insert('end', str, (self.tag,))
            self.text_widget.configure(state='disabled')
            self.text_widget.see('end')  # Scroll to the end
        def flush(self):
            pass

class Converter_GUI():
    def __init__(self, root):
        self.history_file = "ltk_spf_history.csv"
        self.create_history_file()
        self.read_history()

        # window top bar title
        self.root = root
        self.root.title("LTK SPF Converter")
        self.root.minsize(1200, 660)  # Set the minimum window size

        # Set the window icon
        self.set_window_icon()

        # create the menu
        self.create_menu()

        # source frame
        self.source_frame = tk.LabelFrame(root, text='Source')
        self.source_frame.pack(fill='x', pady=10, padx=5)
        # source text
        source_label = tk.Label(self.source_frame, text="Input:")
        source_label.pack(side='left', padx=0)
        # source radiobuttons
        # Variable to hold the source type
        self.source_type = tk.StringVar(value='Folder')
        self.source_file_radiobutton = tk.Radiobutton(
            self.source_frame, text="File", variable=self.source_type, value='File', command=self.update_combobox) ############### disabled in beta 1 release
        self.source_file_radiobutton.pack(side='left')
        self.source_folder_radiobutton = tk.Radiobutton(
            self.source_frame, text="Folder", variable=self.source_type, value='Folder', command=self.update_combobox)
        self.source_folder_radiobutton.pack(side='left')
        # select button
        self.select_button = tk.Button(
            self.source_frame, text="Select File / Folder", command=self.select_file_folder)
        self.select_button.pack(side='left', padx=2, pady=5)
        # source select combobox
        self.source_select_combobox = ttk.Combobox(
            self.source_frame, postcommand=self.update_source_history_on_select)
        self.source_select_combobox.pack(fill='x', expand=True, padx=2)
        # initially populate the combobox with file history
        self.update_combobox()

        # destination frame
        self.dest_frame = tk.LabelFrame(root, text='Destination')
        self.dest_frame.pack(fill='x', pady=10, padx=5)
        # default output folder button
        self.default_output_button = tk.Button(
            self.dest_frame, text="Default Output Folder", command=self.set_default_output_folder)
        self.default_output_button.pack(side='left', padx=3, pady=5)
        # destination select button
        self.dest_select_button = tk.Button(
            self.dest_frame, text="Select Output Folder", command=self.select_output_folder)
        self.dest_select_button.pack(side='left', padx=2, pady=5)
        # destination select combobox
        self.dest_select_combobox = ttk.Combobox(
            self.dest_frame, postcommand=self.update_dest_history_on_select)
        self.dest_select_combobox.pack(fill='x', expand=True, padx=2)
        # initially populate the combobox with destination history
        self.update_dest_combobox()

        # Bottom Frame
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(fill='x', pady=5, padx=0)

        # Bottom Left frame - Options
        # make it a LabelFrame with the title 'Options'
        self.options_frame = tk.LabelFrame(self.bottom_frame, text="Options")
        self.options_frame.pack(fill='x', padx=5, side='left', anchor='w')
        # CPU GEN combobox
        self.spu_gen_frame = tk.Frame(self.options_frame)
        self.spu_gen_frame.pack()
        self.cpu_gen_label = tk.Label(self.spu_gen_frame, text="CPU Gen:")
        self.cpu_gen_label.pack(side='left', padx=5)
        self.cpu_gen = ttk.Combobox(self.spu_gen_frame, values=[
                                    "PTL", "LNL"])
        self.cpu_gen.pack(padx=5)
        self.cpu_gen.set("PTL")
        # add 'Use itpp Comments' tick button to options frame
        self.use_itpp = tk.IntVar()
        self.use_itpp_checkbutton = tk.Checkbutton(
            self.options_frame, text="Use itpp Comments", variable=self.use_itpp)
        self.use_itpp_checkbutton.pack(anchor='w')

        # Bottom right frame
        self.buttons_frame = tk.Frame(self.bottom_frame)
        self.buttons_frame.pack(side='right', padx=10)
        self.convert_button = tk.Button(
            self.buttons_frame, text="Convert", command=self.convert, width=7)
        self.convert_button.pack(side='top', pady=2)
        self.stop_requested = False
        self.cancel_button = tk.Button(
            self.buttons_frame, text="Cancel", command=self.stop_convertion ,width=7,state='disabled')
        self.cancel_button.pack(side='top', pady=2)

        # Progress Bar  ########################################################
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            root, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=5)

        # Console Frame
        self.console_frame = tk.Frame(root)
        self.console_frame.pack(fill='both', expand=True, padx=0, pady=0)
        monospace_font = tkFont.Font(family="Courier New", size=10)  # You can change the size as needed
        self.console_text = tk.Text(
            self.console_frame,
            height=10,
            state='disabled',
            background='black',
            foreground='#00FF00',
            font=monospace_font,
            )
        self.console_text.pack(side='left', fill='both', expand=True)
        # Create a Scrollbar and set it to the right of the Text widget
        self.scrollbar = tk.Scrollbar(self.console_frame, command=self.console_text.yview)
        self.scrollbar.pack(side='right', fill='y')
        # Link the scrollbar to the text widget
        self.console_text.config(yscrollcommand=self.scrollbar.set)
        # Redirect standard output
        sys.stdout = TextRedirector(self.console_text, "stdout")


        # Floor Frame
        self.floor_frame = tk.Frame(root,relief='ridge',borderwidth=2)
        self.floor_frame.pack(fill='x', pady=0, padx=0, side='bottom', anchor='s')
        # Software Version
        self.version_label = tk.Label(self.floor_frame, text=VERSION)
        self.version_label.pack(side='left')
        # Copyright
        self.copyright_label = tk.Label(
            self.floor_frame, text="© 2024 Sivan Zusin")
        self.copyright_label.pack(side='right')

    def set_window_icon(self):
        # Get the absolute path to the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the icon file
        icon_path = os.path.join(script_dir, 'crown.ico')

        # Load and set the icon
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"Icon file not found: {icon_path}")


    def progress_callback(self, value):
        self.progress.set(value)

    def update_source_history_on_select(self):
        selected = self.source_select_combobox.get()
        history = ''
        if selected:
            if self.source_type.get() == 'File' and os.path.isfile(selected):
                history = self.source_file_history
            elif self.source_type.get() == 'Folder' and os.path.isdir(selected):
                history = self.source_folder_history
            if history:
                self.update_history(history, selected)
            self.update_combobox()  # Refresh the combobox with updated history

    def update_dest_history_on_select(self):
        selected = self.dest_select_combobox.get()
        if selected:
            self.update_history(self.dest_history, selected)
            self.update_dest_combobox()  # Refresh the combobox with updated history

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
            if self.source_type.get() == 'File':
                base_path = os.path.dirname(source_path)
            else:
                base_path = source_path

            timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
            default_folder = os.path.join(base_path, f"LTK_{timestamp}")
            self.update_history(self.dest_history, default_folder)
            self.update_dest_combobox()
            self.dest_select_combobox.set(default_folder)

    def select_file_folder(self):
        base_path = ''
        # Function to handle file/folder selection
        if self.source_type.get() == 'File':
            file_path = filedialog.askopenfilename()
            if file_path:
                self.update_history(self.source_file_history,file_path)
                self.update_combobox()
                self.source_select_combobox.set(file_path)
                base_path = os.path.dirname(file_path)
        else: # if it's a Folder
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.update_history(self.source_folder_history,folder_path)
                self.update_combobox()
                self.source_select_combobox.set(folder_path)
                base_path = folder_path

        if base_path:
            # Automatically set the default output folder after source selection
            timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
            default_folder = os.path.join(base_path, f"LTK_{timestamp}")
            # Update destination folder history
            self.dest_history.insert(0, default_folder)
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

        if self.source_type.get() == 'File':
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
        if self.source_type.get() == 'File':
            self.source_select_combobox['values'] = self.source_file_history
        else:
            self.source_select_combobox['values'] = self.source_folder_history
        self.save_history()

    def update_dest_combobox(self):
        # Update the combobox items for the destination history
        self.dest_select_combobox['values'] = self.dest_history

    def convert(self):
        self.console_text.configure(state='normal')  # Temporarily enable the widget for editing
        self.console_text.delete("1.0", "end")  # Delete all content from the start to the end
        self.console_text.configure(state='disabled')  # Disable the widget again to make it read-only
        # Check if source and destination are selected, if not raise an error
        self.source_path = self.source_select_combobox.get()
        self.dest_path = self.dest_select_combobox.get()
        if not self.source_path:
            messagebox.showerror("Error", "Source not selected!")
            return
        if not (os.path.isfile(self.source_path) or os.path.isdir(self.source_path)):
            messagebox.showerror("Error", "Invalid source!")
            return
        if not self.dest_path:
            messagebox.showerror("Error", "Destination not selected!")
            return

        # update and save history
        if os.path.isfile(self.source_path):
            self.update_history(self.source_file_history,self.source_path)
        else:
            self.update_history(self.source_folder_history,self.source_path)
        self.update_history(self.dest_history,self.dest_path)
        self.save_history()

        # Gather conversion details
        cpu_gen = self.cpu_gen.get()
        use_itpp = self.use_itpp.get()

        self.stop_requested = False

        # Create an instance of the Converter class
        converter = Converter(
            self.source_path,
            self.dest_path,
            cpu_gen,
            use_itpp,
            self.progress_callback,
            lambda: self.stop_requested,
            self.on_conversion_complete  # Pass the completion callback
            )
        # Run the conversion in a separate thread
        self.conversion_thread = threading.Thread(target=converter.run_conversion)
        self.conversion_thread.start()

        self.cancel_button.configure(state='normal')
        self.convert_button.configure(state='disabled')

        # # Display conversion details
        # messagebox.showinfo("Convert",  f"Convert button clicked.\n"
        #                                 f"Source: {source_path}\n"
        #                                 f"Destination: {dest_path}\n"
        #                                 f"CPU Gen: {cpu_gen}\n"
        #                                 f"Use itpp Comments: {'Yes' if use_itpp else 'No'}")
    
    def on_conversion_complete(self):
        # This method will be called when conversion is complete
        # Write log to logfile
        # Schedule error handling to be run in the main thread
        self.root.after(0, self.handle_error)

    def handle_error(self):
        self.console_log = self.console_text.get("1.0", "end-1c")
        self.log_path = os.path.join(self.dest_path, 'conversion_log.txt')
        with open(self.log_path, 'a') as logfile:
            logfile.write(self.console_log)
        if 'Tap not found' in self.console_log:  # Problem with conversion!
            self.attachment_paths = []
            lines  = self.console_log.split('\n')
            for i,line in enumerate(lines):
                if 'Tap not found' in line:
                    self.attachment_paths.append(lines[i+1])
            error_popup = CustomErrorDialog(self.root, "Problem Detected", "A problem was detected with the conversion. Would you like to send the log to the developer for debugging?")
            response = error_popup.result
            if response == "send_log":
                self.send_log_to_developer(self.log_path)
            elif response == "help":
                self.show_help()
        else:
            messagebox.showinfo("Conversion Complete", "The file conversion process has finished.")

        # Re-enable the Convert button and disable the Cancel button
        self.convert_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')

    def send_log_to_developer(self,log_path):
        # Function to handle the sending of log files to the developer
        # This is a placeholder for your actual sending logic, which might use email, FTP, HTTP POST, etc.
        print("Log would be sent to the developer.")
        to_email = "sivan.zusin@intel.com"
        subject = "LTK SPF Conversion Problem"
        body = "This is an automatically generated Email. The Log file and a sample of the problematic SPF files will be sent to the developer for debugging. A fixed will be soon provided to you.\n\nThanks."
        self.attachment_paths.append(log_path)
        send_email_with_attachments(to_email, subject, body, self.attachment_paths)

    def show_help(self):
        # Function to show help information
        messagebox.showinfo("Help", "Please contact support@example.com for help with conversion issues.")

    def stop_convertion(self):
        self.stop_requested = True  # Signal the thread to stop
        #self.conversion_thread.join()  # Wait for the thread to finish
        self.handle_error()
        self.cancel_button.configure(state='disabled')
        self.convert_button.configure(state='normal')


if __name__ == "__main__":
    original_stdout = sys.stdout
    root = tk.Tk()
    app = Converter_GUI(root)
    root.mainloop()
    sys.stdout = original_stdout