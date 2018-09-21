# Mycroft Translation Framework

This repository contains scripts and helper tools which are used to help automate translations between `mycroft-skills` and our Pootle infrastructure - https://translate.mycroft.ai

## How translations are imported into Pootle

See: http://docs.translatehouse.org/projects/pootle/en/stable-2.8.x/server/project_setup.html

for an introduction

In the Pootle configuration, there is a setting called `POOTLE_TRANSLATION_DIRECTORY` [documentation](http://docs.translatehouse.org/projects/pootle/en/stable-2.8.x/server/settings.html#std:setting-POOTLE_TRANSLATION_DIRECTORY) that specifies where the translations are stored.

On our host, `POOTLE_TRANSLATION_DIRECTORY` is set to ;
`/var/www/pootle/env/lib/python2.7/site-packages/pootle/translations#`

## How translations are exported from Pootle



## Credits

Andrew Wilson - @ajwkc
