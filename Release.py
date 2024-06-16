import re
import os
import shutil

def validate_version(version_input):
    # Define regex pattern
    pattern = r'^\d+\.\d+\.\d+[a-z]?\d*$'

    # Check if version_input matches the pattern
    return re.match(pattern, version_input) is not None

def main():
    USER_INPUT = False
    if USER_INPUT:
        # Get the release version from user input
        while True:
            version_number = input("Enter the release version (format x.x.xY or x.x.x): ").strip()
            if validate_version(version_number):
                break
            else:
                print("Invalid version format. Please enter a valid version.")
    else:
        with open(r'LTK_SPF_Converter.py','r') as source:
            for line in source:
                if line.startswith('VERSION = '):
                    version_number = line.split(' ')[-1].strip().strip("'")

    # Get the current working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the module name and source paths relative to the current directory
    module_name = "LTK_SPF_Converter"
    icon_path = os.path.join(base_dir, "crown.ico")
    help_file = os.path.join(base_dir, "LTK_SPF_HELP.chm")
    history_file = os.path.join(base_dir, "ltk_spf_history.csv")
    script_path = os.path.join(base_dir, f"{module_name}.py")
    email_sender_path = os.path.join(base_dir, "compose_email.vbs")
    user_email_sender_path = os.path.join(base_dir, "compose_user_email.vbs")

    # Define the output directory relative to the current directory
    output_dir = os.path.join(base_dir, "Release", f"{module_name}_{version_number}")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run pyinstaller
    os.system(f'pyinstaller --noconfirm --onefile --windowed --icon "{icon_path}" --add-data "{icon_path};." --add-data "{help_file};." --add-data "{history_file};." "{script_path}" --distpath "{output_dir}"')

    # Copy additional files to the output directory
    shutil.copy(icon_path, output_dir)
    shutil.copy(help_file, output_dir)
    shutil.copy(email_sender_path, output_dir)
    shutil.copy(user_email_sender_path, output_dir)

    # Create empty history file
    with open(os.path.join(output_dir,"ltk_spf_history.csv"),'w') as h:
        pass

    # Delete the .spec file and the build folder
    spec_file = os.path.join(base_dir, f"{module_name}.spec")
    build_folder = os.path.join(base_dir, "build")
    os.remove(spec_file)
    shutil.rmtree(build_folder)

    print("Build and copy completed.")

if __name__ == "__main__":
    main()
