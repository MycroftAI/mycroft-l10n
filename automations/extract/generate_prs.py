#! /usr/bin/env python

# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import json
from os.path import join, exists
from requests import get

import polib
from github_actions import get_work_repos, create_work_dir, create_or_edit_pr

DEFAULT_BRANCH = '19.02'
SKILLS_URL = ('https://raw.githubusercontent.com/MycroftAI/mycroft-skills/'
              '{}/.gitmodules')


def get_skill_repos(branch=None):
    """ Fetches the skill list from the mycroft-skills repo and returns
        a dict mapping paths to urls

        Arguments:
            branch: branch of the repo to use

        Returns: dict with path-url pairs
    """
    branch = branch or DEFAULT_BRANCH
    response = get(SKILLS_URL.format(branch))
    skills = response.text.split('\n')

    d = {}
    key = None
    for l in skills:
        if 'path = ' in l:
            key = l.split(' = ')[1].strip()
        elif key and 'url = ' in l:
            d[key] = l.split(' = ')[1].strip()
            key = None
        else:
            key = None
    return d


def download_lang(lang):
    # TODO
    # build url for language code

    # use wget module to download

    # use zip to unpack

    # return path # Path to directory with po_files
    pass


with open('occurrences.json') as f:
    occurrences = json.load(f)


def is_translated(path):
    """ Checks if all files in the translation has at least one translation.

    Arguments:
        path (str): path to po-file

    Returns: True if all files in translation has at least one translation,
             otherwise False.
    """
    po = polib.pofile(path)
    files = []
    for e in po:
        files += [f[0] for f in e.occurrences]
    all_files = sorted(set(files))
    translated_entities = [e for e in po if e.translated()]
    files = []
    for e in translated_entities:
        files += [f[0] for f in e.occurrences]
    translated_files = sorted(set(files))

    return translated_files == all_files


def parse_po_file(path, skill):
    """ Create dictionary with translated files as key containing
    the file content as a list.

    Arguments:
        path: path to the po-file of the translation

    Returns:
        Dictionary mapping files to translated content
    """
    out_files = {}  # Dict with all the files of the skill
    # Load the .po file
    po = polib.pofile(path)

    for entity in po:
        # Escape the citation signs (")
        for f in occurrences[skill][entity.msgid.replace("\"", r"\"")]:
            content = out_files.get(f, [])
            content.append(entity.msgstr)
            out_files[f] = content

    return out_files


def insert_translation(path, translation):
    for filename in translation:
        with open(join(path, filename), 'w+') as f:
            f.writelines([l + '\n' for l in translation[filename]])


pootle_langs = {
    'sv-se': 'sv',
    'de-de': 'de',
    'fr-fr': 'fr',
    'ru-ru': 'ru',
    'es-es': 'es'
}


def main():
    skill_repos = get_skill_repos()

    for skill in skill_repos:
        # Get repo information
        skill_url = skill_repos[skill]
        if 'mycroftai/' not in skill_url.lower():
            print('Skipping {}'.format(skill_url))
            continue
        # Get git repo and github connections
        fork, upstream = get_work_repos(skill_url)
        work = create_work_dir(upstream, fork) # local clone
        # Checkout new branch
        branch = 'translations'
        work.checkout('-b', branch)

        langs = []
        for lang in pootle_langs:
            # Build po-file path
            f = (join(pootle_langs[lang] + '-mycroft-skills',
                      pootle_langs[lang],
                      'mycroft-skills',
                      skill + '-' + pootle_langs[lang] + '.po'))
            if not exists(f) or not is_translated(f):
                print('Skipping {}'.format(f))
                continue
            langs.append(lang)
            print('Processing {}'.format(f))
            translation = parse_po_file(f, skill)
            # Modify repo

            if 'locale' in os.listdir(work.tmp_path):
                path = join('locale', lang)
                if exists(join(work.tmp_path, path)):
                    work.rm(join(path, '*'))  # Remove all files
                os.makedirs(join(work.tmp_path, path))
                # insert new translations
                insert_translation(join(work.tmp_path, path), translation)
                work.add(join(path, '*'))  # add the new files
            else:
                # handle dialog directory
                if exists(join(work.tmp_path, 'dialog')):
                    path = join('dialog', lang)
                    if exists(join(work.tmp_path, path)):
                        work.rm(join(path, '*'))  # Remove all files
                    os.makedirs(join(work.tmp_path, path))
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.dialog')})
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.list')})
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.value')})
                    work.add(join(path, '*'))  # add the new files
                # handle vocab directory
                if exists(join(work.tmp_path, 'vocab')):
                    path = join('vocab', lang)
                    if exists(join(work.tmp_path, path)):
                        work.rm(join(path, '*'))  # Remove all files
                    os.makedirs(join(work.tmp_path, path))
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.intent')})
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.voc')})
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.entity')})
                    work.add(join(path, '*'))  # add the new files
                # Handle regex dir
                path = join('regex', lang)
                if exists(join(work.tmp_path, 'regex')):
                    if exists(join(work.tmp_path,path)):
                        work.rm(join(path, '*'))  # Remove all files
                    os.makedirs(join(work.tmp_path, path))
                    insert_translation(join(work.tmp_path, path),
                        {k: translation[k] for k in translation if
                            k.endswith('.rx')})
                    work.add(join(path, '*'))  # add the new files

        if work.diff('--cached') != '':
            print("\tCreating PR for {}".format(skill))
            # Commit
            work.commit('-m', 'Update translations')
            # Push branch to fork
            work.push('-f', 'work', branch)
            # Open PR
            create_or_edit_pr(branch, upstream, langs)
        else:
            print('\tNo changes for {}, skipping PR'.format(skill))
        work.tmp_remove()

if __name__ == '__main__':
    main()
