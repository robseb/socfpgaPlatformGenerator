
![GitHub](https://img.shields.io/static/v1?label=Ubuntu&message=18.04+LTS,+20.04+LTS&color=yellowgreen)
![GitHub](https://img.shields.io/static/v1?label=CentOS&message=7.0,+8.0&color=yellowgreen)
![GitHub](https://img.shields.io/static/v1?label=Intel+EDS&message=20.1&color=blue)
![GitHub](https://img.shields.io/github/license/robseb/socfpgaPlatformGenerator)
# Python Script to automaticly generate all necessary components for booting a embedded Linux on a Intel (ALTERA) SoC-FPGA
 build the bootloader (u-boot) and bring all components to a bootable for Intel (ALTERA) SoC-FPGAs 

![Alt text](doc/Concept.png?raw=true "Concept illustration")

<br>

**This Python allows to build with the Intel Embedded Development Suite (SoC EDS) the entire bootflow and generates an bootable image (.img) file to boot any Linux Distribution**

This Python script was designed to automate the always identical build flow for Intel SoC-FPGAs to reduce the possible sources of error during design. It can use the informations provided by the Quartus Prime project to compile and configure the bootloader (u-boot) to boot up an embedded Linux and to configure the FPGA fabric with the Quartus Prime project. During generation it is for the user enabled to select a compatible Yocto Project Linux Distribution or to copy a custom Linux Distribution to a Image folder. The Image folder conatins for every partition of the final SD-Card image a sub-folder. Files copied into these folders will automatically be pre-installed to the depending partition on the bootable SD-Card image. To achieve that is internaly my  [*LinuxBootImageFileGenerator*](https://github.com/robseb/LinuxBootImageFileGenerator) used to genrate a image file. 
Beside the executing of the script as a console application it is also enabled to use the included Python class to implement it into a custom build system. I used it to automate the entre generation of my embedded Linux [*rsyocto*](https://github.com/robseb/rsyocto) for *Intel* *SoC-FPGAs*.

It can run on any modern Linux operating system, such as CentOS or Ubuntu Linux with the pre-installed SoC EDS. 

___

# Features
* **Automatically generate a bootable image file with configuration provided by a Quartus Prime project**
* **Cloning and compiling of the *u-boot* bootloader for Intel SoC-FPGAs**
* **Allows *menuconfig* of *u-boot***
* **Installs and uses the *Linaro* cross-platform toolchain**
* **HPS Memory- and HPS I/O- configuration based on the Quartus Prime project settings**
* **Allows to use a pre-build bootloader execuatable and default u-boot script**
* **In case in the u-boot script is configured to load a FPGA configuration the depending FPGA configuration will be generated**
* **Detects if a compatibile Yocto Project Linux Distribution is available and can copy it to the partition**
* **Allows to pre-install any files or operating system to the SD-Card image**

* **Boot image *(.img)* file generation for distributing embedded Linux Distributions**
* **Up to 4 freely configurable partitions**
* **Configurable partition size in *Byte*,*Kilobyte*,*Megabyte* or *Gigabyte***
* **File structure for each partition will be generated and user files can be added**
* **Partition file size check** 
* **Dynamic mode: Partition size = Size of the files to add to the partition**
* **An offset can be added to a dynamic size (*e.g. for user space on the running Linux*)**
* **Linux device tree (*dts*) -files inside a partition can be automatically compiled and replaced with the uncompiled file**  
* **A u-boot script with the name "*boot.script*" inside a partition can be automatically compiled and replaced with the uncompiled file**
* **Compressed files *(e.g. "tar.gz")* containing for instance the Linux *rootfs* can be unzip and automatically added to the partition**
* **Image Sizes, Block Sizes, Start Sectors for every partition will be automatically generated for the depending configuration**
* **The final image file can be compressed to a "*zip*-archive file to reduce the image size**

* **Supported Filesystems**
    * **ext2**
    * **ext3**
    * **ext4**
    * **Linux**
    * **vfat**
    * **fat**
    * **swap**
    * **RAW**
* **Supported archive file types, that can be unzipped automatically**
    * *.tar* **-Archives**
    * *.tar.gz* **-Archives**
    * *.zip* **-Archives**
* **Tested Development Environments**
    * **Ubuntu 18.04 LTS**
    * **Ubuntu 20.04 LTS**
    * **CentOS 7.7**
    * **CentOS 8.0**
* **Supported Intel Embedded Development Suite (SoC EDS) Versions**
    * **EDS 20.1 (Linux)**
* **Supported Intel SoC-FPGAs**
    * **Intel Cyclone V**


# Getting started as a console application

For generating a bootable image for *Intel* SoC-FPGAs by executing a single Linux command please follow this step-by-step guide:
    
* Instal Intel Quartus Prime (18.1 or newer)
    *    A step-by-step guide how to install Intel Quartus Prime on Linux is available [here](https://github.com/robseb/NIOSII_EclipseCompProject#i-installment-of-intel-quartus-prime-191-and-201-with-nios-ii-support) (*NIOS II support is for this project not requiered*)
* Install the Intel Embedded Development Suite (SoC EDS)
    * [Download](https://fpgasoftware.intel.com/soceds/20.1/?edition=standard&platform=windows&download_manager=direct) Intel SoC EDS 20.1 Standard for Linux
    * Install SoC EDS by executing following Linux console commands
        ````shell
        chmod +x SoCEDSSetup-20.1.0.711-linux.run && ./SoCEDSSetup-20.1.0.711-linux.run
        ````
* Install the required packages
    ````shell
    sudo apt-get update -y && sudo apt-get install -y bison flex libncurses-dev \
         git device-tree-compiler  u-boot-tools
    ````
* Navigate into your Quartus Prime Project folder with the Linux console
    * The project configurations will then be used to build the bootable image 
    * Note: The project complabilation must be successfully finished 

* Clone this repository with the following Linux console command
    ````shell
    git clone https://github.com/robseb/socfpgaPlatformGenerator.git
    ````

**The Quartus Project folder should now look like this**

![Alt text](doc/project_folder.png?raw=true "Screenshot of the Quartus Prime Project")

* Navigate into the repository folder
    ````shell 
    cd socfpgaPlatformGenerator
* Start the Python script and follow the instructions
    ````shell
    python3 socfpgaPlatformGenerator.py
    ````
    * Note: The execution with root (*"sudo"*) privileges is not allowed


## Major activities of the script in console mode

1. **Generation of a XML configuration file**
     
    The script will generate the **XML-file** "SocFPGABlueprint.xml" ('*socfpgaPlatformGenerator/*'). It defines the blueprint of the final image `LinuxDistroBlueprint`.
    The `partition` object characterizes a partition on the final image. 
    A description of every attribute is available inside this file, as well. The default file is already suitable for *Intel* SoC-FPGAs.
    
        
    | File Name | Origin | Description | Disk Partition
    |:--|:--|:--|:--|
    | \"rootfs.tar.gz\"|copy from the Yocto Project or iniserted by hand| compressed Linux root file system |**2.: ext3** |
    |\"u-boot-with-spl.sfp\"| *generated* | *u-boot* bootloader executable |**3.: raw** |
    |\"uboot_cy5.scr\"|*generated*| by hand | Secondary bootloader script |**3.: vfat** |
    |\"zImage\"| copy from the Yocto Project or iniserted by hand | compressed Linux Kernel |**1.: vfat** |    
    |\"socfpga.dts\"| copy from the Yocto Project or iniserted by hand| Linux Device Tree |**1.: vfat** |
    |\"socfpga.rbf\"| *generated* | FPGA Config  |**1.: vfat** | 
     
    The following lines show the XML file of a partition configuration for *Intel* *SoC-FPGAs*.
    ````xml
    <?xml version="1.0" encoding = "UTF-8" ?>
    <!-- Linux Distribution Blueprint XML file -->
    <!-- Used by the Python script "LinuxDistro2Image.py" -->
    <!-- to create a custom Linux boot image file -->
    <!-- Description: -->
    <!-- item "partition" describes a partition on the final image file-->
    <!-- L "id"        => Partition number on the final image (1 is the lowest number) -->
    <!-- L "type"      => Filesystem type of partition  -->
    <!--   L       => ext[2-4], Linux, xfs, vfat, fat, none, raw, swap -->
    <!-- L "size"      => Partition size -->
    <!-- 	L	    => <no>: Byte, <no>K: Kilobyte, <no>M: Megabyte or <no>G: Gigabyte -->
    <!-- 	L	    => "*" dynamic file size => Size of the files2copy + offset  -->
    <!-- L "offset"    => in case a dynamic size is used the offset value is added to file size-->
    <!-- L "devicetree"=> compile the Linux Device (.dts) inside the partition if available (Top folder only)-->
    <!-- 	L 	    => Yes: Y or No: N -->
    <!-- L "unzip"     => Unzip a compressed file if available (Top folder only) -->
    <!-- 	L 	    => Yes: Y or No: N -->
    <!-- L "ubootscript"  => Compile the u-boot script file ("boot.script") -->
    <!-- 	L 	    => Yes, for the ARMv7A (32-bit) architecture ="arm" -->
    <!-- 	L 	    => Yes, for the ARMv8A (64-bit) architecture ="arm64" -->
    <!-- 	L 	    => No ="" -->
    <LinuxDistroBlueprint>
    <partition id="1" type="vfat" size="*" offset="1M" devicetree="Y" unzip="N" ubootscript="arm" />
    <partition id="2" type="ext3" size="*" offset="500M" devicetree="N" unzip="Y" ubootscript="" />
    <partition id="3" type="RAW" size="*" offset="20M"  devicetree="N" unzip="N" ubootscript="" />
    </LinuxDistroBlueprint>
    ````
    To change the available user space on the root file system change the *offset* value of the *ext3* partition. 


2. **Generation of a directory for every configured partition**

    The script will generate for every selected partition a depending folder. At this point it is enabled to drag&drop files and folders 
    to the partition folder. This content will then be included in the final image file. 
    Linux device tree- and archive-files, copied to the partition folder, will be automatically processed by the script incase these features were enabled for the partition inside the XML file. Of cause, archive files or uncompiled device tree files will not be added to the final image. 

    The following illustration shows generated folder structure with the previous XML configuration file.

    ![Alt text](doc/FolderStrucre.png?raw=true "Example of the folder structure")

3. **Generation of *u-boot* bootloader for Intel SoC-FPGA devices**
    
    The script will ask if the pre-build default bootloader should be used or the entire bootloader should be build. 

    In case the entire bootloader should be generated the script will do following tasks:
        * Download the Limaro cross-platform toolchain 
        * Generates the Board Support Package (BSP) with the Intel SoC EDS
        * Clone the (*u-boot-socfpga*)https://github.com/altera-opensource/u-boot-socfpga from Github
        * Runs the Intel SoC EDS filter script
        * Allow deeper *u-boot* configuration with **menuconfig**
        * Make the *u-boot* bootloader for the Intel SoC-FPGA device
        * The generated executeable will be copied to the RAW partition folder
    In case the default bootloader should be used
        * A pre-build bootloader with a default configuration will be copied to the RAW partition folder

4.a. **Use the Yocto Project output files as Linux Distribution to boot**
    That is stage is required bootloader based on the Quartus Prime project allredy generated. Now it is possible to insert files of a embedded Linux to a image folder.
    The script will check in the first step if compatible Yocto Project Linux Distribution files available. To achieve that will the Python script compare the folders inside following directory *"poky/build/tmp/deploy/images"* with
    the name of the SoC-FPGA device specified inside the Quartus Prime project. In case a compatible folder is avaibile the script will ask if these files should be used as the embedded Linux Distribution to boot. 
    Following message will appear: 

    ![Alt text](doc/yovto_msg.png?raw=true "Yocto Project found Message")

4.b. **Adding the files of a embedded Linux Distribution by hand to the Image folder**

    Instead to use the Yocto Project files it is possible to copy the files manually to partition folder. The files of this partition folder will then be pre-installed on the SD-Card image. 
    Uncomplied files, like the Linux Device Tree (*".dts"*)- or *u-boot* script (*".script"*) will automaticly complied be the script and only the compliled file will then be copied to the final image. 
    Compressed files (e.g. "*tar.gz*"), such as the compressed root file system (*rootfs.tar.gz*") will uncompressed, as well. This feature can be enabled or disabled within the XML configuration file.  
	The following illustration shows the folder structure of the partition folder (*"socfpgaPlatformGenerator/Image_partitions"*) depending of the XML partition table configurations. 
    
    ![Alt text](doc/project_folder.png?raw=true "Yocto Project found Message")

    Files copied a partition folder will then be pre-installed on to the depending partition. The following table shows the required file location for *Intel* SoC-FPGAs:

    | Partition Number | File System Type | Required Files | pre-installed by the script| Note 
    |:--|:--|:--|:--|:--|
    | **1** | *vfat* | Linux compressed Kernel file (*zImage*) | No |
    | **1** | *vfat* | Linux Device Tree File         (*.dts*) | No | Will be complied by the script
    | **1** | *vfat* | *u-boot* boot script (*.script*) | Yes | Will be complied by the script
    | **1** | *vfat* | FPGA configuration file (*.rbf*) | Yes |Will be created with the Quartus Project 
    | **2** | *ext3* | compressed root file system (*.tar.gz*) | No |  Will be unziped by the script
    | **3** | *RAW* | executable of the bootloader (*.sfp*) | Yes | Will be generated by the script

    
    **Copy or drag&drop your files/folders to these partition folders to pre-install these content to the final image.**
    **Note: Copy at this stage only the Linux files (*roofts*,*zImgae*,*device tree*) to the partition. The other files will be copied by the script in the next step!**

    *Note: On RAW partitions are only files allowed!*

5. **Chose if the output image should be compressed**
    The Python script allows to compress the generated bootable image files as a *".zip"* aerchive files. This can strongly reduce the image size.Tools, like "*rufus*" can process this "*.zip*" file directly and can bring it onto a SD-Card. 

6. **Copy additional files to all partitions or to the root file system (*rootfs*)**
    In the 5. step the script will unzip the *rootfs*. No it is enabled to change the partition or to copy files manually to the root file system of the embedded Linux Distribution. Following manual steps are allowed at this stage:
    * Change the *u-boot* boot script (*boot.script*)
    * Change the Linux Device Tree
    * Change files inside the Linux *rootfs* or copy one to it
    * Change or add files to the other partitions

7. **Generation of the bootable image file with custom configuration**
    
    The script will progress the data inside the Partition folders by compiling the Linux device tree, the u-boot script and will display the partition sizes for the entire image partition of bootable image file.
    In case the *u-boot* is configred to write the FPGA configuration the script will generate the depending FPGA configuration file. This only possible if no unlicensed IP is available inside the Quartus Prime Projects. For instance Quartus Prime projects congaing a Intel NIOS II Soft-Core processor can not be generated. The it is possible to copy a other FPGA configuration file to the image partition folder (*No.1 vfat*).
    
    
    ![Alt text](doc/partitionTable.png?raw=true "Partition table")
    *Example of a partition table calculated by the script*

    In connection the Python script will use the [*LinuxBootImageFileGenerator*](https://github.com/robseb/LinuxBootImageFileGenerator) to build the finale bootable image file. The file will be located inside the "*socfpgaPlatformGenerator*" folder. 


# Getting started as Python library 

Beside the usage of this Python script as an console application it is enabled to use it inside a other Python application.
The "*socfpgaPlatformGenerator*" extends the [*LinuxBootImageFileGenerator*](https://github.com/robseb/LinuxBootImageFileGenerator). For more informations about this libary please vist the GitHub reository of this project. 

The *socfpgaPlatformGenerator* consists of a single Python class:  

| Class | Description
|:--|:--|
| **SocfpgaPlatformGenerator**  | The entire boot image generator for *Intel* SoC-FPGAs |

The [*LinuxBootImageFileGenerator*](https://github.com/robseb/LinuxBootImageFileGenerator) will be automatically cloned from Github. 

The following steps describes in the right sequence the required Python methods to generate a bootable image file for *Intel* SoC-FPGAs:

1. **Generation of the partition table**

   To generate a partition table depending of "*SocFPGABlueprint.xml*" configurations use following methode.
   Here is check that all required configurations are selected inside the configuration file.
    ````python 
    #
    # @brief Create the partition table for Intel SoC-FPGAs by reading the "SocFPGABlueprint" XML-file
    # @return                      success
    #
    def GeneratePartitionTable(self):
    ````

2. **Generation of the entire bootloader based of the Quartus Prime Project configuration**
    
    Use following Python methode to generate the requiered bootloader for *Intel* SoC-FPGAs:
    ````python
    #
    # @brief Build the bootloader for the chosen Intel SoC-FPGA
    #        and copy the output files to the depending partition folders
    # @param generation_mode       0: The User can chose how the bootloader should be build
    #                              1: Always build or re-build the entire bootloader 
    #                              2: Build the entire bootloader in case it was not done
    #                              3: Use the default pre-build bootloader for the device 
    # @return                      success
    #
    def BuildBootloader(self, generation_mode= 0):
    ```` 

3. **Copy the Yocto Project Linux Distribution files to the partition**
    
    The following methode can copy the Linux *rootfs*, device tree and the conmpressed Kernel Image form the Yocto Project to the Image partition folder.
    ````python
    #
    # @brief Copy all essential Linux Distribution files (rootfs,zImage,Device Tree) to  
    #        the depending partition
    # @param copy_mode             0: The User can chose which files should be used 
    #                              1: Use compatible Yocto Project files
    #                              2: Use the existing files inside the partition
    # @note                        Use this method allways! It checks if all files are available
    # @return                      success
    #
    def CopyLinuxFiles2Partition(self,copy_mode=0):
    ```` 

4. **Generate a binary FPGA configuration file**
    
    The next Python methode allows to generate a FPGA binary configuration file ( *RAW Binary file (.rbf) with Passsive Parallel x8*) incase inside the "*u-boot*" configuration file was selected to write the FPGA configuration durring boot. 
    ````python
    #
    # @brief Create a FPGA configuration file for configure the FPGA during boot in case this
    #        feature was selected inside the u-boot script
    # @param copy_file             Only copy and rename a existing rbf file 
    # @pram  dir2copy              Directory with the rbf file to copy 
    # @return                      success
    #
    def GenerateBootFPGAconf(self,copy_file=False,dir2copy=''):
    ```` 

5. **Unzip the *rootfs* archvie file**
    
    To unzip the "*rootfs.tar.gz* archive file use following methode. After the execution it is enabled to change the entire partitions and the root file system.
    
    ````python
    #
    # @brief Scan every Partition folder and unpackage all archive files such as the rootfs
    # @return                      success
    #
    def ScanUnpackagePartitions(self):
    ````

6. **Generate the output bootable image file**

    The following methode can bring the partition table to a bootable image file (*img*). It is also enabled to zip the output file
    
    ````python 
    #
    #
    # @brief Generate a bootable Image file for the selected 
    #        feature was selected inside the u-boot script
    # @param ImageFileName         Name of the output ".img" image file
    # @param OutputZipFileName     Name of the output ".zip" compressed image file
    # @param compress_output       Compress the output image file to ".zip"
    # @param print_Table           Print the partatition table 
    # @return                      success
    #
    def GenerateImageFile(self,ImageFileName='',OutputZipFileName='', compress_output=False, \
                            print_Table= False):
    ````

<br>
<br>

___

# Author

**Robin Sebastian**

*socfpgaPlatformGenerator*, [*LinuxBootImageFileGenerator*](https://github.com/robseb/LinuxBootImageFileGenerator) and  [*rsyocto*](https://github.com/robseb/rsyocto) are Projects, that I have fully developed on my own.
No companies are involved in these projects.
I’m recently graduated as a master in electrical engineering with the major embedded systems (*M. Sc.*).

I'm open for cooperations as a freelancer to realize your specific requirements.
Otherwise, I‘m looking for an interesting full time job offer to share and deepen my shown skills.

**[Github sponsoring is welcome.](https://github.com/sponsors/robseb)**

[![Gitter](https://badges.gitter.im/rsyocto/community.svg)](https://gitter.im/rsyocto/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Email me!](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](mailto:git@robseb.de)

[![GitHub stars](https://img.shields.io/github/stars/robseb/socfpgaPlatformGenerator?style=social)](https://GitHub.com/robseb/socfpgaPlatformGenerator/stargazers/)
[![GitHub watchers](https://img.shields.io/github/watchers/robseb/socfpgaPlatformGenerator?style=social)](https://github.com/robseb/socfpgaPlatformGenerator/watchers)
[![GitHub followers](https://img.shields.io/github/followers/robseb?style=social)](https://github.com/robseb)

