#!/usr/bin/python3

# VERSION 1.2
# Run this file in the Skills repo to extract all translatable strings.

import os
from glob import glob

ftag = "_(\""
btag = "\")"

def main():

    oldstylepaths = glob("mycroft-skills/**/en-us/**.*", recursive=True)
    print("\n pathlist is: " )  
    for path in oldstylepaths:
        print (path) 

    # add locale path to the pathlist
    newstylepaths = glob("mycroft-skills/locale/en-us/**.*", recursive=True)
    print("\n pathlist is: " )  
    for path in newstylepaths:
        print (path)

    combinedpaths = oldstylepaths + newstylepaths


    if not os.path.exists('tags'):
        os.mkdir('tags')

    if not os.path.exists('pots'):
        os.mkdir('pots')
    for path in combinedpaths:
        print(" ======================================== \n")
        print(" Began tagging the path " + path)

        dirpath, file = os.path.split(path)
        print("\n first dirpath is:  " + dirpath)
        dirpath = os.path.split(dirpath)[0].replace('mycroft-skills/', '')
        print("\n second dirpath is: " + dirpath)
        print("\n file is:  " + file)

        skill, subfolder = os.path.split(dirpath)
        print("\n skill is:  " + skill)

        tagpath = os.path.join('tags', skill)
        print("\n tagpath is:  " + tagpath)


        with open(path, 'r') as source:
            tagdir = os.path.join('tags', skill)
            if not os.path.exists(tagdir):
                os.makedirs(tagdir)
            with open(os.path.join(tagdir,file), 'w') as temp:
                linelist = source.readlines()
                for line in linelist:
                    line = line.replace(r'"', r'\"')
                    print("line is:  " + line)
                    temp.write('{0}{1}{2}{3}'.format(ftag, line.strip("\n"), btag,
                            "\n"))

    skilllist = os.listdir('tags')

    for dir in skilllist:
        print("dir is :  " + dir + "\n \n \n")
        if not os.path.exists('pots/' + dir):
            os.makedirs('pots/' + dir)
            print("\n creating dir: " + ('pots/' + dir))
        gtxtcommand = "xgettext --keyword=_ --language=Python --add-comments " + \
                    "--output='pots/" + dir +".pot' tags/" + dir + "/*.*"

        print("\n gtxtcommand is:  " + gtxtcommand + "\n")
        os.system(gtxtcommand)
        print("\n created file: " +  'pots/' + dir + '.pot')

if __name__ == '__main__':
    main()
