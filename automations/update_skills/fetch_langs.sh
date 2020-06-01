#! /usr/bin/env bash

TRANSLATE_BASE='https://translate.mycroft.ai/export/?path='
PROJECT='mycroft-skills'

rm *.zip
rm -rf *-mycroft-skills
LANGS="sv de fr es hu ru ro nl pt_BR it da tr el es_LM"
for l in ${LANGS}; do
    echo "Fetching $l"
    wget -O ${l}.zip ${TRANSLATE_BASE}/${l}/${PROJECT}
    unzip ${l}.zip
done
rm *.zip
