# importer.sh
#
# Script to harvest strings for translation from the GitHub
# `mycroft-skills` repo and import them into Pootle.
#
# kathy.reid@mycroft.ai
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
POOTLE_TRANSLATION_DIRECTORY=/var/www/pootle/env/lib/python2.7/site-packages/pootle/translations
LOCAL_REPO_NAME=mycroft-skills

# echo "MYCROFT_SKILLS_REPO is " $MYCROFT_SKILLS_REPO

# Clone the latest `mycroft-skills` repo
# and import all the gitmodules
#git clone $MYCROFT_SKILLS_REPO $LOCAL_REPO_NAME
#cd  $LOCAL_REPO_NAME
#git submodule update --init
#cd ../

# Run the extract.py script
# @TODO I'm fairly sure this script assumes the name of
# the locally cloned mycroft-skills repo, may need to update that
./extract.py

# copy the contents of the pots directory to the Pootle translations dir
cp -r pots/* $POOTLE_TRANSLATION_DIRECTORY/


# Clean up
#@TODO assumes  cwd is this dir - may need to check that, change cwd

#rm -R $LOCAL_REPO_NAME
#cd $LOCAL_REPO_NAME

#rm -R pots
#rm -R tags


echo "end script" 
