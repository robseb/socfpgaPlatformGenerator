#!/usr/bin/env Python
#
#            ########   ######     ##    ##  #######   ######  ########  #######                  
#            ##     ## ##    ##     ##  ##  ##     ## ##    ##    ##    ##     ##           
#            ##     ## ##            ####   ##     ## ##          ##    ##     ##        
#            ########   ######        ##    ##     ## ##          ##    ##     ##       
#            ##   ##         ##       ##    ##     ## ##          ##    ##     ##      
#            ##    ##  ##    ##       ##    ##     ## ##    ##    ##    ##     ##        
#            ##     ##  ######        ##     #######   ######     ##     #######         
#             ___          _   _      _     ___               _                 
#            | _ )  _  _  (_) | |  __| |   / __|  _  _   ___ | |_   ___   _ __  
#            | _ \ | || | | | | | / _` |   \__ \ | || | (_-< |  _| / -_) | '  \ 
#            |___/  \_,_| |_| |_| \__,_|   |___/  \_, | /__/  \__| \___| |_|_|_|
#                                                  |__/                              
#
#
# Robin Sebastian (https://github.com/robseb)
# Contact: git@robseb.de
# Repository: https://github.com/robseb/meta-intelfpga
#
# Python Script to automatically generate the u-boot loader 
# for Intel SoC-FPGAs 
 
# (2020-07-17) Vers.1.0 
#   first Version 
#

version = "0.01"

#
#
#
############################################ Const ###########################################
#
#
#
DELAY_MS = 1 # Delay after critical tasks in milliseconds 

QURTUS_DEF_FOLDER       = "intelFPGA"
QURTUS_DEF_FOLDER_LITE  = "intelFPGA_lite"

SPLM = ['/','\\'] # Linux, Windows 
SPno = 0

GITNAME                  = "socfpgaPlatformGenerator"
GIT_SCRIPT_URL           = "https://github.com/robseb/socfpgaPlatformGenerator.git"
GIT_U_BOOT_SOCFPGA_URL   = "https://github.com/altera-opensource/u-boot-socfpga"
GIT_U_BOOT_SOCFPGA_BRANCH = "socfpga_v2019.10" # default: master


import os
import sys
import time
import io
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from typing import NamedTuple
import math
import glob
from pathlib import Path
from datetime import datetime
from datetime import timedelta

try:
    from LinuxBootImageFileGenerator.LinuxBootImageGenerator import Partition,BootImageCreator
except ModuleNotFoundError as ex:
    print('ERROR: The LinuxBootImageGenerator is not available inside the cloned folder!')
    print('       Delate the github folder and use following command ')
    print('       to clone all required components:')
    print(' $ git clone --recursive -j8 '+GIT_SCRIPT_URL+'\n')
    sys.exit()

if sys.platform =='linux':
    try:
        import git
        from git import RemoteProgress

    except ImportError as ex:
        print('Msg: '+str(ex))
        print('This Python Application requirers "git"')
        print('Use following pip command to install it:')
        print('$ pip3 install GitPython')
        sys.exit()


#
#
#
############################################ Github clone function ###########################################
#
#
#

if sys.platform =='linux':
    # @brief to show process bar during github clone
    #
    #

    class CloneProgress(RemoteProgress):
        def update(self, op_code, cur_count, max_count=None, message=''):
            if message:
                sys.stdout.write("\033[F")
                print("    "+message)


############################################                                ############################################
############################################             MAIN               ############################################
############################################                                ############################################

if __name__ == '__main__':
    print('\n##############################################################################')
    print('#                                                                            #')
    print('#    ########   ######     ##    ##  #######   ######  ########  #######     #')        
    print('#    ##     ## ##    ##     ##  ##  ##     ## ##    ##    ##    ##     ##    #')          
    print('#    ##     ## ##            ####   ##     ## ##          ##    ##     ##    #')    
    print('#    ########   ######        ##    ##     ## ##          ##    ##     ##    #')   
    print('#    ##   ##         ##       ##    ##     ## ##          ##    ##     ##    #')  
    print('#    ##    ##  ##    ##       ##    ##     ## ##    ##    ##    ##     ##    #')    
    print('#    ##     ##  ######        ##     #######   ######     ##     #######     #') 
    print('#                                                                            #')
    print("#       AUTOMATIC SCRIPT TO COMBINE ALL FILES OF A EMBEDDED LINUX TO A       #")
    print("#                       BOOTABLE DISTRIBUTABLE IMAGE FILE                    #")
    print('#                                                                            #')
    print("#               by Robin Sebastian (https://github.com/robseb)               #")
    print('#                          Contact: git@robseb.de                            #')
    print("#                            Vers.: "+version+"                                     #")
    print('#                                                                            #')
    print('##############################################################################\n\n')

    ############################################ Runtime environment check ###########################################

    # Check proper Python Version
    if sys.version_info[0] < 3:
        print('ERROR: This script can not work with your Python Version!')
        print("Use Python 3.x for this script!")
        sys.exit()

    # Check that the Version runs on Linux
    if not sys.platform =='linux':
        print('ERROR: This script works only on Linux!')
        print("Please run this script on a Linux Computer!")
        sys.exit()

    ######################################### Find the Intel EDS Installation Path ####################################
    
    print('--> Find the System Platform')

    EDS_Folder_def_suf_dir = os.path.join(os.path.join(os.path.expanduser('~'))) + '/'

    EDS_EMBSHELL_DIR    = "/embedded/embedded_command_shell.sh"

    # 1.Step: Find the EDS installation path
    print('--> Try to find the default Intel EDS installation path')

    quartus_standard_ver = False
    # Loop to detect the case that the free Version of EDS (EDS Standard [Folder:intelFPGA]) and 
    #    the free Version of Quartus Prime (Quartus Lite [Folder:intelFPGA_lite]) are installed together 
    while(True):
        if (os.path.exists(EDS_Folder_def_suf_dir+QURTUS_DEF_FOLDER)) and (not quartus_standard_ver):
            EDS_Folder=EDS_Folder_def_suf_dir+QURTUS_DEF_FOLDER
            quartus_standard_ver = True
        elif(os.path.exists(EDS_Folder_def_suf_dir+QURTUS_DEF_FOLDER_LITE)):
            EDS_Folder=EDS_Folder_def_suf_dir+QURTUS_DEF_FOLDER_LITE
            quartus_standard_ver = False
        else:
            print('ERROR: No Intel EDS Installation Folder was found!')
            sys.exit()

        # 2.Step: Find the latest Intel EDS Version No.
        avlVer = []
        for name in os.listdir(EDS_Folder):
            if  os.path.abspath(name):
                try:
                    avlVer.append(float(name))
                except Exception:
                    pass

        if (len(avlVer)==0):
            print('ERROR: No valid Intel EDS Version was found')
            sys.exit()

        avlVer.sort(reverse = True) 

        highestVer = avlVer[0]
        EDS_Folder = EDS_Folder +SPLM[SPno]+ str(highestVer)   

        if (not(os.path.realpath(EDS_Folder))):
            print('ERROR: No vaild Intel EDS Installation Folder was found!')
            sys.exit()

        if(highestVer < 19): 
            print('ERROR: This script is designed for Intel EDS Version 19+ (19.1, 20.1, ...) ')
            print('       You using Version '+str(highestVer)+' please update Intel EDS!')
            sys.exit()
        elif(highestVer > 20.1):
            print('WARNING: This script was designed for Intel EDS Version 19.1 and 20.1')
            print('         Your version is newer. Errors may occur!')

        # Check if the NIOS II Command Shell is available 
        if((not(os.path.isfile(EDS_Folder+EDS_EMBSHELL_DIR)) )):
            if( not quartus_standard_ver):
                print('ERROR: Intel EDS Embedded Command Shell was not found!')
                sys.exit()
        else:
            break

    print('        Following EDS Installation Folder was found:')
    print('        '+EDS_Folder)


    ############################### Check that the script runs inside the Github folder ###############################
    print('\n--> Check that the script runs inside the Github folder')
    excpath = os.getcwd()
    quartus_proj_top_dir =''
    try:
    
        if(len(excpath)<len(GITNAME)):
            raise Exception()

        # Find the last slash in the execution path 
        slashpos =0
        for str_ in excpath:
            slashpos_pos=excpath.find(SPLM[SPno],slashpos)
            if(slashpos_pos == -1):
                break
            slashpos= slashpos_pos+len(SPLM[SPno])

        if(not excpath[slashpos:] == GITNAME):
             raise Exception()

        quartus_proj_top_dir = excpath[:slashpos-1]

    except Exception:
        print('ERROR: The script was not executed inside the cloned Github folder')
        print('       Please clone this script from Github and execute the script')
        print('       directly inside the cloned folder!')
        print('URL: '+GIT_SCRIPT_URL)
        sys.exit()

############################### Check that the script runs inside the Quartus project ###############################
    print('--> Check that the script runs inside the Quartus Prime project folder')
    
    # Find the Quartus project (.qpf) file 
    qpf_file_name = ''
    for file in os.listdir(quartus_proj_top_dir):
            if ".qpf" in file:
                qpf_file_name =file
                break

    # Find the Platform Designer (.qsys) file  
    qsys_file_name = ''
    for file in os.listdir(quartus_proj_top_dir):
            if ".qsys" in file and not ".qsys_edit" in file:
                qsys_file_name =file
                break
 
    # Find the Platform Designer folder
    if not os.path.isdir(quartus_proj_top_dir+SPLM[SPno]+qsys_file_name[:qsys_file_name.find('.qsys')]):
        print('ERROR: The script was not executed inside the cloned Github folder')
        print('       Please clone this script from Github, copy it to the top folder of your Quartus project and execute the script')
        print('       directly inside the cloned folder!')
        print('URL: '+GIT_SCRIPT_URL)
        print(' -- Required folder structure  --')
        print(' YOUR_QURTUS_PROJECT_FOLDER ')
        print('|     L-- PLATFORM_DESIGNER_FOLDER')
        print('|     L-- platform_designer.qsys')
        print('|     L-- _handoff')
        print('|     L-- quartus_project.qpf')
        print('|     L-- socfpgaPlatformGenerator <<<----')
        print('|         L-- socfpgaPlatformGenerator.py')
        print(' Note: File names can be chosen freely')
        sys.exit()

    # Find the handoff folder
    print('--> Find the Quartus handoff folder')
    handoff_folder_name = ''
    handoff_folder_start_name =''
    for file in os.listdir(quartus_proj_top_dir):
            if "_handoff" in file:
                handoff_folder_start_name =file
                break
    folder_found = False
    for folder in os.listdir(quartus_proj_top_dir+SPLM[SPno]+handoff_folder_start_name):
        if os.path.isdir(quartus_proj_top_dir+SPLM[SPno]+handoff_folder_start_name+SPLM[SPno]+folder):
            handoff_folder_name = folder
            if folder_found:
                print('ERROR: More then one folder inside the Quartus handoff folder "'+handoff_folder_name+'" found! Please delate one!')
                sys.exit()
            folder_found = True
    handoff_folder_name = handoff_folder_start_name+SPLM[SPno]+handoff_folder_name
    print('     Handoff folder:" '+handoff_folder_name+'"')

    # Find the "hps.xml"-file inside the handoff folder
    print('--> Find the "hps.xml" file ')
    handoff_xml_found =False

    for file in os.listdir(quartus_proj_top_dir+SPLM[SPno]+handoff_folder_name):
        if "hps.xml" == file:
            handoff_xml_found =True
            break
    if not handoff_xml_found:
        print('ERROR: The "hps.xml" file inside the handoff folder was not found!')
        sys.exit()

    # Load the "hps.xml" file to read the device name
    print('--> Read the "hps.xml"-file to decode the device name')

    try:
        tree = ET.parse(quartus_proj_top_dir+SPLM[SPno]+handoff_folder_name+SPLM[SPno]+'hps.xml') 
        root = tree.getroot()
    except Exception as ex:
        print(' ERROR: Failed to prase "hps.xml" file!')
        print(' Msg.: '+str(ex))
        sys.exit()

    device_name_temp =''
    for it in root.iter('config'):
        name = str(it.get('name'))
        if name == 'DEVICE_FAMILY':
            device_name_temp = str(it.get('value'))
            break
    if device_name_temp == '':
        print('ERROR: Failed to decode the device name inside "hps.xml"')

    # Convert Device name
    if device_name_temp == 'Cyclone V':
        device_name = 'cyclone5'
    elif device_name_temp == 'Arria V':
        device_name = 'arria5'
    else:
        print('Error: Your Device ('+device_name_temp+') is not supported right now!')
        print('       I am working on it...')
        sys.exit()
    print('     Device Name:"'+device_name_temp+'"') 
 

############################### Create "software/bootloader" folder inside Quartus project  ###################################
    if not os.path.isdir(quartus_proj_top_dir+SPLM[SPno]+'software'):
        print('-> Create the folder software')
        try:
            os.mkdir(quartus_proj_top_dir+SPLM[SPno]+'software')      
        except Exception as ex:
            print('ERROR: Failed to create the software folder MSG:'+str(ex))

    quartus_bootloder_dir = quartus_proj_top_dir+SPLM[SPno]+'software'+SPLM[SPno]+'bootloader'
    bootloader_available =False
    if not os.path.isdir(quartus_bootloder_dir):
        print('-> Create the folder bootloader')
        try:
            os.mkdir(quartus_bootloder_dir)      
        except Exception as ex:
            print('ERROR: Failed to create the bootloader folder MSG:'+str(ex))
    else:
        bootloader_available = True

####################################################### Clone "u-boot-socfpga" ################################################
    u_boot_socfpga_dir = quartus_bootloder_dir+SPLM[SPno]+'u-boot-socfpga'
    if(os.path.isdir(u_boot_socfpga_dir)):
        print('--> "u-boot-socfpga" is already available')
        print('       Pull it from Github')
        g = git.cmd.Git(u_boot_socfpga_dir)
        g.pull()
        
    else:
        print('--> Cloning "u-boot-socfpga" Version ('+GIT_U_BOOT_SOCFPGA_URL+')\n')
        print('       please wait...')

        try:
            git.Repo.clone_from(GIT_U_BOOT_SOCFPGA_URL, u_boot_socfpga_dir, branch=GIT_U_BOOT_SOCFPGA_BRANCH, progress=CloneProgress())
        except Exception as ex:
            print('ERROR: The cloning failed! Error Msg.:'+str(ex))
            sys.exit()

        if not os.path.isabs(u_boot_socfpga_dir):
            print('ERROR: Failed to clone u-boot-socfpga!')
            sys.exit()

        print('       cloning done')
    
################################################## Find the EDS Filter script ##############ä####################################
    eds_filter_script_dir = SPLM[SPno]+'arch'+SPLM[SPno]+ \
                            'arm'+SPLM[SPno]+'mach-socfpga'+SPLM[SPno]+'qts-filter.sh'
    # Find the filter script
    if not os.path.isfile(u_boot_socfpga_dir+eds_filter_script_dir):
        print('ERROR: The EDS Filter script is not available on the default directory')
        print('       "/arch/arm/mach-socfpga/qts-filter.sh"')
        sys.exit()
    # Find the BPS for the selected device inside u-boot
    u_boot_bsp_qts_dir=''
    if device_name == 'cyclone5':
        u_boot_bsp_qts_dir = '/board/altera/cyclone5-socdk/qts/'
        if not os.path.isdir(u_boot_socfpga_dir+SPLM[SPno]+u_boot_bsp_qts_dir):
            print('Error: The u-boot BSP QTS direcorory is for the device not available!')
            print('       "/board/altera/cyclone5-socdk/qts/"')
            sys.exit()
    elif device_name == 'arria5':
        u_boot_bsp_qts_dir = '/board/altera/arria5-socdk/qts/'
        if not os.path.isdir(u_boot_socfpga_dir+SPLM[SPno]+u_boot_bsp_qts_dir):
            print('Error: The u-boot BSP QTS direcorory is for the device not available!')
            print('       "/board/altera/arria5-socdk/qts/"')
            sys.exit()


#################################### Setup u-boot with the Quartus Prime Settings  ################################################

    # Is a new bootloader build necessary?
    bootloader_build_required =True
    if (bootloader_available and os.path.isfile(u_boot_socfpga_dir+SPLM[SPno]+'u-boot-with-spl.sfp')):
        modification_time = os.path.getmtime(u_boot_socfpga_dir+SPLM[SPno]+'u-boot-with-spl.sfp') 
        current_time =  datetime.now().timestamp()

        # Offset= 3 hour
        if modification_time  + 3*60*60 > current_time:
            bootloader_build_required = False
            print('\n################################################################################')
            print('#                                                                              #')
            print('#                  Bootloader was created within 3 hours ago                   #')
            print('#                                                                              #')
            print('#                    Do you want to rebuild the bootloader?                    #')
            print('#                                                                              #')
            print('--------------------------------------------------------------------------------')
            print('#    Y:              Yes, rebuild the bootloader                               #')
            print('#    anything else:  No,  continue without rebuilding the bootloader           #')
            print('#    Q:              Abort                                                     #')
            print('------------------------------------------------------------------------------')
            __wait2__ = input('Please type...')

            if __wait2__ =='q' or __wait2__=='Q':
                sys.exit()
            elif __wait2__ =='Y' or __wait2__=='y':
                bootloader_build_required = True
    '''
    Later update: Support for linaro build system 
    https://rocketboards.org/foswiki/Documentation/BuildingBootloader#Building_Linux_Kernel

    wget https://releases.linaro.org/components/toolchain/binaries/7.5-2019.12/arm-linux-gnueabihf/gcc-linaro-7.5.0-2019.12-x86_64_arm-linux-gnueabihf.tar.xz
    tar xf gcc-linaro-7.5.0-2019.12-x86_64_arm-linux-gnueabihf.tar.xz
    export PATH=`pwd`/gcc-linaro-7.5.0-2019.12-x86_64_arm-linux-gnueabihf/bin:$PATH
    export ARCH=arm
    export CROSS_COMPILE=arm-linux-gnueabihf-
    '''

    # Build the bootloader
    if bootloader_build_required:
        print('--> Start the Intel Embedded Command Shell')
        try:
            # Create the BSP package for the device with the Intel EDS shell
            with subprocess.Popen(EDS_Folder+SPLM[SPno]+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
                time.sleep(DELAY_MS)
                
                print('--> Generate the Board Support Package (BSP) for the Quartus Prime configuration')
                b = bytes(' cd '+quartus_proj_top_dir+"\n", 'utf-8')
                edsCmdShell.stdin.write(b) 

                b = bytes('bsp-create-settings --type spl --bsp-dir software/bootloader '+ \
                        '--preloader-settings-dir "'+handoff_folder_name+'" ' +\
                        '--settings software/bootloader/settings.bsp\n','utf-8')

                edsCmdShell.stdin.write(b)
                edsCmdShell.communicate()
                
                
            # Check that BSP generation is okay
            if not os.path.isdir(quartus_proj_top_dir+'/software/bootloader/generated') or \
                not os.path.isfile(quartus_proj_top_dir+'/software/bootloader/settings.bsp'):
                print('ERROR: The BSP generation failed!')
                sys.exit()

            print('--> Run the Intel EDS Filter script')
            with subprocess.Popen(EDS_Folder+SPLM[SPno]+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
                time.sleep(DELAY_MS)
                b = bytes('cd '+quartus_proj_top_dir+'/software/bootloader/u-boot-socfpga \n','utf-8')
                edsCmdShell.stdin.write(b) 
                #
                # 
                # soc_type      - Type of SoC, either 'cyclone5' or 'arria5'.
                # input_qts_dir - Directory with compiled Quartus project
                #                and containing the Quartus project file (QPF).
                # input_bsp_dir - Directory with generated bsp containing
                #                 the settings.bsp file.
                # output_dir    - Directory to store the U-Boot compatible
                #                 headers.

                b = bytes('./'+eds_filter_script_dir+' '+device_name+' ../../../ ../ ' \
                        '.'+u_boot_bsp_qts_dir+'  \n','utf-8')
                edsCmdShell.stdin.write(b) 
                #time.sleep(10*DELAY_MS)

                edsCmdShell.communicate()
                time.sleep(3*DELAY_MS)
        
        except Exception as ex:
            print('ERROR: Failed to start the Intel EDS Command Shell! MSG:'+ str(ex))
            sys.exit()

        # Check that the output files are available 
        if (not os.path.isdir(quartus_bootloder_dir+SPLM[SPno]+"generated"))  or \
         (not os.path.isdir(quartus_bootloder_dir+SPLM[SPno]+"generated"+SPLM[SPno]+"sdram")):
            print('ERROR: BSP Generation failed!')

        print('\n################################################################################')
        print('#                                                                              #')
        print('#                     OPTIONAL: CHANGE U-BOOT MANUALLY                         #')
        print('#                                                                              #')
        print('#  At this point it is possible to change the code of "u-boot-socfpga"         #')
        print('#                                                                              #')
        print('--------------------------------------------------------------------------------')
        print('#                   --- "u-boot-socfpga" file direcotroy ---                   #')
        print('#   '+u_boot_socfpga_dir)
        print('--------------------------------------------------------------------------------')
        print('#                M: Start menuconfig for "u-boot-socfpga"                      #')
        print('#                Q: Abort                                                      #')
        print('#    anything else: continue with compiling "u-boot-socfpga"                   #')
        print('------------------------------------------------------------------------------')
        __wait__ = input('Type anything to continue ... ')

        start_menuconfig = False 
        if __wait__ =='q' or __wait__=='Q':
            sys.exit()
        
        if __wait__ =='m' or __wait__=='M':
            start_menuconfig = True

    ###################################################   Build u-boot  ################################################
        print('--> Start the Intel Embedded Command Shell')
        try:
            with subprocess.Popen(EDS_Folder+SPLM[SPno]+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
                time.sleep(DELAY_MS)
                print('--> Compile "u-boot-socfpga"')

                b = bytes(' cd '+quartus_proj_top_dir+'/software/bootloader/u-boot-socfpga \n', 'utf-8')
                edsCmdShell.stdin.write(b) 

                b = bytes('export CROSS_COMPILE=arm-linux-gnueabihf- \n','utf-8')
                edsCmdShell.stdin.write(b) 

                b = bytes('export ARCH=arm \n','utf-8')
                edsCmdShell.stdin.write(b) 

                b = bytes('make distclean \n','utf-8')
                edsCmdShell.stdin.write(b) 

                
                b = bytes('make socfpga_cyclone5_defconfig\n','utf-8')
                edsCmdShell.stdin.write(b) 

                if not start_menuconfig: 
                    b = bytes('make -j 24 \n','utf-8')
                    edsCmdShell.stdin.write(b) 

                edsCmdShell.communicate()
                time.sleep(DELAY_MS)
        
        except Exception as ex:
            print('ERROR: Failed to start the Intel EDS Command Shell! MSG:'+ str(ex))
            sys.exit()

        ################################################### Start menuconfig ###################################################
        # Start menuconfig for "u-boot-socfpga"
        if start_menuconfig:
            # Create "menuconfig.sh" shell script for starting menuconfig
            if os.path.isfile('menuconfig.sh'):
                try:
                    os.remove('menuconfig.sh')
                except Exception:
                    print('ERROR: Failed to remove menuconfig.sh')

            with open('menuconfig.sh', "a") as f:
                f.write('#!/bin/sh\n')
                f.write('export TOP_FOLDER=`pwd`\n')
                f.write('cd && cd '+quartus_proj_top_dir+'/software/bootloader/u-boot-socfpga\n')
                f.write('make menuconfig\n')
                f.write('cd $TOP_FOLDER\n')
            if not os.path.isfile('menuconfig.sh'):
                print('ERROR: Failed to create "menuconfig.sh" script')
                sys.exit()
            
            # Run the shell script to allow the user to use menuconfig
            print('--> Starting menuconfig for "u-boot-socfpga"')
            os.system('chmod +x menuconfig.sh  && sh  menuconfig.sh')
            __wait3__ = input('Type anything to continue ... ')

            # Remove the shell script 
            if os.path.isfile('menuconfig.sh'):
                try:
                    os.remove('menuconfig.sh')
                except Exception:
                    print('ERROR: Failed to remove menuconfig.sh')

            # Build u-boot with the menuconfig changes 
            try:
                with subprocess.Popen(EDS_Folder+SPLM[SPno]+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
                    time.sleep(DELAY_MS)
                    print('--> Compile "u-boot-socfpga"')

                    b = bytes(' cd '+quartus_proj_top_dir+'/software/bootloader/u-boot-socfpga \n', 'utf-8')
                    edsCmdShell.stdin.write(b) 

                    b = bytes('export CROSS_COMPILE=arm-linux-gnueabihf- \n','utf-8')
                    edsCmdShell.stdin.write(b) 

                    b = bytes('export ARCH=arm \n','utf-8')
                    edsCmdShell.stdin.write(b) 

                    b = bytes('make -j 24 \n','utf-8')
                    edsCmdShell.stdin.write(b) 

                    edsCmdShell.communicate()
                    time.sleep(DELAY_MS)
            
            except Exception as ex:
                print('ERROR: Failed to start the Intel EDS Command Shell! MSG:'+ str(ex))
                sys.exit()

        # Check that u-boot output file is there 
        if not os.path.isfile(u_boot_socfpga_dir+SPLM[SPno]+'u-boot-with-spl.sfp') or \
            not os.path.isfile(u_boot_socfpga_dir+SPLM[SPno]+'u-boot.img'):
            print('ERROR: u-boot build failed!')
            sys.exit()

        # Read the creation date of the output files to check that the files are new
        modification_time = os.path.getmtime(u_boot_socfpga_dir+SPLM[SPno]+'u-boot-with-spl.sfp') 
        current_time =  datetime.now().timestamp()

        # Offset= 5 min 
        if modification_time+ 5*60 < current_time:
            print('Error: u-boot build failed!')

        print('--> "u-boot-socfpga" build was successfully')
    # u-boot build
 
    print('\nNOTE: WORK IN PROCESS! THE DEVELOPMENT FOR THIS SCRIPT IS NOT DONE!\n')
############################################################ Goodby screen  ###################################################
    print('\n################################################################################')
    print('#                                                                              #')
    print('#                        GENERATION WAS SUCCESSFUL                             #')
    print('# -----------------------------------------------------------------------------#')
    print('#                                                                              #')
    print('#                            ROBIN SEBASTIAN                                   #')
    print('#                     (https://github.com/robseb/)                             #')
    print('#                            git@robseb.de                                     #')
    print('#                                                                              #')
    print('#    LinuxBootImageGenerator and rsYocto are projects, that I have fully       #')
    print('#        developed on my own. No companies are involved in these projects.     #')
    print('#        I am recently graduated as Master of Since of electronic engineering  #')
    print('#                Please support me for further development                     #')
    print('#                                                                              #')
    print('################################################################################')
# EOF
