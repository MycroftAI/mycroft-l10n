# importer.sh
#
# Script to harvest strings for translation from the GitHub
# `mycroft-skills` repo and import them into Pootle.
#
# kathy.reid@mycroft.ai
# based on significant work by Andrew Wilson
# September 2018

# Summary of Steps
#
#  Clone the latest `mycroft-skills` repo
#  Run `git submodule update --init` to populate all the Skills
#  Run the `extract.py` script
#  Copy the files from the `pots` directory this script creates to the `/var/www/pootle/env/lib/python2.7/site-packages/pootle/translations` directory inside the Pootle installation. This is equivalent to the `POOTLE_TRANSLATION_DIRECTORY` setting in the Pootle settings, so if possible we should use this for the script to be flexible / resilient in the future.
#  Run `(env) $ pootle update_stores --project=mycroft-skills` to update the Pootle stores. This has to be done from within the Python virtual environment. This is based on [this Pootle documentation](http://docs.translatehouse.org/projects/pootle/en/stable-2.8.x/server/project_setup.html).
#  Update the strings for the project using `(env) $ pootle update_stores --project=mycroft-skills --language=templates`
#  Sync the stores using `(env) $ pootle sync_stores --project=mycroft-skills`
#  Then `(env) $ pootle update_stores --project=mycroft-skills` again to update after sync'ing.
#  Using `wget ` or similar (possibly `curl`), make sure that [this page in Pootle]https://translate.mycroft.ai/admin/) shows a running worker in the Background Jobs section. Not sure if there's a way to run an API call or similar on Pootle as a better approach.

# Setup variables
MYCROFT_SKILLS_REPO=https://github.com/MycroftAI/mycroft-skills.git
POOTLE_TRANSLATION_DIRECTORY=/var/www/pootle/env/lib/python2.7/site-packages/pootle/translations/mycroft-skills
LOCAL_REPO_NAME=/root/mycroft-translate/automations/mycroft-skills
AUTOMATIONS_DIR=/root/mycroft-translate/automations

# check to see that the  xgettext utility is available, abort if not
command -v xgettext >/dev/null 2>&1 || { echo >&2 "I require gettext but it's not installed.  You need to run `sudo apt-get install gettext`. Aborting."; exit 1;} 

echo "MYCROFT_SKILLS_REPO is " $MYCROFT_SKILLS_REPO
echo "LOCAL_REPO_NAME is " $LOCAL_REPO_NAME

# Clone the latest `mycroft-skills` repo
# and import all the gitmodules
git clone $MYCROFT_SKILLS_REPO $LOCAL_REPO_NAME
cd  $LOCAL_REPO_NAME
git submodule update --init
cd ../

# Run the extract.py script
# @TODO I'm fairly sure this script assumes the name of
# the locally cloned mycroft-skills repo, may need to update that
python3 extract.py


# Activate the Pootle virtual environment
cd /var/www/pootle/
echo "pwd is: " $PWD
source env/bin/activate

# Update from database to filesystem
pootle sync_stores --project=mycroft-skills


# copy the contents of the pots directory to the Pootle translations dir
cp -r $AUTOMATIONS_DIR/pots/* $POOTLE_TRANSLATION_DIRECTORY/

# Update from filesystem to database
pootle update_stores --project=mycroft-skills

# Update from database to filesystem
pootle sync_stores --project=mycroft-skills

# For each Skill, for each language, we need to create a *.po file from a *.pot file
# Example: pot2po -t decide-skill-ca.po decide-skill.pot decide-skill-ca.po
# More info at: http://docs.translatehouse.org/projects/pootle/en/stable-2.8.x/server/project_setup.html#project-setup-updating-strings
 
# Find which languages are in use
# Assumes the virtual environment is still activated

cd $POOTLE_TRANSLATION_DIRECTORY/

LANGUAGE_LIST="$(pootle list_languages)"

echo "getting list of languages ..."
echo $LANGUAGE_LIST

i=0
for LANGUAGE in $LANGUAGE_LIST
do
    echo "adding " $LANGUAGE "to array ..."
    langArr[$i]=$LANGUAGE
    i=$((i+1))
done

echo "there are " $i "languages"

cd $POOTLE_TRANSLATION_DIRECTORY

SKILL_LIST="$(ls | grep ".pot$" )"

echo "getting list of skills ..." 
echo $SKILL_LIST

j=0
for SKILL in $SKILL_LIST
do
   echo "adding " $SKILL "to array ..."
   skillArr[$j]=$SKILL
   tmp=${skillArr[$j]}
   tmp2=${tmp%%.pot*}
   skillArr[$j]=$tmp2
   echo "added " $tmp2 "to array ..."
   j=$((j+1))
 
done

echo "there are " $j "skills"

# Now, we loop through both and create the relevant *.po files

echo "now creating *.po files ..."

m=0
for k in "${langArr[@]}"
do
    echo "k is: " $k
    for l in "${skillArr[@]}"
    do
      echo "l is: " $l
      pot2po -t $l-$k.po $l.pot $l-$k.po
      m=$((m+1))
    done
done

echo "created " $m "*.po files"


# Update from file system to database
pootle update_stores --project=mycroft-skills

# Deactivate the virtual environment
 echo "pwd is: " $PWD
 deactivate


# Prove that the script worked correctly
#@TODO I'm not sure the best way to do this, 
# possibly a curl to get a page and check for a string?

# Clean up
#@TODO assumes  cwd is this dir - may need to check that, change cwd

cd $AUTOMATIONS_DIR

echo "pwd is: " $PWD
echo "now cleaning up directories that were created..."
echo "removing pots directory..."
rm -R pots
echo "removing tags directory..."
rm -R tags
echo "removing " $LOCAL_REPO_NAME
rm -R $LOCAL_REPO_NAME

echo "end script" 
