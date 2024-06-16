#############################
# Module name: lnl_spf_2_pythonsv_script_BlackBox_Advanced.py
# Description: This module is designed to convert SPF (Serial Programming File) scripts into
#              PythonSV scripts for use in validation and testing environments.
#              It supports direct register access, comparison, and manipulation of register fields,
#              and includes functionality for handling different CPU generations and their specific
#              register access methods. The script also provides utilities for timing control, comment handling,
#              and conditional execution based on register values. It is tailored for use in Intel's validation processes,
#              particularly for the Lunar Lake (LNL) and other specified CPU generations.
#############################

#---------######################################################################
# IMPORTS ######################################################################
#---------######################################################################
import sys, os, time, math, re


#---------######################################################################
# GLOBALS ######################################################################
#---------######################################################################



#-----------####################################################################
# FUNCTIONS ####################################################################
#-----------####################################################################
def get_and_set_IO(dirpath,filename,path_offset):
    input_path = os.path.join(dirpath, filename)
    out_file_name = input_path.split("\\")[-1].replace(".spf",".py").replace(".SPF",".py")
    output_path_arrL = input_path.split("\\")[:path_offset]
    output_path_arrR = input_path.split("\\")[path_offset:-1]
    output_path = ""
    for pathBit in output_path_arrL:
        output_path += pathBit+"\\"
    output_path += "TRANSLATED\\"
    try:
        os.mkdir(output_path)
    except:
        pass
    for pathBit in output_path_arrR:
        output_path += pathBit+"\\"
        try:
            os.mkdir(output_path)
        except:
            pass
    output_path += out_file_name
##    print ("INPUT:    "+input_path)
##    print ("OUTPUT:   "+output_path)
    paths = {   "input"  : input_path,
                "output" : output_path}
    return paths

def context_search_and_print(string, directory, Context_size):
    def number_helper_10000(number):
        num_len = len(str(number))
        space = " "
        for i in range(5-num_len):
            space += " "
        return(str(number) + space)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".spf"):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if re.search(string, line):
                        print(file_path)
                        print("Line Numbers: %s - %s"%(i-Context_size if  i-Context_size > 0 else 0,i+Context_size if i+Context_size < len(lines) else len(lines)))
                        # 10 lines before
                        for j in range(Context_size+1,1,-1):
                            if i-j >=0:
                                print(number_helper_10000(i-j+1) + ": ", lines[i-j],end="")
                        # The Line
                        print(number_helper_10000(i) + ">>",line,end="")
                        # 10 lines after
                        for j in range(1,Context_size+1):
                            if i+j < len(lines):
                                print(number_helper_10000(i+j+1) + ": ", lines[i+j],end="")
                        #input("Press Enter to continue...")
                        return








#-------------##################################################################
# DEFINITIONS ##################################################################
#-------------##################################################################







class Command():
    def __init__(self, _Root_Path="", _FilePath = "",_Output_Root_Dir = "", _CPU_Gen = "PTL",direct_reg = False):
        import sys, os, time, math
        self.spf_comments = True
        self.labels = True
        self.focus_tap_sv = []
        self.param_read = []
        self.param_write = []
        self.prev_reg = ""
        self.reg_name = ""
        self.full_reg_name = ""
        self.prev_row = ""
        self.flush_flag = False
        self.print_last_label = False
        self.itpp_reg_name = ""
        self.comment_reg_name_flag = 0
        self.itpp_compare_targets = ""
        self.FilePath = _FilePath
        self.Root_Path = _Root_Path
        self.Output_Root_Dir = _Output_Root_Dir
        self.CPU_Gen =_CPU_Gen
        self.svPath = r"sv.socket0."
        if self.CPU_Gen == "LNL":
            self.focus_tap_dict = {
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_CDU_APOLLO0_TAP"    : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_CDU_APOLLO1_TAP"    : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo1.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_CDU_APOLLO0_TAP"    : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_CDU_APOLLO1_TAP"    : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo1.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG0_TAP0"           : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg0_tap0.",
                r"TPSB_STAP"                                          : r"soc.taps.tpsb.",
                r"IPU_STAP"                                           : r"soc.taps.ipu.",
                r"NPK_STAP"                                           : r"soc.taps.npk.",
                r"GPIOCOM0_STAP"                                      : r"soc.taps.gpio.com0.sb.",
                r"GPIOCOM1_STAP"                                      : r"soc.taps.gpio.com1.sb.",
                r"GPIOCOM3_STAP"                                      : r"soc.taps.gpio.com3.sb.",
                r"GPIOCOM4_STAP"                                      : r"soc.taps.gpio.com4.sb.",
                r"GPIOCOM5_STAP"                                      : r"soc.taps.gpio.com5.sb.",
                r"TAP2IOSFSB_GP"                                      : r"cdie.taps.cdie_tap2iosfsb_gp.",
                r"PMC_HVM_STAP"                                       : r"soc.taps.pmc_hvm.",
                r"DFX_PAREDP_STAP"                                    : r"soc.taps.dfx_paredp.",
                r"DFX_PARPXPBG5PHY_STAP"                              : r"soc.taps.dfx_parpxpbg5phy.",
                r"DFX_PARPXPAMPPHY_STAP"                              : r"soc.taps.dfx_parpxpampphy.",
                r"TAM_STAP"                                           : r"soc.taps.tam."
                }
        elif self.CPU_Gen == "MTL1":
            self.focus_tap_dict = {
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_CDU_APOLLO0_TAP"    : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_CDU_APOLLO0_TAP"    : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG0_TAP0"           : r"soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg0_tap0.",
                r"TPSB_STAP"                                          : r"soc.north.taps.tap2iosfsb_gp.", # r"soc.south.taps.tpsb.",
                r"IPU_STAP"                                           : r"soc.taps.ipu.",
                r"NPK_STAP"                                           : r"soc.taps.npk.",
                r"GPIOCOM0_STAP"                                      : r"soc.taps.gpio.com0.sb.",
                r"GPIOCOM1_STAP"                                      : r"soc.taps.gpio.com1.sb.",
                r"GPIOCOM3_STAP"                                      : r"soc.taps.gpio.com3.sb.",
                r"GPIOCOM4_STAP"                                      : r"soc.taps.gpio.com4.sb.",
                r"GPIOCOM5_STAP"                                      : r"soc.taps.gpio.com5.sb.",
                r"TAP2IOSFSB_GP"                                      : r"soc.north.taps.tap2iosfsb_gp.",
                r"PMC_HVM_STAP"                                       : r"soc.south.taps.pmc_hvm."
                }
        elif self.CPU_Gen == "MTL-P":
            self.focus_tap_dict = {
                r"TPSB_STAP"       : r"ioe.taps.tpsb.",
                r"PMC_HVM_STAP"    : r"ioe.taps.pmc_debug.",
                r"DFX_PAREDP_STAP" : r"ioe.taps.dfx_parioepptmpphy.",
                r"TAP2IOSFSB_GP"   : r"soc.north.taps.tap2iosfsb_gp.", # or "gcd.taps.tap2iosfgp." or "compute0.taps.tap2iosfgp."
                r"IPU_STAP"        : r"NON EXISTANT!",
                r"NPK_STAP"        : r"soc.south.taps.npk.", # or 'soc.south.taps.npk.'
                r"GPIOCOM0_STAP"   : r"soc.south.taps.gpiocom0.",
                r"GPIOCOM1_STAP"   : r"soc.south.taps.gpiocom1.",
                r"GPIOCOM3_STAP"   : r"soc.south.taps.gpiocom3.",
                r"GPIOCOM4_STAP"   : r"soc.south.taps.gpiocom4.",
                r"GPIOCOM5_STAP"   : r"soc.south.taps.gpiocom5.",
                r"DFX_PARPXPBG5PHY_STAP" : r"ioe.taps.dfx_parioepg5phy.",
                r"DFX_PARPXPAMPPHY_STAP" : r"NON EXISTANT!",
                r"TAM_STAP"        : r"ioe.taps.tam.", # or "soc.south.taps.tam."
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_CDU_APOLLO0_TAP" : r"ioe.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_CDU_APOLLO0_TAP" : r"ioe.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG0_TAP0"        : r"ioe.taps.dfx_par_iom_taplinknw_phy_fia_0_mg0_tap0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_MG0_TAP0"        : r"ioe.taps.dfx_par_iom_taplinknw_phy_fia_1_mg0_tap0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG1_TAP0"        : r"ioe.taps.dfx_par_iom_taplinknw_phy_fia_0_mg1_tap0.",
                r"DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_MG1_TAP0"        : r"ioe.taps.dfx_par_iom_taplinknw_phy_fia_1_mg1_tap0."
                }
        elif self.CPU_Gen == "PTL":
            self.focus_tap_dict = {
                r'DFX_PARISCLK_STAP'                               : r'soc.taps.dfx_parisclk.',
                r'IPU_STAP'                                        : r'soc.taps.ipu.',
                r'ISCLK_STAP'                                      : r'soc.taps.isclk.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG0_TAP0'        : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg00.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG1_TAP0'        : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg10.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_MG0_TAP0'        : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_1_mg00.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_MG1_TAP0'        : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_1_mg10.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_CDU_APOLLO0_TAP' : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo0.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_CDU_APOLLO1_TAP' : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_0_cdu_apollo1.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_CDU_APOLLO0_TAP' : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo0.',
                r'DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_CDU_APOLLO1_TAP' : r'soc.taps.dfx_par_iom_taplinknw_phy_fia_1_cdu_apollo1.',
                r'TPSB_STAP'                                       : r'soc.taps.tpsb.',
                r'DFX_PAR_IOM_TAPLINKNW_IOM_IOM_AONGTAP'           : r'soc.taps.dfx_par_iom_taplinknw_iom_iom_aong.',
                r'GLUE_DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG0_TAP0'   : r'soc.taps.cltap.', #### !!!!!! IN QUESTION NEED TO APPROVE WITH MITRANI
                r'GLUE_DFX_PAR_IOM_TAPLINKNW_PHY_FIA_0_MG1_TAP0'   : r'soc.taps.cltap.', #### !!!!!! IN QUESTION NEED TO APPROVE WITH MITRANI
                r'GLUE_DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_MG0_TAP0'   : r'soc.taps.cltap.', #### !!!!!! IN QUESTION NEED TO APPROVE WITH MITRANI
                r'GLUE_DFX_PAR_IOM_TAPLINKNW_PHY_FIA_1_MG1_TAP0'   : r'soc.taps.cltap.', #### !!!!!! IN QUESTION NEED TO APPROVE WITH MITRANI
                }
            ### I M P O R T A N T !!!!!!!! YOU NEED TO ADD '.' AT THE END OF THE TRANSLATED TAP NAME, AND ALSO PAY ATTENTION TO THE FIRST ELEMENT IN THE HIERARCHY.
        self.taps_used = set()
        self.direct_reg = direct_reg
        self.reg_address = ""
        self.direct_command = ""
        self.direct_write_flush = True
        self.data = ""
        self.compare_flag = False
        if self.direct_reg == True:
            self.iom_block = True
        else:
            self.iom_block = False
        self.run()


    def prRed(self,skk):
        print("\033[91m {}\033[00m" .format(skk))
    def prGreen(self,skk):
        print("\033[92m {}\033[00m" .format(skk))
    def prYellow(self,skk):
        print("\033[93m {}\033[00m" .format(skk))

    def printC1(self,a,file):
##        print(a)
        file.write("    " + a + "\n")

    def bitfield(self,n):
        a = self.bitfield_rev(n)
        b= []
        for i in a:
            b.insert(0,i)
        return b

    def bitfield2(self,n):
        a = self.bitfield2_rev(n)
        b= []
        for i in a:
            b.insert(0,i)
        return b

    def bitfield2_rev(self,n):
        if type(n) is not str:
            n = hex(n)
        if n[1] == "x":
            num = int(n,16)
        elif n[1] != "b":
            num = int(n)
        if n[1] != "b":
            bitArr = ["1" if digit=='1' else "0" for digit in bin(num)[2:]]
            return bitArr
        else:
            a = []
            for digit in n[2:]:
                a.append(digit)
            return a

    def bitfield_rev(self,n):
        if type(n) is not str:
            n = hex(n)
        output = []
        mid=""
        if n[1] == "x":
            for fourbit in n[2:]:
                mid += str(bin(int(fourbit, 16))[2:].zfill(4))
            return self.bitfield_rev("0b" + mid)
        elif n[1] == "b":
            for bit in n[2:]:
                output.append(bit)
            return output

    def bitArr2hex(self,bitArr):
        out_str = ""
        for bit in reversed(bitArr):
            out_str += bit
        return int(out_str,2)

    def reg_compare(self,reg,data):
        for i in range(len(data)):
##            print(i)
##            print("reg =     {}".format(reg))
##            print("reg[i] =  {}".format(reg[i]))
##            print("data =    {}".format(data))
##            print("data[i] = {}".format(data[i]))
            if data[i] == "x" or data[i] == "X" or reg[i] == data[i]:
                continue
            else:
                return False
        return True

    def comp_command(self,row_num, row:str, output,spf_file):
        if row.startswith("label"):
            if (self.labels == True):
                # Need to add comment "label: ..."
                x = "##>>> SPF Label:    {}".format(row[6:-2])
                self.printC1(x,output)
            self.printC1("""last_label = '{}'""".format(row.split('"')[1]),output)
            self.printC1("print(last_label)",output)
            self.print_last_label = True
            self.prev_row = row
            return
    
        if self.iom_block == True:
            if row.startswith("pass itpp"):
                self.iom_block == False
            else:
                self.prev_row = row
                return

        # RETURN ERROR ON MISSING REG NAME WHEN DIRECT WRITING TO REG
        if self.direct_reg == True and self.prev_row.startswith('pass itpp') and 'CMD_WRITE' in self.prev_row:
            if not (row.startswith('pass itpp') and 'REG_NAME' in row ):
                output.close()
                print(spf_file)
                print(f"row number: {row_num}")
                print(self.prev_row)
                print(row)
                print(">>> Error: No reg names!")
                raise error_msg("no reg names")

        if row.startswith(r"focus_tap"):
            # Set focus tap. goes to: sv.socket0.soc.taps.<focus_tap_sv>.register
            self.focus_tap_sv = []
            taps = row.replace("focus_tap ","").split(";")[0]
            if " " in taps:
                taps = taps.split(" ")
            elif "," in taps:
                taps = taps.split(",")
            else:
                taps = [taps]
            for tap in taps:
                try:
                    self.focus_tap_sv.append(self.focus_tap_dict[tap])
                    self.taps_used.add(self.focus_tap_dict[tap])
                except KeyError as e:
                    print(" >>> Error: Tap not found: " + str(e))
                    context_search_and_print(tap, self.Root_Path, 10)
                    return 1
                

        elif row.startswith(r"set"):
            # if self.direct_reg == True:
            #     if self.direct_command == True:
            #         self.direct_command = False
            #         if row.startswith("set CRSEL[15:0]"):
            #             data = row.split(' = ')[1].strip(";\n")
            #             #convert bin or hex to hex string
            #             if data[1] == 'b':
            #                 data = hex(int(data[2:],2))
            #             elif data[1] == 'h':
            #                 data = hex(int(data[2:],16))
            #             self.printC1("exec('sv.socket0.soc." + self.itpp_reg_name[:37] + r"%s" +self.itpp_reg_name[38:] + " = " + self.data + r"'%index)", output)
            #             return
            #     else:
            #         pass

            if self.direct_reg == True:
                if row.startswith("set CRSEL"):
                    self.direct_write_flush = False
                    self.prev_row = row
                    return
            ##save reg to param_read
            self.reg_name = row.split(" ")[1].split("[")[0].split("->")[0].replace(" ","").lower()
            if self.prev_reg != self.reg_name:
                if self.flush_flag == False and self.prev_reg != "":
                    for tap in range(len(self.focus_tap_sv)):
                        self.printC1("reg{}.flush()".format(tap),output)
                    self.printC1("\n    \n    ",output)
                self.prev_reg = self.reg_name
                ## Init new Reg
                self.printC1("##### WRITE TO REGISTER #####",output)
                for tap in range(len(self.focus_tap_sv)):
                    self.full_reg_name = self.svPath + self.focus_tap_sv[tap] + self.reg_name

                    edp_direct_access_rule = (self.direct_reg == True) and (self.focus_tap_sv[tap] == 'soc.taps.tpsb.' and self.reg_name == 'sbmsggo')
                    tcss_direct_access_rule = (self.direct_reg == True) and (self.focus_tap_sv[tap] in[
                                                                                                    'soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg0_tap0.',
                                                                                                    'soc.taps.dfx_par_iom_taplinknw_phy_fia_0_mg1_tap0.',
                                                                                                    'soc.taps.dfx_par_iom_taplinknw_phy_fia_1_mg0_tap0.']
                                                                                                    and self.reg_name == 'crsel')
                    '''
                    if (self.direct_reg == True) and (edp_direct_access_rule == True): #check for direct register access flag
                        #derive the direct reg access from the tap name and the register address
                        while(not ('set SBMSGGO[63:48] = ' in row)):
                            row = spf_file.readline()
                        if 'set SBMSGGO[63:48] = ' in row:
                            self.reg_address = hex(int(row.split(" = 'b")[1].split(';')[0], 2))
                            #self.printC1("reg{0} = svReg({1})".format(tap,reg_address),output)
                            row = spf_file.readline()
                        if 'set SBMSGGO[95:64] = ' in row: # We write to the register
                            data = hex(int(row.split(" = 'b")[1].split(';')[0], 2))
                            self.printC1(f"reg[{self.reg_address}] = {data}",output)     ### TBD: replace  reg[{reg_address}]  with real data from CRIF
                            print (f"reg_name= {self.full_reg_name}, reg_address= {self.reg_address}, data= {data}")
                        else: #we later compare or capture this register
                            print (f"reg_name= {self.full_reg_name}, reg_address= {self.reg_address}, compare_mode")
                        row = spf_file.readline()
                        '''

                    self.printC1("reg{0} = svReg({1})".format(tap,self.full_reg_name),output)
                        
            ##get the indexes of the bits we want to write
            if "'b" in row or "'h" in row:
                data = "0" + row.split("=")[1].split(";")[0].split(r"'")[1].replace("h","x")
            else: 
                data = hex(int(row.split("=")[1].split(";")[0]))
            if "[" in row.split(r"#")[0].split(r"=")[0]:
                indexes = row.split("[")[1].split("]")[0]
                if ":" in indexes:
                    sv_field = (int(indexes.split(":")[0]) ,int(indexes.split(":")[1]) )
                else:
                    sv_field = (int(indexes), int(indexes))
                for tap in range(len(self.focus_tap_sv)):
                    self.printC1("""reg%s.storeField(%s,"%s")""" %(tap,sv_field,data),output)
            elif "->" in row.split(r"#")[0].split(r"=")[0]:
                reg_and_field = row.replace("set ", "").split("=")[0].replace(" ","")
                sv_field = reg_and_field.split("->")[1].lower()
                for tap in range(len(self.focus_tap_sv)):
                    self.printC1("""reg%s.storeField("%s","%s")""" %(tap,sv_field,data),output)
            self.flush_flag = False

        elif row.startswith("flush"):
            self.flush_flag = True
            if self.direct_write_flush == False:
                self.direct_write_flush = True
                self.direct_command  = ""
                self.prev_row = row
                return
            elif self.prev_row.split(" ")[0] == "set" or self.prev_row.startswith("#") or self.prev_row.startswith("mask") or self.prev_row.startswith("capture") or self.prev_row == ("\n"):
                for tap in range(len(self.focus_tap_sv)):
                    self.printC1("reg{}.flush()".format(tap),output)
                self.printC1("\n    \n    ",output)
            elif self.prev_row.split(" ")[0] == "compare":
                pass
            else:
                self.printC1("### ERROR Flush not recognized ###",output)
                self.printC1("###   >>>"+self.prev_row,output)
                self.printC1("""print("### ERROR Flush not recognized ###")""",output)

        elif row.startswith(r"compare SBMSGRSP->STATUS") or row.startswith(r"compare TAP2APBR_GO->ACK") or row.startswith(r"compare TAP2APBR_GO->ERROR") or row.startswith(r"compare TAP2APBR_GO->ERROR"):  ### Ignore SideBand Status bit
            pass

        elif row.startswith("compare"):
            self.printC1("###### " + row.split(";")[0] + " #####",output)
            ##save reg to param_read
            self.reg_name = row.split(" ")[1].split("[")[0].split("->")[0].replace(" ","").lower()
            if self.prev_reg != self.reg_name:
                self.prev_reg = self.reg_name
                ## get LIVE register size
                if len(self.focus_tap_sv) > 1:
                    input("Comparison of more than one tap!!!")
                self.full_reg_name = self.svPath + self.focus_tap_sv[0] + self.reg_name
                self.printC1("reg0 = svReg({})".format(self.full_reg_name),output)
            # if self.print_last_label:
            #     self.printC1("print(last_label)  #functional when running in sv",output)
            #     self.print_last_label = False
            data = "0" + row.split("=")[1].split(";")[0].split(r"'")[1].replace("h","x")
            ##get the indexes of the bits we want to write
            if "[" in row.split(r"#")[0].split(r"=")[0] and "->" in row.split(r"#")[0].split(r"=")[0]:   ####### NEW CASE
                # a new creature
                indexes = row.split("[")[1].split("]")[0]
                if ":" in indexes:
                    sv_field_i = (int(indexes.split(":")[0]) ,int(indexes.split(":")[1]) )
                else:
                    sv_field_i = (int(indexes), int(indexes))
                reg_and_field = row.replace("set ", "").split("=")[0].replace(" ","")
                sv_field = (reg_and_field.split("->")[1].lower().split("[")[0],sv_field_i[0],sv_field_i[1])
                self.printC1("""reg0.compare(%s,"%s","%s","%s")\n    \n""" %(sv_field, data,self.itpp_reg_name,self.itpp_compare_targets),output)
            elif "[" in row.split(r"#")[0].split(r"=")[0]:           ########   OK CASE   #################################
                indexes = row.split("[")[1].split("]")[0]
                if ":" in indexes:
                    sv_field = (int(indexes.split(":")[0]) ,int(indexes.split(":")[1]) )
                else:
                    sv_field = (int(indexes), int(indexes))
                self.printC1("""reg0.compare(%s,"%s","%s","%s")\n    \n""" %(sv_field, data,self.itpp_reg_name,self.itpp_compare_targets),output)
            elif "->" in row.split(r"#")[0].split(r"=")[0]:      ################## OK CASE ###############################
                reg_and_field = row.replace("set ", "").split("=")[0].replace(" ","")
                sv_field = reg_and_field.split("->")[1].lower()
                self.printC1("""reg0.compare("%s","%s","%s","%s")\n    \n""" %(sv_field, data,self.itpp_reg_name,self.itpp_compare_targets),output)

        elif row.startswith("cycle"):
            # Need to call self.cycle("value in row")
            try:
                delay_time = int(row.split("cycle")[1].strip().split(";")[0])
            except:
                pass
            ####### Checked w/Idan: It's 1 Cycle of 400MHz Clock... well, let's assume 1 Cycle is 10 microseconds #########
            delay_out = "time.sleep(%s)\n    \n    "%(delay_time/100000)
            self.printC1("### " + row[:-2], output)
            self.printC1(delay_out,output)

        elif row.startswith("mask"):
            # non relevant for sv
            pass

        elif row.startswith("capture"): ### UPDATE   self.itpp_reg_name   AND   self.itpp_compare_targets   DATA!!!
            pass
            # ##save reg to param_read
            # if len(self.focus_tap_sv) > 1:
            #     input("Capture of more than one tap!!!")
            # self.reg_name = row.split(" ")[1].split("[")[0].split("->")[0].replace(" ","").lower()
            # if self.prev_reg != self.reg_name:
            #     self.prev_reg = self.reg_name
            #     ## get LIVE register size
            #     self.full_reg_name = self.svPath + self.focus_tap_sv[0] + self.reg_name
            #     self.printC1("##### CAPTURE REGISTER (Print it's value) #####\n    reg0 = svReg({})".format(self.full_reg_name),output)
            # ##get the indexes of the bits we want to write
            # if "[" in row.split(r"#")[0].split(r"=")[0] and "->" in row.split(r"#")[0].split(r"=")[0]:
            #     reg_and_field = row.replace("set ", "").split("=")[0].split(";")[0].strip(" ")
            #     sv_field = reg_and_field.split("->")[1].lower()
            # elif "[" in row.split(r"#")[0].split(r"=")[0]:
            #     indexes = row.split("[")[1].split("]")[0]
            #     if ":" in indexes:
            #         sv_field = str((int(indexes.split(":")[0]) ,int(indexes.split(":")[1]) ))
            #     else:
            #         sv_field = (indexes, indexes)
            #     self.printC1("""reg0.capture(%s)""" %(sv_field),output)
            # elif "->" in row.split(r"#")[0].split(r"=")[0]:
            #     reg_and_field = row.replace("set ", "").split("=")[0].split(";")[0].strip(" ")
            #     sv_field = reg_and_field.split("->")[1].lower()
            #     self.printC1("""reg0.capture("%s")""" %(sv_field),output)

            self.flush_flag = False

        elif row.startswith('#') or row.startswith('@') or row.startswith("comment") or row.startswith("//"):
            # SPF Comment
            if self.spf_comments == True:
                x="##### SPF Comment:    {}".format(row[:-2])
                self.printC1(x,output)
            if (self.comment_reg_name_flag > 0) or ("# Reg: " in row): ## Enter into comment_reg_indicator mode
                if "# Reg: " in row:
                    self.comment_reg_name_flag = 6
                    self.printC1("""print('%s')"""%row[2:-2],output)
                else:
                    self.comment_reg_name_flag = self.comment_reg_name_flag - 1
                    self.printC1("""print('%s')"""%row[2:-2],output)

        elif row.startswith("pass itpp"):
            x="# {}".format(row[:-2])
            self.printC1(x,output)
            # Objective: Save last REG_NAME and display it when comparing
            if self.direct_reg == True: #tap2cri: (Address 2'b00, Write 2'b01, Data 2'b01, Read 2'b11)
                if row.startswith('pass itpp') and "tap2cri:COMPARE" in row:
                    self.compare_flag = True
                if row.startswith('pass itpp "#    DATA'):
                    self.data = row.split(' = ')[1].strip('";\n')
                    if self.compare_flag == True:
                        self.prev_row = row
                        return
                    #convert bin or hex to hex string
                    if self.data[1] == 'b':
                        self.data = hex(int(self.data[2:],2))
                    elif self.data[1] == 'h':
                        self.data = hex(int(self.data[2:],16))

                if 'CMD_WRITE' in row:
                    command = row.split("'b")[1].split('";')[0]
                    if command == '00': # Address
                        self.direct_command = ""
                    elif command == '01': # Write
                        self.direct_command = "w"
                    elif command == '10': # Data
                        self.direct_command = ""
                    elif command == '11': # Read
                        self.direct_command = "r"
                        
                if 'REG_NAME' in row:
                    self.direct_write_flush = False
                    
                    self.itpp_reg_name = row.split(" = ")[1].strip('";\n')
                    pattern = r'[A-Z]{2}.*'
                    a = re.search(pattern, self.itpp_reg_name.split("=>")[1])
                    a = a.group()
                    self.itpp_reg_name = self.itpp_reg_name.split("MemSpace")[0] + a
                    self.itpp_reg_name = self.itpp_reg_name.lower().replace('/','.')
                    if self.compare_flag == True:
                        self.printC1("reg0 = svReg(path_to_tcss_phy_env{})".format(self.itpp_reg_name.split('tcss_phy_env_i_')[1][1:]),output)
                        reg_numbits = """reg0.regSize - 1"""
                        self.printC1("""exec('reg0.compare((%s,0),"%s","%s","%s")'%sindex)\n    \n""" %(reg_numbits, self.data.replace("'","0"), self.itpp_reg_name[:37] + r"%s" +self.itpp_reg_name[38:], "all",r"%"),output)
                        self.compare_flag =False
                        self.prev_row = row
                        return
                    if self.direct_command == "w":
                        self.printC1("exec('sv.socket0.soc." + self.itpp_reg_name[:37] + r"%s" +self.itpp_reg_name[38:] + " = " + self.data + r"'%index)", output)
                        self.direct_command = ""
                        self.direct_write_flush = False
                    elif self.direct_command == 'r':
                        self.printC1("exec('sv.socket0.soc." + self.itpp_reg_name[:37] + r"%s" +self.itpp_reg_name[38:] + r".show'%index)", output)
            
            
            else:
                if "REG_NAME" in row:
                    self.itpp_reg_name = row.split(" = ")[1].strip('";\n')
                elif "COMPARE_TARGETS" in row:
                    self.itpp_compare_targets = row.split("COMPARE_TARGETS = ")[1].strip('";\n')

        elif row.startswith("\n"):
            pass

        else:
            error_msg = """

###UNRECOGNIZED FORMAT!!!!!!#######
#
#   >>>{}<<<#
###################################

""".format(row.strip("\n"))
            self.printC1(error_msg,output)


        self.prev_row = row

    def run(self):
        def define_output_path():
            output_name = self.Output_Root_Dir + self.FilePath.replace(self.Root_Path,"").replace(".spf",".py").replace(".SPF",".py")
            abc = output_name
            abc2 = ""
            for i in abc.split("\\")[:-1]:
                abc2 += i + "\\"
                try:
                    os.mkdir(abc2[:-1])
                except:
                    pass
            if self.direct_reg == True:
                output_name = output_name.replace(".py","_DirectReg.py")
            return output_name

        def modify_line_spf_py(line:str):
            line.replace(".spf",".py")
            return line

        input_name = self.FilePath

        # Handle _FILE_NAMES.txt
        if input_name.endswith("output.txt"):
            output_name = define_output_path()
            with open(input_name, 'r') as src_file:
                with open(output_name, 'w') as dest_file:
                    for line in src_file:
                        dest_file.write(modify_line_spf_py(line))

        if not (input_name.endswith(".spf") or input_name.endswith(".SPF")):
            return
        output_name = define_output_path()
        if os.path.exists(output_name):
            os.remove(output_name)
        output = open(output_name,"w")
        spf_file = open(input_name,"r")


        # print the file name to the log
        print(output_name,end="")

        base_settings = """
import sys, os, time, numpy
import namednodes

## FOR DEBUG:
namednodes.sv.get_all()
sv = namednodes.sv
##from lunarlake.debug.domains.sio_dv import pysv_loader
##sv = pysv_loader.object_singleton.object

##class PythonSvSingleton:
##    _instance = None
##
##    def __new__(cls, *args, **kwargs):
##        if not cls._instance:
##            cls._instance = super(PythonSvSingleton, cls).__new__(cls, *args, **kwargs)
##        return cls._instance
##
##namednodes.sv.get_all()
##object_singleton = PythonSvSingleton()
##object_singleton.object = namednodes.sv


def prRed(skk): print("\\033[91m {}\\033[00m" .format(skk))
def prGreen(skk): print("\\033[92m {}\\033[00m" .format(skk))
def prYellow(skk): print("\\033[93m {}\\033[00m" .format(skk))

def reg_compare(reg,data):
        for i in range(len(data)):
            if data[i] == "x" or data[i] == "X" or reg[i] == data[i]:
                continue
            else:
                return False
        return True

def bitfield(n):
    a = bitfield_rev(n)
    b= []
    for i in a:
        b.insert(0,i)
    return b

def bitfield2(n):
    a = bitfield2_rev(n)
    b= []
    for i in a:
        b.insert(0,i)
    return b

def bitfield2_rev(n):
    if type(n) is not str:
        n = hex(n)
    if n[1] == "x":
        num = int(n,16)
    elif n[1] != "b":
        num = int(n)
    if n[1] != "b":
        bitArr = ["1" if digit=='1' else "0" for digit in bin(num)[2:]]
        return bitArr
    else:
        a = []
        for digit in n[2:]:
            a.append(digit)
        return a


def bitfield_rev(n):
    if type(n) is not str:
        n = hex(n)
    output = []
    mid=""
    if n[1] == "x":
        for fourbit in n[2:]:
            mid += str(bin(int(fourbit, 16))[2:].zfill(4))
        return bitfield_rev("0b" + mid)
    elif n[1] == "b":
        for bit in n[2:]:
            output.append(bit)
        return output

def bitArr2hex(bitArr):
    out_str = ""
    for bit in reversed(bitArr):
        out_str += bit
    return int(out_str,2)



class svReg():
    def __init__(self, _regName):
        self.regName = _regName
        self.regNameStr = _regName.path
        self.param_read_arr = bitfield(self.regName)
        self.regSize = self.getRegSize(self.regName)
        while len(self.param_read_arr) < self.regSize:
            self.param_read_arr.append("0")

    def getRegSize(self, _regName):
        return _regName.numbits

    def storeField(self, fieldName,data):
        if isinstance(fieldName, tuple):
            index = fieldName
            data_arr = bitfield(data)
            if data_arr == ['0']:
                i = index[1]
                while i < index[0]:
                    data_arr.append('0')
                    i += 1
            i=0
            for t in range(index[1],index[0]+1):
                if i < len(data_arr):
                    self.param_read_arr[t] = data_arr[i]
                else:
                    self.param_read_arr[t] = '0'
                i += 1
        else:
            bit_offset = getattr(self.regName,fieldName).info['bitOffset']
            index_len = getattr(self.regName,fieldName).info['bitWidth']
            index = (int(str(bit_offset)) + int(str(index_len)) -1 ,  int(str(bit_offset)))
            data_arr = bitfield(data)
            if data_arr == ['0']:
                i = index[1]
                while i < index[0]:
                    data_arr.append('0')
                    i += 1
            i=0
            for t in range(index[1],index[0]+1):
                if i < len(data_arr):
                    self.param_read_arr[t] = data_arr[i]
                else:
                    self.param_read_arr[t] = '0'
                i += 1

    def compare(self, fieldName, data, reg_name, compare_targets):
        append = True
        data_arr = bitfield2(data)
        if isinstance(fieldName, tuple):
            if len(fieldName) == 2:
                index_len = fieldName[0] - fieldName[1] + 1
                index = fieldName
            else:
                bit_offset = getattr(self.regName,fieldName[0].split("[")[0]).info['bitOffset']
                index_len = getattr(self.regName,fieldName[0].split("[")[0]).info['bitWidth']
                index = (int(str(bit_offset)) + int(str(index_len)) -1 ,  int(str(bit_offset)))
                index =( int(str(index[1]))+ int(str(fieldName[1])) , int(str(index[1])) + int(str(fieldName[2])))
                data_arr = data_arr[ 0 : fieldName[2] - fieldName[1] + 1 ]
                append = False
        else:
            bit_offset = getattr(self.regName,fieldName).info['bitOffset']
            index_len = getattr(self.regName,fieldName).info['bitWidth']
            index = (int(str(bit_offset)) + int(str(index_len)) -1 ,  int(str(bit_offset)))
        if append:
            while len(data_arr) < index_len:
                data_arr.append("0")    
        if reg_compare(self.param_read_arr[index[1]:index[0]+1],data_arr):
            prGreen("### P A S S ###  compare %s = %s\\n                  compared fields: %s" %(reg_name, data, compare_targets))
        else:
            actualData = bitArr2hex(self.param_read_arr[index[1]:index[0]+1])
            prRed("### F A I L ###  compare %s = %s               REG Value is: %s\\n                  compared fields: %s" %((reg_name, data, hex(actualData),compare_targets)))

    def capture(self,fieldName):
        if isinstance(fieldName, tuple):
            if len(fieldName) == 2:
                index = fieldName
            else:
                bit_offset = getattr(self.regName,fieldName[0]).info['bitOffset']
                index_len = getattr(self.regName,fieldName[0]).info['bitWidth']
                index = (int(str(bit_offset)) + int(str(index_len)) -1 ,  int(str(bit_offset)))
                index =(index[0]+ fieldName[1], index[0]+fieldName[2]+1)
        else:
            bit_offset = getattr(self.regName,fieldName).info['bitOffset']
            index_len = getattr(self.regName,fieldName).info['bitWidth']
            index = (int(str(bit_offset)) + int(str(index_len)) -1 ,  int(str(bit_offset)))
        actualData = bitArr2hex(self.param_read_arr[index[1]:index[0]+1])
        print("%s = %s" % (self.regNameStr, actualData))


    def flush(self):
        self.regName.write(bitArr2hex(self.param_read_arr))



prev_reg = ""
reg_size = 0x0


#####  END OF SETUP  ###########################################################

def runConverted():
        """
        self.printC1(base_settings,output)
        for row_num, row in enumerate(spf_file):
            if row == ("\n"):
                continue
            else:
                while row.startswith(" "):
                    row = row[1:]
            if self.comp_command(row_num,row,output,spf_file):
                return
        #self.printC1("\nrunConverted()",output)
        end_string = ' ,Converted Successfully !'
        print (end_string)
        output.close()

    def returnTapsUsed(self):
        return self.taps_used


def main():
    ############################################################################

    for dirpath, dirnames, filenames in os.walk("C:\SPFs"):           ###   "C:\pythonsv\lunarlake\debug\domains\hsio_dv\Display"
        for filename in [f for f in filenames if (f.endswith(".spf") or f.endswith(".SPF"))]:
            if "ate_dptx_upcs_top_external_loopback_tx1_rx2_HDMI_6G_COLORDEPTH.spf" in filename:
                input_name = dirpath+"\\"+filename
                A = Command(input_name)
    end_string = """
    ###########################
    #########---END---#########
    ###########################"""
    print (end_string)


    ############################################################################

if __name__ == '__main__':
    main()
