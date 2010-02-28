#!/usr/bin/env python
"""
mose - MakeObject Script Environment
(c.) Michael 'Cruzer' Hohl

makeScript is scripting language for using the tool makeobj for packing addons for Simutrans.
"""

import cmd
import os, sys
import shutil, glob, fnmatch
import stat
import zipfile
from optparse import OptionParser

"""
Tools for handling with much files
Written by Vladimir Valsek
"""
def fix(caller, path, info):
	if caller == os.remove:
		os.chmod(path, stat.S_IWRITE + stat.S_IREAD);
		os.remove(path);

def copyPath(src, target):
    """Copies filesystem objects defined by wildcard in a shell-like manner."""
    objlist = glob.glob(src);
    for obj in objlist :
        if os.path.isfile(obj) :
            shutil.copy(obj, target);
        if os.path.isdir(obj) :
            shutil.copytree(obj, target);

def deletePath(pth):
    """Deletes filesystem objects defined by wildcard in a shell-like manner: whatever it is, away with it."""
    objlist = glob.glob(pth);
    for obj in objlist :
        if os.path.isfile(obj) :
            os.remove(obj);
        if os.path.isdir(obj) :
            shutil.rmtree(obj, onerror=fix);


"""
class MakeScript: Command Line Interpred
Written by Michae 'Cruzer' Hohl
"""
class MakeScript(cmd.Cmd):
    quiet = False
    exitscript = False
    startfile = ""
    version = "MOSE"
    var = {}
    
    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.prompt = "mose> "
        self.ruler = "-"
        self.version = """MOSE - MakeObj Script Environment [Version 0.3.4.0]
Copyright (C) 2009  Michael Hohl
This program comes with ABSOLUTELY NO WARRANTY; for details type 'license'.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
        self.var.update({"makeobj":os.getcwd()+"/makeobj"})
        if not(os.path.exists(self.var["makeobj"])):
            self.var.update({"makeobj":"makeobj"})
        self.var.update({"moutput":0})
        self.var.update({"only_error":0})
        
        parser = OptionParser("{0} [Option] [file]".format(args[0]))
        parser.add_option("-q", "--quiet", action="store_true", dest="verbose", default=False, help="don't print status messages to stdout")
        parser.add_option("-x", "--exit", action="store_true", dest="exit", default=False, help="qiuet after running script")
        (options, oargs) = parser.parse_args()
        if options.verbose:
            self.quiet = True
            self.prompt = ""
        if options.exit:
            self.exitscript = True
        if len(oargs)==1:
            self.startfile = oargs[0]
        else:
            self.output(self.version)

        self.var.update({"size":64})

    #Default: If the command is unkown, print an Error Message!
    def default(self, prm):
        if not(prm[0]=="#" or prm==""):
            self.output("Unkown command! Use 'help' for getting a list of all commands.")

    #Preloop: Called before starting mainloop.
    def preloop(self):
        if os.path.exists("config.mos"):
            self.onecmd("run config.mos")
        if not(self.startfile==""):
            self.output("mose> run {0}".format(self.startfile))
            self.onecmd("run {0}".format(self.startfile))
            return True

    def precmd(self, line):
        try:
            for key in self.var:
                line = line.replace("%{0}%".format(key), str(self.var[key]))
            return line
        except:
            return "echo System.Error in PreCMD Loop! Please contact application admin!"

    #!-Command: Comments or version indepentend commands.
    def do_shell(self, prm):
        prms = prm.split()
        if prms[0]=="mose":
            if prms[1]=="min_version" and int(prms[2])>3:
                self.output("For this script you need a newer MOSE version!")
                return True
            elif prms[1]=="intro":
                self.output(self.version)
        else:
            ps = prms[0].split("=")
            if len(ps)==2:
                self.var.update({ps[0]:ps[1]})

    #Shell-Help: A short description of shell command
    def help_shell(self):
        self.output(self.intro)
        self.output("""There are 3 types of commands in mose:
 ?xyz          Print a description of command xyz.
 !xyz          This is a comment.
 xyz           Run the 'xyz' command. For show a list of all commands type
               'help'!
 """)

    #Commands: do_* = Command, help_* = Help
    def do_build(self, prm):
        if int(self.var["moutput"])==1:
            OSCode = "{0} PAK{1} {2}".format(self.var["makeobj"], self.var["size"], prm)
        else:
            OSCode = "{0} PAK{1} {2} >NUL".format(self.var["makeobj"], self.var["size"], prm)
        errcode = os.system(OSCode)
        
        if errcode==3:
            self.output("Illegal Arguments!\nUse '?build' for get help! Error-Datail: '{0}'".format(OSCode))
        elif errcode==1:
            self.output("There is an error in DAT or PNG file!")
        elif errcode==0:
            if not(self.var["only_error"]==1):
                self.output("It seems that there is every thing right!")
        else:
            self.output("Errorlevel: '{0}'".format(errcode))
        return False

    def do_merge(self, prm):
        if int(self.var["moutput"])==1:
            errcode = os.system("{0} MERGE {1}".format(self.var["makeobj"], prm))
        else:
            errcode = os.system("{0} MERGE {1} >NUL".format(self.var["makeobj"], prm))
            
        if errcode==3:
            self.output("Illegal Arguments!\nUse '?build' for get help!")
        elif errcode==1:
            self.output("There is an error in DAT or PNG file!")
        elif errcode==0:
            if not(self.var["only_error"]==1):
                self.output("It seems that there is every thing right!")
        else:
            self.output("Errorlevel: '{0}'".format(errcode))
        return False
    

    def do_run(self, prm):
        if not(os.path.exists(prm)):
            self.output("File doesn'te exists!")
            return False
        ps = os.path.split(prm)
        x = os.getcwd()
        if not(ps[0]==""):
            os.chdir(ps[0])
        try:
            with open(prm, "r") as fobj:
                for line in fobj:
                    self.onecmd(self.precmd(line))
        except IOError as e:
            self.output("Can't run this script file!")
        os.chdir(x)
    def do_copy(self, prm):
        if not(prm==""):
            prms = prm.split()
            try:
                shutil.copy(prms[0], prms[1])
            except:
                self.output("File '{0}' can't copy.".format(prms[0]))
        else:
            self.output("Command 'copy' needs more arguments!")

    def do_xcopy(self, prm):
        if not(prm==""):
            prms = prm.split()
            try:
                copyPath(prms[0], prms[1])
            except:
                self.output("Files '{0}' can't Xcopy.".format(prms[0]))
        else:
            self.output("Command 'copy' needs more arguments!")

    def do_chdir(self, prm):
        if not(os.path.exists(prm)):
            self.output("Directory didn't exists!")
        else:
            os.chdir(prm)
            self.output("Current directory: {0}".format(os.getcwd()))

    def do_ls(self, prm):
        if prm=="":
            prm = os.getcwd()
        for file in os.listdir(prm):
            self.output(file)

    def do_mkdir(self, prm):
        if os.path.exists(prm):
            if not(int(self.var["only_error"])==1):
                self.output("Directory '{0}' already exists!".format(prm))
            return False
        try:
            os.mkdir(prm)
        except:
            self.output("Can't create directory '{0}'!".format(prm))

    def do_rmdir(self, prm):
        if not(os.path.exists(prm)):
            if not(int(self.var["only_error"])==1):
                self.output("Directory '{0}' doesn't exists!".format(prm))
            return False
        deletePath(prm)
        try:
            pass
        except:
            self.output("Can't remove directory '{0}'!".format(prm))

    def do_echo(self, prm):
        self.output(prm)

    def do_zip(self, prm):
        try:
            zfile = zipfile.ZipFile(prm.split()[0], "a")
            for prms in prm.split()[1:]:
                if os.path.isfile(prms):
                    zfile.write(prms)
                else:
                    try:
                        prmfs = os.path.split(prms)
                        if prmfs[0]=="":
                            prmfs[0]="{0}\\".format(os.getcwd())
                        for file in os.listdir(prmfs[0]):
                            if fnmatch.fnmatch(file, prmfs[1]):
                                zfile.write(file)
                    except:
                        self.output("Can't include file '{0}'!".format(prms))
            zfile.close()
        except:
            self.output("Can't open '{0}'!".format(prm.split()[0]))

    def do_zextract(self, prm):
        try:
            zfile = zipfile.ZipFile(prm.split()[0], "r")
            if len(prm)==2:
                zfile.extractall(prm.split()[1])
            else:
                zfile.extractall()
            zfile.close()
        except:
            self.output("Can't open '{0}'!".format(prm.split()[0]))

    def do_exit(self, prm):
        if prm=="":
            self.output("Good bye!")
        elif prm=="-w":
            self.output("Press 'Enter' for close the script environment...")
            input()
        elif not(prm=="-q"):
            ptint("Illegal Argument!")
        return True

    

    def do_config(self, prm):
        if prm=="":
            self.output("Use '?config' for get help!")
        prms = prm.split("=")
        if prms[0]=="makeobj":
            self.var.update({"makeobj":prms[1]})
        elif prms[0]=="paksize":
            self.var.update({"size":int(prms[1])})
        elif prms[0]=="moutput":
            self.var.update({"moutput":int(prms[1])})
        elif prms[0]=="only_error":
            self.var.update({"only_error":int(prms[1])})
        elif prms[0]=="chdir":
            try:
                os.chdir(prms[1])
            except:
                self.output("Can't change directory. MOSE must be quit.")
                return True
        else:
            self.output("Unkown value!")

    def do_ver(self, prm):
        self.output(self.version)

    def do_license(self, prm):
        self.output("""MOSE - MakeObj Script Engine
Copyright (C) 2009  Hohl Michael

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
""")


    #Help: do_* = Command, help_* = Help
    def help_config(self):
        self.output("""Change settings of the script environment.
Syntax: config setting=value

setting       The variable which should be changed. Could be on of this:
               makeobj       Defines the makeobj executable.
               paksize       Defines the size of the Pak set.
               moutput       If moutput is 1 all messages would be written on
                              screen.
               only_error    If onyl_error is 1 only error messages would be
                              displayed!
               chdir         Change current working directory.
""")

    def help_copy(self):
        self.output("""Copy one file to another place.
Syntax: copy sourcefile destinationfile
""")

    def help_xcopy(self):
        self.output("""Copy files or directorys to another place. It's also able to use patterns!
Syntax: xcopy sourcefile destinationfile

sourcefile    Could be a directory, a file or a pattern (like '*.tab')
destination   Could be file or a directory (don't use a / at the end if it is a
               directory!)
""")

    def help_zip(self):
        self.output("""Add an inputfile, to the zipfile.
Syntax: zip zipfile inputfile1 [inputfile2 [inputfile3]

zipfile       Could be any zip file. If it already exist, the inputfile would be
              add to it.
inputfile     Could be a pattern or a file.
""")

    def help_ls(self):
        self.output("""List all files in a directory.
Syntax: ls [directory]

directory     Could be any directory which should be list.
""")

    def help_build(self):
        self.output("""Create a pak file out of a dat file.
Syntax: build [outputfile inputfile1 [inputfile2 [inputfile3]]

outputfile    Could be a directory or a file. In this file/directory, all object
              would be build.
inputfile     Could be a directory or a file. This file/directory must be the
              dat file!
""")
        
    def help_merge(self):
        self.output("""Pack a handful pak-files into one pak-file
Syntax: merge [outputfile inputfile1 [inputfile2 [inputfile3]]

outputfile    Could be a directory or a file. In this file/directory, all object
              would be build.
inputfile     Could be a directory or a file. This file/directory must be the
              dat file!
""")

    def help_exit(self):
        self.output("Close the script environment.")

    def help_ver(self):
        self.output("ver prints the version of mose.")

    def help_echo(self):
        self.output("""Echo prints a various text on the screen.
Syntax: echo text

text          Could be any text. This text would be print on display.
""")
    def output(self, text):
        if self.quiet==False:
            print(text)

"""
Run MakeScript class
"""

if __name__ == "__main__":
	mose = MakeScript(sys.argv)
	mose.cmdloop()
