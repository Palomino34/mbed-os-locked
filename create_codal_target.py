import os 
from os import walk
from os import listdir
from subprocess import call
from subprocess import check_output

#
# create_codal_target.py
#
# Takes a working build of an mbedos "blinky" and cretes a static library containing mbed functionality
# Also extracts neessary header files.
#

#
# Function to create a directory, if necessary.
#
def create_dir(directory):
    if not os.path.exists(directory):
#print ("making1...." + directory)
        #call(["mkdir", "-p", directory])
        os.makedirs(directory)
        #print ("making2....")    

#
# Function to parse the link file descriptions, and return a list of object files.
#
def generate_lib(infilename, outfile) :
    infile = open(infilename)

    params = infile.readline().split(" ")
    #cmd = ["arm-none-eabi-ar", "-rcs", outfile]
    cmd = ["arm-none-eabi-ld", "-Ur", "-o", outfile]
    objs = []
    

    for item in params :
        #print(item)
        if item.endswith(".o") and not item.endswith("main.o") :
            if item.startswith('"') and item.endswith('"') :
                objs.append(item[1:-1])                
            else :
                objs.append(item)               
    # We should no have filtered out all but the object files.
    #for item in objs:
    #    print item 
   
    for item in objs:
        shit = []
        shit.append(item)   
        call(cmd + shit)

#
# Function to parse the link file descriptions, and return a list of object files.
#
def generate_o(infilename, outdir) :

    infile = open(infilename)

    params = infile.readline().split(" ")
    

    for item in params :       
        if item.endswith(".o\"") and not item.endswith("/main.o\"") :
            if item.startswith('"') and item.endswith('"') :
                obj = item[1:-1]
            else :
                obj = item

            #print(obj)
            
            obj = obj.replace("/","\\")
            outdir = outdir.replace("/","\\")
            
            objNoExt = obj.replace(".o", "")
            objNoExtPath = objNoExt.replace("BUILD\\NUCLEO_L452RE_P\\GCC_ARM-RELEASE\\", "..\\source\\")
            
            
            if not os.path.exists(objNoExtPath + ".c") and not os.path.exists(objNoExtPath + ".cpp") and not os.path.exists(objNoExtPath + ".s"):
                cmd = 'copy /y ' +  obj + ' ' + outdir + ' > NUL'
                os.system(cmd)                
            else:
                print('Found ' +  obj)
                           
                
            #cmd = ["copy /y ", obj , outdir ]    
            #print(cmd)
            #call (cmd)
            #cmd = 'copy /y ' +  obj + ' ' + outdir + ' > NUL'
            #print(cmd)
            #os.system(cmd)
            #shutil.copy('file1.txt', 'file3.txt')


#
# Function to extract a copy of all necessary include files.
#
def generate_includes(infilename, outdir) :

    infile = open(infilename)

    create_dir(outdir)

    if not outdir.endswith("/") :
        outdir = outdir + "/"

    cwd = os.getcwd().replace("\\","/") + "/"

    params = infile.readline().split(" ")
    dirs = []

    for item in params :
        if item.startswith('"') and item.endswith('"') :
            item = item[1:-1]

        if item.startswith("-I") :
            inc = item[2:]
            if inc.startswith('"') and inc.endswith('"') :
                inc = inc[1:-1]

            inc = inc.replace("\\","/")

            if inc.startswith(cwd) :
                inc = inc[len(cwd):]

            if os.path.exists(inc) :
                dirs.append(inc)            

    # We should no have filtered out all but the object files.
    for item in dirs :
        out = outdir + item
        
        if out.startswith('./codal-mbedos/inc/./mbed-os'):
            out1 = out[28:]
            out1 = 'RECURSIVE_FIND_DIR(INCLUDE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/${CODAL_OUTPUT_NAME}/inc' + out1 + '" "*.h"'
            #print(out1)
        
        create_dir(out)
        
        #cmd = ["sh", "-c", "cp " + item + "/*.h " + out]
        agrs = item + "/*.h " + out
        
        agrs = agrs.replace("/","\\")
       
        cmd = 'copy /y ' + agrs + ' > NUL'                                

        headers = [f for f in listdir(item) if f.endswith(".h")]
        

        if (len(headers) > 0) :
            #print(cmd)
            #call(cmd)
            os.system(cmd)
#
# Search the given folder structure for a file matching the given prefic and postfix. 
# Return the first match we find.
#
def find_file(prefix, postfix, directory) :
    for (dirpath, dirnames, filenames) in walk(directory) :
        for (f) in filenames :
            if f.startswith(prefix) and f.endswith(postfix) :
                return dirpath + "/" + f;

# Determine our target
targetnamestring = check_output(["mbed","target"]).decode("utf-8") 
#print (targetnamestring)
#targetname = targetnamestring[targetnamestring.index(" ") + 1:].strip()
#print ("This is targetname:")
#print (targetname)
#print ("End")
targetname = "NUCLEO_L452RE_P"
# targetname = "NUCLEO_L476RG"
#targetname = "NUCLEO_F401RE"

# The file containing the command line linker
#linkfilename = find_file (".link_files", ".txt", "BUILD/" + targetname + "/GCC_ARM")
linkfilename = find_file (".link_", ".txt", "BUILD/" + targetname + "/GCC_ARM-RELEASE")
print (linkfilename)

# The file containing the compile time include paths 
includefilename = find_file (".includes_", ".txt", "BUILD/" + targetname + "/GCC_ARM-RELEASE")
print (includefilename)
# The directory to store our output in
outputdir = "./codal-mbedos"


#
# Create a subdirectory for export, and populate with a generated static library and include files.
#

create_dir(outputdir)
create_dir(outputdir+"/obj")
#
#print("Creating codal-mbedos library...")
#generate_lib(linkfilename, outputdir + "/mbedos.o") 
print("Creating codal-mbedos object...")
generate_o(linkfilename, outputdir + "/obj") 
#
print("Creating codal-mbedos includes...")
generate_includes(includefilename, outputdir + "/inc")

print("done.")
