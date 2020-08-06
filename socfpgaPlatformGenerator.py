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

QURTUS_DEF_FOLDER         = "intelFPGA"
QURTUS_DEF_FOLDER_LITE    = "intelFPGA_lite"

YOCTO_BASE_FOLDER         = 'poky'

BOOTLOADER_FILE_NAME      = 'u-boot-with-spl.sfp'


GITNAME                  = "socfpgaPlatformGenerator"
GIT_SCRIPT_URL           = "https://github.com/robseb/socfpgaPlatformGenerator.git"
GIT_U_BOOT_SOCFPGA_URL   = "https://github.com/altera-opensource/u-boot-socfpga"
GIT_U_BOOT_SOCFPGA_BRANCH = "socfpga_v2019.10" # default: master

#
# @brief default XML Blueprint file
#
intelsocfpga_blueprint_xml_file ='<?xml version="1.0" encoding = "UTF-8" ?>\n'+\
    '<!-- Linux Distribution Blueprint XML file -->\n'+\
    '<!-- Used by the Python script "LinuxDistro2Image.py -->\n'+\
    '<!-- to create a custom Linux boot image file -->\n'+\
    '<!-- Description: -->\n'+\
    '<!-- item "partition" describes a partition on the final image file-->\n'+\
    '<!-- L "id"        => Partition number on the final image (1 is the lowest number) -->\n'+\
    '<!-- L "type"      => Filesystem type of partition  -->\n'+\
    '<!--   L       => ext[2-4], Linux, xfs, vfat, fat, none, raw, swap -->\n'+\
    '<!-- L "size"      => Partition size -->\n'+\
    '<!-- 	L	    => <no>: Byte, <no>K: Kilobyte, <no>M: Megabyte or <no>G: Gigabyte -->\n'+\
    '<!-- 	L	    => "*" dynamic file size => Size of the files2copy + offset  -->\n'+\
    '<!-- L "offset"    => in case a dynamic size is used the offset value is added to file size-->\n'+\
    '<!-- L "devicetree"=> compile the Linux Device (.dts) inside the partition if available (Top folder only)-->\n'+\
    '<!-- 	L 	    => Yes: Y or No: N -->\n'+\
    '<!-- L "unzip"     => Unzip a compressed file if available (Top folder only) -->\n'+\
    '<!-- 	L 	    => Yes: Y or No: N -->\n'+\
    '<LinuxDistroBlueprint>\n'+\
    '<partition id="1" type="vfat" size="*" offset="500M" devicetree="Y" unzip="N" />\n'+\
    '<partition id="2" type="ext3" size="*" offset="1M" devicetree="N" unzip="Y" />\n'+\
    '<partition id="3" type="RAW" size="*" offset="20M"  devicetree="N" unzip="N" />\n'+\
    '</LinuxDistroBlueprint>\n'

socfpga_devices_list = ['cyclone5', 'arria5', 'arria10' ]

# Device ID: 0=Cyclone5, 1=Arria5, 2=Arria10 
device_id=0 

# "u-boot-socfpga" QTS file location direcotry 
u_boot_bsp_qts_dir_list = ['/board/altera/cyclone5-socdk/qts/', '/board/altera/arria5-socdk/qts/', \
                    '/board/altera/arria10-socdk/qts/']

# "u-boot-socfpga deconfig" file name for make (u-boot-socfpga/configs/)
u_boot_defconfig_list = ['socfpga_cyclone5_defconfig', 'socfpga_arria5_defconfig', \
                    'socfpga_arria10_defconfig']

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
        EDS_Folder = EDS_Folder +'/'+ str(highestVer)   

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
    print('--> Check that the script runs inside the Github folder')
    excpath = os.getcwd()
    quartus_proj_top_dir =''
    try:
    
        if(len(excpath)<len(GITNAME)):
            raise Exception()

        # Find the last slash in the execution path 
        slashpos =0
        for str_ in excpath:
            slashpos_pos=excpath.find('/',slashpos)
            if(slashpos_pos == -1):
                break
            slashpos= slashpos_pos+len('/')

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
    if qsys_file_name=='' or qpf_file_name=='':
        print('\nERROR: The script was not executed inside the cloned Github- and Quartus Prime project folder!')
        print('       Please clone this script with its folder from Github,')
        print('       copy it to the top folder of your Quartus project and execute the script')
        print('       directly inside the cloned folder!')
        print('       URL: '+GIT_SCRIPT_URL+'\n')
        print('       --- Required folder structure  ---')
        print('          YOUR_QURTUS_PROJECT_FOLDER ')
        print('       |     L-- PLATFORM_DESIGNER_FOLDER')
        print('       |     L-- platform_designer.qsys')
        print('       |     L-- _handoff')
        print('       |     L-- quartus_project.qpf')
        print('       |     L-- socfpgaPlatformGenerator <<<----')
        print('       |         L-- socfpgaPlatformGenerator.py')
        print('       Note: File names can be chosen freely\n')
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
    for folder in os.listdir(quartus_proj_top_dir+'/'+handoff_folder_start_name):
        if os.path.isdir(quartus_proj_top_dir+'/'+handoff_folder_start_name+'/'+folder):
            handoff_folder_name = folder
            if folder_found:
                print('ERROR: More then one folder inside the Quartus handoff folder "'+handoff_folder_name+'" found! Please delate one!')
                sys.exit()
            folder_found = True
    handoff_folder_name = handoff_folder_start_name+'/'+handoff_folder_name
    print('     Handoff folder:" '+handoff_folder_name+'"')

    # Find the "hps.xml"-file inside the handoff folder
    print('--> Find the "hps.xml" file ')
    handoff_xml_found =False

    for file in os.listdir(quartus_proj_top_dir+'/'+handoff_folder_name):
        if "hps.xml" == file:
            handoff_xml_found =True
            break
    if not handoff_xml_found:
        print('ERROR: The "hps.xml" file inside the handoff folder was not found!')
        sys.exit()

    # Load the "hps.xml" file to read the device name
    print('--> Read the "hps.xml"-file to decode the device name')

    try:
        tree = ET.parse(quartus_proj_top_dir+'/'+handoff_folder_name+'/'+'hps.xml') 
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
        device_id = 0
    elif device_name_temp == 'Arria V':
        device_id = 1
    elif device_name_temp == 'Arria 10':
        device_id = 2
    ## NOTE: ADD ARRIA 10 SUPPORT HERE 

    else:
        print('Error: Your Device ('+device_name_temp+') is not supported right now!')
        print('       I am working on it...')
        sys.exit()
    print('     Device Name:"'+device_name_temp+'"') 
 

############################### Create "software/bootloader" folder inside Quartus project  ###################################
    if not os.path.isdir(quartus_proj_top_dir+'/'+'software'):
        print('-> Create the folder software')
        try:
            os.mkdir(quartus_proj_top_dir+'/'+'software')      
        except Exception as ex:
            print('ERROR: Failed to create the software folder MSG:'+str(ex))

    quartus_bootloder_dir = quartus_proj_top_dir+'/'+'software'+'/'+'bootloader'
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
    u_boot_socfpga_dir = quartus_bootloder_dir+'/'+'u-boot-socfpga'
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
    eds_filter_script_dir = '/'+'arch'+'/'+ \
                            'arm'+'/'+'mach-socfpga'+'/'+'qts-filter.sh'
    # Find the filter script
    if not os.path.isfile(u_boot_socfpga_dir+eds_filter_script_dir):
        print('ERROR: The EDS Filter script is not available on the default directory')
        print('       "/arch/arm/mach-socfpga/qts-filter.sh"')
        sys.exit()
    # Find the BPS for the selected device inside u-boot
    u_boot_bsp_qts_dir=u_boot_bsp_qts_dir_list[device_id]
    if not os.path.isdir(u_boot_socfpga_dir+'/'+u_boot_bsp_qts_dir):
        print('Error: The u-boot BSP QTS direcorory is for the device not available!')
        print('       '+u_boot_bsp_qts_dir)
        sys.exit()



#################################### Setup u-boot with the Quartus Prime Settings  ################################################

    # Is a new bootloader build necessary?
    bootloader_build_required =True
    if (bootloader_available and os.path.isfile(u_boot_socfpga_dir+'/'+'u-boot-with-spl.sfp')):
        modification_time = os.path.getmtime(u_boot_socfpga_dir+'/'+'u-boot-with-spl.sfp') 
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
            with subprocess.Popen(EDS_Folder+'/'+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
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
            with subprocess.Popen(EDS_Folder+'/'+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
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

                b = bytes('./'+eds_filter_script_dir+' '+socfpga_devices_list[device_id]+' ../../../ ../ ' \
                        '.'+u_boot_bsp_qts_dir+'  \n','utf-8')
                edsCmdShell.stdin.write(b) 
                #time.sleep(10*DELAY_MS)

                edsCmdShell.communicate()
                time.sleep(3*DELAY_MS)
        
        except Exception as ex:
            print('ERROR: Failed to start the Intel EDS Command Shell! MSG:'+ str(ex))
            sys.exit()

        # Check that the output files are available 
        if (not os.path.isdir(quartus_bootloder_dir+'/'+"generated"))  or \
         (not os.path.isdir(quartus_bootloder_dir+'/'+"generated"+'/'+"sdram")):
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
            with subprocess.Popen(EDS_Folder+'/'+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
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

                b = bytes('make '+u_boot_defconfig_list[device_id]+'\n','utf-8')   
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
                with subprocess.Popen(EDS_Folder+'/'+EDS_EMBSHELL_DIR, stdin=subprocess.PIPE) as edsCmdShell:
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
        if not os.path.isfile(u_boot_socfpga_dir+'/'+'u-boot-with-spl.sfp') or \
            not os.path.isfile(u_boot_socfpga_dir+'/'+'u-boot.img'):
            print('ERROR: u-boot build failed!')
            sys.exit()

        # Read the creation date of the output files to check that the files are new
        modification_time = os.path.getmtime(u_boot_socfpga_dir+'/'+'u-boot-with-spl.sfp') 
        current_time =  datetime.now().timestamp()

        # Offset= 5 min 
        if modification_time+ 5*60 < current_time:
            print('Error: u-boot build failed!')

        print('--> "u-boot-socfpga" build was successfully')
    # u-boot build

    ###############################################   Create SD-CARD folder  ##############################################
    # Create the parttition blueprint xml file 
    if os.path.exists('SocFPGABlueprint.xml'):
        # Check that the SocFPGABlueprint XML file looks valid
        print('---> The Linux Distribution blueprint XML file exists')
    else:
        print(' ---> Creating a new Linux Distribution blueprint XML file')
        with open('SocFPGABlueprint.xml',"w") as f: 
            f.write(intelsocfpga_blueprint_xml_file)
    

    ############################################ Read the XML Blueprint file  ###########################################
    ####################################### & Process the settings of a partition   ####################################
    print('---> Read the XML blueprint file ')
    try:
        tree = ET.parse('SocFPGABlueprint.xml') 
        root = tree.getroot()
    except Exception as ex:
        print(' ERROR: Failed to prase SocFPGABlueprint.xml file!')
        print(' Msg.: '+str(ex))
        sys.exit()
    
    # Load the partition table of XML script 
    print('---> Load the items of XML file ')
    partitionList= []

    for part in root.iter('partition'):
        try:
            id = str(part.get('id'))
            type = str(part.get('type'))
            size = str(part.get('size'))
            offset = str(part.get('offset'))
            devicetree = str(part.get('devicetree'))
            unzip_str = str(part.get('unzip'))
        except Exception as ex:
            print(' ERROR: XML File decoding failed!')
            print(' Msg.: '+str(ex))
            sys.exit()

        comp_devicetree =False
        if devicetree == 'Y' or devicetree == 'y':
            comp_devicetree = True

        unzip =False
        if unzip_str == 'Y' or unzip_str == 'y':
            unzip = True

        try:
            partitionList.append(Partition(True,id,type,size,offset,comp_devicetree,unzip))
        except Exception as ex:
            print(' ERROR: Partition data import failed!')
            print(' Msg.: '+str(ex))
            sys.exit()
    
    # Add a datecode to the output file names
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M")

    # Use the default name "SocfpgaLinux.img" as output file name
    imageFileName   = "SocfpgaLinux"+dt_string+".img"
    outputZipFileName= "SocfpgaLinux"+dt_string+".zip"

    ####################################### Check if the partition folders are already available  #######################################

    # Generate working folder names for every partition
    working_folder_pat = []
    for part in partitionList:
        working_folder_pat.append(part.giveWorkingFolderName(True))

    image_folder_name = 'Image_partitions'
    create_new_folders = True

    # Check if the primary partition folder exists
    if os.path.isdir(image_folder_name):
        if not len(os.listdir(image_folder_name)) == 0:
            # Check that all partition folders exist
            for file in os.listdir(image_folder_name):
                if not file in working_folder_pat:
                    print('ERROR:  The existing "'+image_folder_name+'" Folder is not compatible with this configuration!')
                    print('        Please delete or rename the folder "'+image_folder_name+'" to allow the script')
                    print('        to generate a matching folder structure for your configuration')
                    sys.exit()  
            create_new_folders = False
    else: 
        try:
            os.makedirs(image_folder_name)
        except Exception as ex:
            print(' ERROR: Failed to create the image import folder on this directory!')
            print(' Msg.: '+str(ex))
            sys.exit()

###################################### Create new import folders for every partition   #######################################
    if create_new_folders:
        for folder in working_folder_pat:
            try:
                os.makedirs(image_folder_name+'/'+folder)
            except Exception as ex:
                print(' ERROR: Failed to create the partition import folder on this directory!')
                print(' Msg.: '+str(ex))
                sys.exit()

################################### Check that all required Partitions are available  ####################################
    raw_folder_dir =''
    vfat_folder_dir=''
    ext_folder_dir=''

    for part in partitionList:
        if part.type_hex=='a2':
            raw_folder_dir=excpath+'/'+image_folder_name+'/'+part.giveWorkingFolderName(False)
        elif part.type_hex=='b': # FAT
            vfat_folder_dir=excpath+'/'+image_folder_name+'/'+part.giveWorkingFolderName(False)
        elif part.type_hex=='83': # LINUX
            ext_folder_dir=excpath+'/'+image_folder_name+'/'+part.giveWorkingFolderName(False)

    # All folders there ?
    if raw_folder_dir =='':
        print('ERROR: The chosen partition table has now RAW/NONE-partition.')
        print('       That is necessary for the bootloader')
        sys.exit()
    if vfat_folder_dir =='':
        print('ERROR: The chosen partition table has now VFAT-partition.')
        print('       That is necessary for the Kernel image')
        sys.exit()
    if ext_folder_dir =='':
        print('ERROR: The chosen partition table has now EXT-partition.')
        print('       That is necessary for the rootfs')
        sys.exit()


####################################### Copy the bootloader files to the partition #######################################
    print(' --> Copy the bootloader file "'+BOOTLOADER_FILE_NAME+'" to the RAW partition')

    # Find the RAW Partition and 
    raw_folder_dir =''
    for part in partitionList:
        if part.type_hex=='a2':
            raw_folder_dir=excpath+'/'+image_folder_name+'/'+part.giveWorkingFolderName(False)
    if raw_folder_dir =='':
        print('ERROR: The chosen partition table has now RAW/NONE-partition.')
        print('       That is necessary for the bootloader')
        sys.exit()
    
    # Copy the bootloader file 
    try:
        shutil.copy2(u_boot_socfpga_dir+'/'+BOOTLOADER_FILE_NAME,
            raw_folder_dir+'/'+BOOTLOADER_FILE_NAME)
    except Exception as ex:
        print('EROR: Failed to copy the bootloader file! MSG: '+str(ex))
        sys.exit()

    print('     = Done')

###################################### Find a Linux build with the Yocto Project    ######################################
    print('--> Looking for the Yocto Project ')

    yocto_project_available =False

    # Directory of the Yocto Project rootfs .tar.gz file
    yocto_rootfs_dir =''
    yocto_rootfs_name='-'

    # Directory of the Yocto Project compressed Kernel file 
    yocto_zimage_dir  =''
    yocto_zimage_name ='-'
    
    # Directory of the Yocto Project uncomplied devicetree file
    yocto_devicetree_dir=''  
    yocto_devicetree_name='-'

    yocto_base_dir =os.path.join(os.path.expanduser('~')) +'/'+ YOCTO_BASE_FOLDER
    yocto_deployImgaes_dir = yocto_base_dir+'/build/tmp/deploy/images'
    yocto_device_dir = yocto_deployImgaes_dir+'/'+socfpga_devices_list[device_id]+'/'

    if os.path.isdir(yocto_base_dir):
        print('    The Yocto Installation was found!')
        #  Find a Yocto Linux Distribution that is compatible with this project
        print('--> Find a Yocto Linux Distribution that is compatible with this project')
        print('    Serarch Dir: "'+yocto_device_dir+'"')
    
        if os.path.isdir(yocto_device_dir):
            print('    A project with the same device "'+socfpga_devices_list[device_id]+'" was found')
            # Find the zImage, the rootfs and devicetree file if available
            for name in os.listdir(yocto_device_dir):
                
                if  os.path.isfile(yocto_device_dir+'/'+name) and \
                    not os.path.islink(yocto_device_dir+'/'+name):

                    if name.find("rootfs") !=-1:
                        yocto_rootfs_dir = yocto_device_dir+'/'+name
                        yocto_rootfs_name = name
                    elif name.find("zImage") !=-1:
                        yocto_zimage_dir = yocto_device_dir+'/'+name
                        yocto_zimage_name = name
                    elif name.find("devicetree") !=-1:
                        # NOTE: Must be checked!!
                        yocto_devicetree_dir = yocto_device_dir+'/'+name
                        yocto_devicetree_name = name 
            # Something found?
            yocto_project_available=  not yocto_rootfs_dir =='' and not yocto_zimage_dir==''
        if not yocto_project_available:
            print('     No Yocto Installation was found!')
    else:
        print('     No Yocto Installation was found!')

    if yocto_project_available:
        # Read the modication date of the Yocto Project rootfs file 
        modification_time = time.ctime(os.path.getmtime(yocto_rootfs_dir))
        
        print('\n################################################################################')
        print('#                                                                              #')
        print('#            COMPATIBLE YOCTO PROJECT LINUX DISTRIBUTION WAS FOUND             #')
        print('#                     Use this distribution for the build?                     #')
        print('--------------------------------------------------------------------------------')
        print('#                   --- Yocto Linux Distribution  ---                          #')
        print('#    Directory: "'+yocto_device_dir+'"  #')
        print('#    Modification Date: '+str(modification_time)+' #')
        print('#    rootfs: "'+yocto_rootfs_name+'" #')
        print('#    zImage: "'+yocto_zimage_name+'" #')
        print('#    Devicetree: "'+yocto_devicetree_name+'" #')
        print('--------------------------------------------------------------------------------')
        print('#                M: No, copy file manually instat                              #')
        print('#                Q: Abort                                                      #')
        print('#    anything else: Yes, use files for this build                              #')
        print('------------------------------------------------------------------------------')
        __wait3__ = input('Type anything to continue ... ')

        if __wait3__ =='q' or __wait3__=='Q':
            sys.exit()
        
        if not (__wait3__ =='m' or __wait3__=='M'):
            print('--> Copy the Yocto Project files to the "'+image_folder_name+'" folder')

            # Copy rootfs.tar.gz to the image parttition folder
            print('    Copy "'+yocto_rootfs_name+'" and rename it to "rootfs.tar.gz"')
            try:
                shutil.copy2(yocto_rootfs_dir,ext_folder_dir+'/rootfs.tar.gz')
            except Exception as ex:
                print('EROR: Failed to copy the rootfs file! MSG: '+str(ex))
                sys.exit()
            #NOTE: Check that is unzip is enabled!
            
            # Copy compressed Kernel image to the image parttition folder
            print('    Copy "'+yocto_zimage_name+'" and rename it to "zImage"')
            try:
                shutil.copy2(yocto_zimage_dir,vfat_folder_dir+'/zImage')
            except Exception as ex:
                print('EROR: Failed to copy the zImage file! MSG: '+str(ex))
                sys.exit()

            # Copy compressed Kernel image to the image parttition folder
            if not yocto_devicetree_dir == '':
                print('    Copy "'+yocto_devicetree_name+'" and rename it to "zImage"')
                # NOTE: Work required!!
                 #NOTE: Check that is devicetree compile is enabled!
            
#################################  Allow the user to import files to the partition folders  ###################################
    print('\n#############################################################################')
    print('#    Copy files to the partition folders to allow the pre-installment         #')
    print('#                    to the depending image partition                         #')
    print('#                                                                             #')
    print('#                     === Folders for every partition ===                     #')
    for part in partitionList:
        print('# Folder: "'+image_folder_name+'/'+part.giveWorkingFolderName(False)+'"| No.: '+ \
                                str(part.id)+' Filesystem: '+part.type+' Size: '+str(part.size_str))
    print('#                                                                            #')
    print('##############################################################################')
    print('#                                                                            #')
    print('#                    Compress the output image file?                         #')
    print('#     Should the output file be compressed as .zip to reduce the size        #')
    print('#     Image creator tools like "Rufus" can directly work with .zip files     #')
    print('#                                                                            #')
    print('#        Y: Compress the output image as .zip                                #')
    print('#        Q: Quit the script                                                  #')
    print('#        Any other input: Do not compress the output image                   #')
    print('#                                                                            #')
    print('##############################################################################')
    _wait_ = input('#              Please type ...                                               #')
    if _wait_ == 'q' or _wait_ == 'Q':
        sys.exit()
    elif _wait_ =='Y' or _wait_ =='y':
        compress_output = True
    else:
        compress_output = False
    print('##############################################################################')

################################## Scan the partition folders to list all directories #######################################
    print('\n---> Scan every partition folder to find all file directories')
    print('      and calculate the total partition size')
    try:
        for part in partitionList:
            # List every file inside the folder
            part.findFileDirectories(True,os.getcwd()+'/'+image_folder_name+'/'+part.giveWorkingFolderName(False))
            # Calculate the total file size of the partition 
            part.calculatePartitionFilesize(True)
    except Exception as ex:
        print(' ERROR: Failed to calculate the total partition size')
        print(' Msg.: '+str(ex))
        sys.exit()


################################# Insert the partition table to the BootImageCreator ######################################
    print('---> Insert the partition list to the image generator') 
    try:
        bootImageCreator = BootImageCreator(partitionList,str(imageFileName),os.getcwd())
    except Exception as ex:
        print(' ERROR: Failed to load the items of the XML file')
        print(' Msg.: '+str(ex))
        sys.exit()

############################################# Print the partition table ###################################################
    print('-> Print the loaded Partition table')
    bootImageCreator.printPartitionTable()

    _wait2_ = input('Start generating the image by typing anything to continue ... (q/Q for quite) ')
    if _wait2_ == 'q' or _wait2_ == 'Q':
        sys.exit()


############################################# Create the new Image File ###################################################
    bootImageCreator.generateImage()

############################# Print the Partition table of the image file with "fdisk" #####################################
    bootImageCreator.printFinalPartitionTable()

    if compress_output:
        print('---> Compress the output image as .zip')
        bootImageCreator.compressOutput(True,outputZipFileName)





        

####################################### Check if the partition folders are already available  #######################################



 
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
