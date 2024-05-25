import os

class Debugger:
    def __init__(self):
        """
        Tools for LTK converter
        """
        
    def get_all_taps(self, folder_path):
        self.folder_path = folder_path
        tap_names = set()
        register_names = set()

        # Read all .spf files in the folder
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.spf'):
                with open(os.path.join(self.folder_path, filename), 'r') as file:
                    for line in file:
                        # Find tap names
                        if 'focus_tap ' in line:
                            start_index = line.find('focus_tap ') + len('focus_tap ')
                            end_index = line.find(';', start_index)
                            if end_index != -1:
                                tap_name = line[start_index:end_index].strip()
                                tap_names.add(tap_name)
                        
                        # Find register names
                        if 'set ' in line and '->' in line:
                            start_index = line.find('set ') + len('set ')
                            end_index = line.find('->', start_index)
                            if end_index != -1:
                                register_name = line[start_index:end_index].strip()
                                register_names.add(register_name)
        
        # Write unique tap names to taps.txt
        with open(r'sio\LNL\sio_dv\users\szusin\taps.txt', 'w') as taps_file:
            for tap_name in sorted(tap_names):  # Sort to make it organized
                taps_file.write(tap_name + '\n')
        
        # Write unique register names to regs.txt
        with open(r'sio\LNL\sio_dv\users\szusin\regs.txt', 'w') as regs_file:
            for register_name in sorted(register_names):  # Sort to make it organized
                regs_file.write(register_name + '\n')

    def generate_sv_copypasta(self):
        regs = []
        with open(r'sio\LNL\sio_dv\users\szusin\regs.txt', 'r') as regs_file:
            regs = regs_file.readlines()
            for i,reg in enumerate(regs):
                regs[i] = f'print(sv.socket0.soc.search("{reg[:-1]}"))\n'
        with open(r'sio\LNL\sio_dv\users\szusin\copypasta_regs.txt', 'w') as regs_file:
            regs_file.writelines(regs)
    
    def output_dict_from_copypasta_response(self):
        taps = set()
        with open(r'sio\LNL\sio_dv\users\szusin\copypasta_response.txt', 'r') as response_file:
            lines = response_file.readlines()
            for line in lines:
                tap = line.split("'")[1]
                tap = tap.split(".")[:-1]
                tap_ = ""
                for t in tap:
                    tap_ += f"{t}."
                tap = tap_[:-1]
                taps.add(tap)
        self.sv_taps = taps

    def create_tap_dict(self):
        self.output_dict_from_copypasta_response()
        spf_taps = []
        with open(r'sio\LNL\sio_dv\users\szusin\taps.txt', 'r') as taps_file:
            spf_taps = taps_file.readlines()
        content = "\n"
        for spf_tap in spf_taps:
            for sv_tap in self.sv_taps:
                a = spf_tap.lower()[:-6]
                b = spf_tap.lower()[:-5]
                if a in sv_tap or b in sv_tap:
                    content += f"r'{spf_tap[:-1]}' : r'{sv_tap}',\n"
        codelines = "self.focus_tap_dict = {%s}"%content
        print(codelines)
        
deb = Debugger()

deb.get_all_taps(r'C:\Users\szusin\OneDrive - Intel Corporation\Documents\PTL\SPFs\TCSS')
deb.generate_sv_copypasta()
deb.create_tap_dict()
