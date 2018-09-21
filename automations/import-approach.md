# Pootle import approach

This is an outline in pseudocode of how the script to export strings from GitHub and import into Pootle should work. The intent of this file is to;

* validate the approach with other developers
* identify any logic issues or corner cases before implementing in code

The intended implementation is `bash`, primarily because filesystem operations are required, although a `python` implementation may be more maintainable.

## Summary of steps

1. Clone the latest `mycroft-skills` repo

1. Run `git submodule update --init` to populate all the Skills

1. Run the `extract.py` script

1. Copy the files from the `pots` directory this script creates to the `/var/www/pootle/env/lib/python2.7/site-packages/pootle/translations` directory inside the Pootle installation. This is equivalent to the `POOTLE_TRANSLATION_DIRECTORY` setting in the Pootle settings, so if possible we should use this for the script to be flexible / resilient in the future.

1. Run `(env) $ pootle update_stores --project=mycroft-skills` to update the Pootle stores. This has to be done from within the Python virtual environment. This is based on [this Pootle documentation](http://docs.translatehouse.org/projects/pootle/en/stable-2.8.x/server/project_setup.html).

1. Update the strings for the project using `(env) $ pootle update_stores --project=mycroft-skills --language=templates`

1. Sync the stores using `(env) $ pootle sync_stores --project=mycroft-skills`

1. Then `(env) $ pootle update_stores --project=mycroft-skills` again to update after sync'ing.

1. Using `wget ` or similar (possibly `curl`), make sure that [this page in Pootle]https://translate.mycroft.ai/admin/) shows a running worker in the Background Jobs section. Not sure if there's a way to run an API call or similar on Pootle as a better approach.


## Pseudocode for exporting strings from GitHub and importing into Pootle

```
BEGIN

cwd to the appropriate directory  - let's call it "import-script"

git clone  https://github.com/MycroftAI/mycroft-skills.git

cwd to the  mycroft-skills dir

git submodule update --init

cwd to the directory above

run the `extract.py` script

cwd to the Pootle virtual environment

(env) $ pootle update_stores --project=mycroft-skills --language=templates

(env) $ pootle sync_stores --project=mycroft-skills`

(env) $ pootle update_stores --project=mycroft-skills

wget https://translate.mycroft.ai/admin/ | grep 'worker running'

pipe output to mail or stderr

place script under a daily cron
