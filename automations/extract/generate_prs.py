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


"""
Script generating translation Pull Requests to github repos.

See "generate_prs.py --help" for options.
"""

import argparse
import os
import json
from os.path import join, exists
from requests import get

import polib
from github_actions import get_work_repos, create_work_dir, create_or_edit_pr

DEFAULT_BRANCH = '20.02'
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


def parse_po_file(path, skill, occurrences):
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
    'es-es': 'es',
    'es-lm': 'es_LM',
    'ro-ro': 'ro',
    'hu-hu': 'hu',
    'nl-nl': 'nl',
    'pt-br': 'pt_BR',
    'it-it': 'it',
    'da-dk': 'da',
    'tr-tr': 'tr',
    'el-gr': 'el'
}


def po_file_path(skill, lang):
    return join(pootle_langs[lang] + '-mycroft-skills',
                pootle_langs[lang],
                'mycroft-skills',
                skill + '-' + pootle_langs[lang] + '.po')


def read_occurrences_file(path):
    """Read the occurence json file and return dictionary."""
    with open(path) as f:
        occurrences = json.load(f)
    return occurrences


def main(dry_run, occurrences_file, mycroft_only):
    """Main script.

    Arguments:
        dry_run (bool): Perform all the actions but do not create pull requests
        occurence_file (str): path to occurence file
        mycroft_only (bool): only perform actions on mycroft skills.
    """
    skill_repos = get_skill_repos()

    occurrences = read_occurrences_file(occurrences_file)

    for skill in skill_repos:
        # Get repo information
        skill_url = skill_repos[skill]
        if mycroft_only and 'mycroftai/' not in skill_url.lower():
            print('Skipping {}'.format(skill_url))
            continue
        print('Running {}'.format(skill_url))
        # Get git repo and github connections
        fork, upstream = get_work_repos(skill_url)
        work_dir = create_work_dir(upstream, fork)  # local clone
        # Checkout new branch
        branch = 'translations'
        work_dir.checkout('-b', branch)

        # Update language files
        langs = update_skill(skill, work_dir, occurrences)

        # If a change has been made commit and make a PR
        if work_dir.diff('--cached') != '':
            print("\n\tCreating PR for {}\n\n".format(skill))
            if not dry_run:
                # Commit
                work_dir.commit('-m', 'Update translations')
                # Push branch to fork
                work_dir.push('-f', 'work', branch)
                # Open PR
                create_or_edit_pr(branch, upstream, langs)
        else:
            print('\n\tNo changes for {}, skipping PR\n\n'.format(skill))
        work_dir.tmp_remove()


def map_translations(translation, filetype):
    return {k: translation[k] for k in translation if k.endswith(filetype)}


def update_skill(skill, work, occurrences):
    """Update language specific files for a skill.

    Arguments:
        skill: skill to operate on
        work: work repo
        occurences (dict): occurence dictiontionary, mapping strings to files
    """
    langs = []
    for lang in pootle_langs:
        # Build po-file path
        f = po_file_path(skill, lang)

        if not (exists(f) and is_translated(f)):
            print('Skipping {}'.format(f))
            continue

        langs.append(lang)
        print('Processing {}'.format(f))
        translation = parse_po_file(f, skill, occurrences)

        # Modify skill
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
                                   map_translations(translation, '.dialog'))
                insert_translation(join(work.tmp_path, path),
                                   map_translations(translation, '.list'))
                insert_translation(join(work.tmp_path, path),
                                   map_translations(translation, '.value'))
                work.add(join(path, '*'))  # add the new files
            # handle vocab directory
            if exists(join(work.tmp_path, 'vocab')):
                path = join('vocab', lang)
                if exists(join(work.tmp_path, path)):
                    work.rm(join(path, '*'))  # Remove all files
                os.makedirs(join(work.tmp_path, path))
                insert_translation(join(work.tmp_path, path),
                                   map_translations(translation, '.intent'))
                insert_translation(join(work.tmp_path, path),
                                   map_translations(translation, '.voc'))
                insert_translation(join(work.tmp_path, path),
                                   map_translations(translation, '.entity'))
                work.add(join(path, '*'))  # add the new files
            # Handle regex dir
            path = join('regex', lang)
            if exists(join(work.tmp_path, 'regex')):
                if exists(join(work.tmp_path, path)):
                    work.rm(join(path, '*'))  # Remove all files
                os.makedirs(join(work.tmp_path, path))
                insert_translation(join(work.tmp_path, path),
                                   map_translations(translation, '.rx'))
                work.add(join(path, '*'))  # add the new files

    return langs  # Return checked languages


def create_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Don\'t send any PR to the skills')
    parser.add_argument('-o', '--occurence-file', default='./occurrences.json',
                        help=('path to occurrences.json, '
                              '(default "./occurrences.json")'))
    parser.add_argument('-m', '--mycroft-only', action='store_true',
                        help='Only operate on mycroft skills.')
    return parser


if __name__ == '__main__':
    parser = create_argparser()
    args = parser.parse_args()
    main(args.dry_run, args.occurence_file, args.mycroft_only)
