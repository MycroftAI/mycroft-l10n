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


# VERSION 1.2

import os
from glob import glob

ftag = "_(\""
btag = "\")"


pathlist = glob("**/en-us/**.*", recursive=True)

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
                temp.write('{0}{1}{2}{3}'.format(ftag, line.strip("\n"), btag,
                           "\n"))
        
skilllist = os.listdir('tags')
for dir in skilllist:
    gtxtcommand = "xgettext --keyword=_ --language=Python --add-comments " + \
                  "--output='pots/" + dir +".pot' tags/" + dir + "/*.*"
    os.system(gtxtcommand)