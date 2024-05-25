def use_example(direct_reg,input_dir,output_dir,week_folder_en,log_file_path,conversion_time,CPUgen='PTL'):
    import os,sys
    import sys
    #sys.path.append(os.getcwd())
    from spfs_source import spf2sv_converter
    # input_dir  = r"C:\pythonsv\atdio\sio\LNL\sio_dv\spfs_source\ww22_2'23\ILB_eDP_eDP"             # r"C:\pythonsv\lunarlake\debug\domains\sio_dv\spfs_source\9_1" #
    # output_dir = r"C:\pythonsv\atdio\sio\LNL\sio_dv\spfs_pysv_ready"             # r"C:\pythonsv\lunarlake\debug\domains\sio_dv\spfs_pysv_ready\Current" # r"C:\Scripts\spf conversion sandbox\output lib"
    print(f"input_dir= {input_dir}\noutput_dir= {output_dir}\nweek_folder_en= {week_folder_en}\ndirect_reg= {direct_reg}\n")
    spf2sv_converter.run(direct_reg,conversion_time,log_file_path,week_folder_en,input_dir,output_dir,CPUgen=CPUgen)
