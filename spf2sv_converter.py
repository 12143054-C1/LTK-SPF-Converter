#############################
# Module name: spf2sv_converter.py
# Description: This module provides functions and classes to translate SPF files to PythonSV files.
#              It clones the file structure of the input directory to the output directory, applies
#              various modifications to the translated files, and logs the process. It supports optional
#              configuration for CPU generation and weekly folder creation.
#############################

import os, sys, datetime, re


def week_num():
    date = datetime.datetime.today()  # Replace with the desired date

    work_week = date.strftime("%W")
    week_day = (date.isoweekday() % 7) + 1  # Convert from ISO weekday (1-7) to custom weekday (0-6)
    if week_day == 1:
        work_week = str(int(work_week) + 1)
    year = str(date.year)[-2:]  # Extract the last two digits of the year

    date_format = "ww{}_{:d}'{}".format(work_week, week_day, year)
    return date_format

def tcss_add_phy_index_and_post_boot(file_path_,output_dir,conversion_time,CPUgen):
    def rewrite_file(file):
        lines = file.readlines()
        i=0
        for line in lines:
            # search for function line
            if line == 'def runConverted():\n':
                # insert variable to function line
                lines[i] = 'def runConverted(phy_index=0, post_boot_config = True):\n'
                break
            i+=1
        if CPUgen == 'LNL':
            parameters_select="""
    if post_boot_config:
        print("\\npost_boot_config - start")
        sv.socket0.soc.pmc.pmu.dfx_tcss_ctl.drv_tcss_hvmmode_en = 1
        print("\\npost_boot_config - end")

    if phy_index == 0:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg0_tap0.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.soc_regs_wrapper.tcss_phy_env_i_0
        mg_index='0'
        index='0'
    elif phy_index == 1:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo1.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo1.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg1_tap0.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.soc_regs_wrapper.tcss_phy_env_i_1
        mg_index='1'
        index='1'
    elif phy_index == 2:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_mg0_tap0.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.soc_regs_wrapper.tcss_phy_env_i_2
        mg_index='0'
        index='2'
                """
        elif CPUgen == 'PTL':
            parameters_select="""
    if post_boot_config:
        print("\\npost_boot_config - start")
        sv.socket0.soc.pmc.pmu.dfx_tcss_ctl.drv_tcss_hvmmode_en = 1
        print("\\npost_boot_config - end")

    if phy_index == 0:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg00.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.tcss_phy_env_i_0
        mg_index='0'
        index='0'
    elif phy_index == 1:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo1.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo1.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg10.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.tcss_phy_env_i_1
        mg_index='1'
        index='1'
    elif phy_index == 2:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_mg00.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.tcss_phy_env_i_2
        mg_index='0'
        index='2'
    elif phy_index == 3:
        path_to_cdu_apollo_taplinkcfg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo1.taplinkcfg
        path_to_cdu_apollo_usb4_phy_common_reg = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo1.usb4_phy_common_reg
        path_to_mg_tap_crsel = sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_1_mg10.crsel
        path_to_tcss_phy_env = sv.socket0.soc.tcss.tcss_phy_env_i_3
        mg_index='3'
        index='3'
                """
        lines.insert(i+1,parameters_select)
        if CPUgen == 'LNL':
            for line_num, line in enumerate(lines):
                lines[line_num] = lines[line_num].replace("(sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.taplinkcfg","(path_to_cdu_apollo_taplinkcfg")
                lines[line_num] = lines[line_num].replace('("kill_mg0_tap0_tclk_out"',r'("kill_mg%s_tap0_tclk_out"%mg_index')
                lines[line_num] = lines[line_num].replace('(sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.usb4_phy_common_reg','(path_to_cdu_apollo_usb4_phy_common_reg')
                lines[line_num] = lines[line_num].replace('(sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg0_tap0.crsel','(path_to_mg_tap_crsel')
                lines[line_num] = lines[line_num].replace('"TCSS/soc_regs_wrapper/tcss_phy_env_i_0','f"TCSS/soc_regs_wrapper/tcss_phy_env_i_{str(phy_index)}')
        elif CPUgen == 'PTL':
            for line_num, line in enumerate(lines):
                lines[line_num] = lines[line_num].replace("(sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.taplinkcfg","(path_to_cdu_apollo_taplinkcfg")
                lines[line_num] = lines[line_num].replace('("kill_mg0_tap0_tclk_out"',r'("kill_mg%s_tap0_tclk_out"%mg_index')
                lines[line_num] = lines[line_num].replace('(sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.usb4_phy_common_reg','(path_to_cdu_apollo_usb4_phy_common_reg')
                lines[line_num] = lines[line_num].replace('(sv.socket0.soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg00.crsel','(path_to_mg_tap_crsel')
                lines[line_num] = lines[line_num].replace('"TCSS/soc_regs_wrapper/tcss_phy_env_i_0','f"TCSS/soc_regs_wrapper/tcss_phy_env_i_{str(phy_index)}')

        file.close()
        #file_path1 = file_path.replace('.py','_CONVERTED.py')
        with open(file_path, 'w') as file:
            file.writelines(lines)
            file.close()

    def list_files_in_folder(folder_path):
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
        return file_list

    folder_path = output_dir
    files = [file_path_]
    files_to_process = []
    for file in files:
        file = os.path.basename(file)
        file = file.replace(".spf",".py")
        if 'tcss' in file or 'tc0' in file or 'tc1' in file or 'tc2' in file or 'tc3' in file:
            files_to_process.append(file)
    # process each file
    for file in files_to_process:
        file_path = os.path.join(folder_path, file)
        try:
            file_modification_time = os.path.getmtime(file_path)
        except:
            file_modification_time = os.path.getmtime(file_path.replace(".py","_DirectReg.py"))
        if file_modification_time > conversion_time:
            try:
                with open(file_path, 'r') as file:
                    rewrite_file(file)
            except:
                with open(file_path.replace(".py","_DirectReg.py"), 'r') as file:
                    rewrite_file(file)
            print("tcss post boot script added on: %s"%file_path)
    print("tcss_add_phy_index_and_post_boot DONE")

def edp_add_post_boot(file_path_,output_dir,conversion_time,CPUgen):
    def rewrite_file(file):
        lines = file.readlines()
        i=0
        for line in lines:
            # search for function line
            if line == 'def runConverted():\n':
                # insert variable to function line
                lines[i] = 'def runConverted(post_boot_config = False):\n'
                break
            i+=1
        parameters_select="""
    if post_boot_config:

        print("\\npost_boot_config - start")

        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane0_dig_pcs_xf_rx_ovrd_in_1 = 0
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane1_dig_pcs_xf_rx_ovrd_in_1 = 0
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane2_dig_pcs_xf_rx_ovrd_in_1 = 0
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane3_dig_pcs_xf_rx_ovrd_in_1 = 0
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane0_dig_pcs_xf_ate_ovrd_in = 0xaf
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane1_dig_pcs_xf_ate_ovrd_in = 0xaf
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane2_dig_pcs_xf_ate_ovrd_in = 0xaf
        sv.socket0.soc.edp_phy.dwc_usbc31dptxphy_phy_x4_ns.rawlane3_dig_pcs_xf_ate_ovrd_in = 0xaf

        print("\\npost_boot_config - end")

            """
        lines.insert(i+1,parameters_select)
        file.close()
        #file_path1 = file_path.replace('.py','_CONVERTED.py')
        with open(file_path, 'w') as file:
            file.writelines(lines)
            file.close()

    def list_files_in_folder(folder_path):
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
        return file_list

    folder_path = output_dir
    # get all files in the folder
    # files = list_files_in_folder(folder_path) ### LEGACY
    files = [file_path_]
    # filter files based on their name pattern
    pattern = r".*eDP.*\.py$"
    files_to_process = [f for f in files if re.match(pattern, f)]
    # process each file
    for file in files_to_process:
        file_path = os.path.join(folder_path, file)
        file_modification_time = os.path.getmtime(file_path)
        if file_modification_time > conversion_time:
            with open(file_path, 'r') as file:
                rewrite_file(file)
            print("eDP post boot script added on: %s"%file_path)
    print("edp_add_post_boot DONE")


class run():
    """
    Translate SPF files to PythonSV file.\n
    Clones file stracture of the input directory to the output directory.\n
    Usage:
        run(input_dir,[optional] output_dir,[optional] CPUgen)\n
        On default: output_dir = 'C:\input_dir\TRANSLATED\\'\n
                    CPUgen = 'LNL'\n
        CPUgen can be ['LNL' , 'MTL-P']
    """

    def __init__(self,direct_reg,conversion_time,log_file_path,_week_folder_en, _input_dir,_input_file, _output_dir="",CPUgen = "PTL"):
        self.log_file_path = log_file_path
        self.conversion_time = conversion_time
        self.input_file = _input_file
        self.input_dir = _input_dir
        if _output_dir == "":
            self.output_dir = _input_dir + "\\TRANSLATED"
        elif _week_folder_en == True:
            self.output_dir = _output_dir + "\\" + week_num()
        elif _week_folder_en == False:
            self.output_dir = _output_dir
        self.CPUgen = CPUgen
        self.direct_reg = direct_reg
        self.run_translation()
        tcss_add_phy_index_and_post_boot(_input_file,self.output_dir,self.conversion_time,self.CPUgen)
        edp_add_post_boot(_input_file,self.output_dir,self.conversion_time,self.CPUgen)

    def run_translation(self):
        # root_dirs = [ r"C:\pythonsv\lunarlake\debug\domains\hsio_dv\Display",
        # r"C:\spf_parsing\SPFs"]

        # get the current working directory
        # cwd = os.getcwd()
        # print(cwd)

        # add the current working directory to the Python path
        # sys.path.append(cwd)

        # # open file to save used taps
        # used_taps_file = open(r"C:\SPFs\used_taps.csv", "w",newline="")
        # writer = csv.writer(used_taps_file)
        # writer.writerow(["file_name", "taps"])
        # import the file using the file name

        sys.path.append(os.getcwd())
        #sys.path.append(r"C:\hamo_git\sio\LNL\sio_dv\spfs_source")
        import lnl_spf_2_pythonsv_script_BlackBox_Advanced as C1converter

        if self.input_file:
            input_dir = os.path.dirname(self.input_file)
            A = C1converter.Command(input_dir, self.input_file, self.output_dir, self.CPUgen, self.direct_reg)
        else:
            # use the os.walk() function to traverse the directory tree
            for dir_path, subdirs, files in os.walk(self.input_dir):
                # loop through all the files in the current directory
                for file_name in files:
                    # use the os.path.join() function to get the full path to the file
                    file_path = os.path.join(dir_path, file_name)
                    A = C1converter.Command(self.input_dir, file_path, self.output_dir, self.CPUgen, self.direct_reg)
                    # taps = list(A.returnTapsUsed())
                    # taps.insert(0,file_name)
                    # writer.writerow(taps)
