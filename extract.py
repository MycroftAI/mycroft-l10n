#!/usr/bin/python3

# VERSION 1.2
# Run this file in the Skills repo to extract all translatable strings.

import os
from glob import glob

ftag = "_(\""
btag = "\")"

def main():

    pathlist = glob("skills/**/en-us/**.*", recursive=True)

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
        if not os.path.exists('pots/' + dir):
            os.makedirs('pots/' + dir)
        gtxtcommand = "xgettext --keyword=_ --language=Python --add-comments " + \
                    "--output='pots/" + dir +".pot' tags/" + dir + "/*.*"
        os.system(gtxtcommand)

if __name__ == '__main__':
    main()