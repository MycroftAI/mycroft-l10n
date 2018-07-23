# Andrew Wilson (ajwkc)
# July 12, 2018
# Mycroft AI
# Translatable String Extraction Script
#
# PSEUDOCODE
# 
# 1) Search the file system for /en-us directories.
# 2) For each file within /en-us, append _(" to the beginning and ") to 
#    the end of each line, marking the strings for gettext extraction.
# 3) Run gettext on each file and place in appropriate folder.

import os
import glob # Python 3 required for recursive glob search
#import fileinput

ftag = "_(\""
btag = "\")"

'''
# VERSION 1.0

for path, dirs, files in os.walk(here):
    if 'en-us' in dirs:
        en_path = os.path.join(path,'en-us')
        for f in os.listdir(en_path):
            f_path = os.path.join(en_path,f)

            linecount = 1
            for line in fileinput.input(f_path, inplace=1):
                print('{0}{1}{2}'.format(ftag, line.strip('\n'), btag))
                linecount += 1
            os.system("echo Finished tagging " + os.path.basename(f_path))
            os.system("xgettext --keyword=_ --language=Python --add-comments -o" + os.path.basename(f_path) + ".pot " + f_path)
'''

'''
# VERSION 1.1

pathlist = glob.glob("**/en-us/**.*", recursive=True)
for path in pathlist:
    os.system("echo Began tagging " + path)
    linecount = 1
    for line in fileinput.input(path, inplace=1):
        if not (line.startswith(ftag) or line.startswith("\n")):
            print('{0}{1}{2}'.format(ftag, line.strip("\n"), btag))
            os.system("echo Tagged line " + str(linecount) + " of " + os.path.basename(path))
            linecount += 1
    os.system("echo Finished tagging " + path)
    os.system("xgettext --keyword=_ --language=Python --add-comments -o " + os.path.basename(path) + ".pot " + path)
'''

# VERSION 1.2

pathlist = glob.glob("**/en-us/**.*", recursive=True)

if not os.path.exists('tags'):
    os.mkdir('tags')

if not os.path.exists('pots'):
    os.mkdir('pots')

for path in pathlist:
    os.system("echo Began tagging " + path)
    dirpath, file = os.path.split(path)
    dirpath = os.path.split(dirpath)[0].strip("skills/")
    skill, subfolder = os.path.split(dirpath)
    tagpath = os.path.join('tags', skill)
    
    with open(path, 'r') as source:

        tagdir = os.path.join('tags', skill)

        if not os.path.exists(tagdir):
            os.makedirs(tagdir)
            
        with open(os.path.join(tagdir,file), 'w') as temp:
            linelist = source.readlines()
            for line in linelist:
                temp.write('{0}{1}{2}{3}'.format(ftag, line.strip("\n"), btag, "\n"))
        

skilllist = os.listdir('tags')
for dir in skilllist:
    gtxtcommand = "xgettext --keyword=_ --language=Python --add-comments --output='pots/" + dir +".pot' tags/" + dir + "/*.*"
    os.system(gtxtcommand)


