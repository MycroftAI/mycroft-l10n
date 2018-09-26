# Pootle export approach

## Objective
The objective of this file is to outline in pseudocode, an approach for exporting phrases from Pootle into GitHub, prior to implementation. Discussion and review at this stage is likely to make implementation in code faster and more efficient, and can be assigned to another developer if they are more proficient.

## Outline of key steps

1. Export `.po` files from Pootle

There are a couple of possible approaches here;

* export using the built in zip exporter by calling a GET from
`https://translate-test.mycroft.ai/export/?path=/LANGUAGE-CODE/PROJECT-NAME/`
ie
`https://translate-test.mycroft.ai/export/?path=/id/mycroft-skills/`

This serves a `.zip` file, containing the following directory structure (example):

```$ ls -las -R id-mycroft-skills/
id-mycroft-skills/:
total 12
4 drwx------ 3 kathyreid kathyreid 4096 Sep 26 21:34 .
4 drwxrwxr-x 3 kathyreid kathyreid 4096 Sep 26 21:34 ..
4 drwx------ 3 kathyreid kathyreid 4096 Sep 26 21:34 id

id-mycroft-skills/id:
total 12
4 drwx------ 3 kathyreid kathyreid 4096 Sep 26 21:34 .
4 drwx------ 3 kathyreid kathyreid 4096 Sep 26 21:34 ..
4 drwx------ 2 kathyreid kathyreid 4096 Sep 26 21:34 mycroft-skills

id-mycroft-skills/id/mycroft-skills:
total 340
 4 drwx------ 2 kathyreid kathyreid  4096 Sep 26 21:34 .
 4 drwx------ 3 kathyreid kathyreid  4096 Sep 26 21:34 ..
 4 -rw-rw-r-- 1 kathyreid kathyreid  1387 Sep 26 11:21 00__skill_template-id.po
12 -rw-rw-r-- 1 kathyreid kathyreid 11723 Sep 26 11:21 btotharye-home-assistant-id.po
12 -rw-rw-r-- 1 kathyreid kathyreid 10683 Sep 26 11:21 carstena-the-cows-lists-id.po
 4 -rw-rw-r-- 1 kathyreid kathyreid  1166 Sep 26 11:21 chatbot-id.po
 (list of skill files truncated)
```

Here is an example of the contents of a Skill `.po` file (`mycroft-mark-1.po`)

```msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2018-09-26 11:21+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: id\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"X-Generator: Translate Toolkit 2.2.5\n"
"X-Pootle-Path: /id/mycroft-skills/mycroft-mark-1-id.po\n"
"X-Pootle-Revision: 1036\n"

#: tags/mycroft-mark-1/auto.noon.dialog:1
msgid "It's seems to be midday, I will adjust the brightness."
msgstr ""

#: tags/mycroft-mark-1/auto.sunrise.dialog:1
msgid "Okay, The sun is coming out, I will adjust the brightness"
msgstr ""

#: tags/mycroft-mark-1/auto.sunrise.dialog:2
msgid "Okay, the sun is out, setting the brightness level"
msgstr ""

#: tags/mycroft-mark-1/auto.sunset.dialog:1
msgid "Okay, It's getting dark, I will adjust the brightness accordingly."
msgstr ""

#: tags/mycroft-mark-1/brightness.auto.intent:1
msgid "set brightness to auto"
msgstr ""

#: tags/mycroft-mark-1/brightness.auto.intent:2
msgid "auto brightness"
msgstr ""
```

_NOTE_ I could not find a way to expore the whole set of languages in a single `.zip` file.

* The second option I can see is to do an export from the database directly using SQL into the Postgres database. I had a quick look at the table structure in the `pootledb`  but it is quite complex. I don't think this is a viable option.

* Another _possible_ option here is to write a "Mycroft Plugin" for Pootle, using the [Pootle plugin framework](http://docs.translatehouse.org/projects/pootle/en/stable-2.8.x/developers/plugins.html). My assessment though is that this framework is very immature at this stage and is likely to be problematic. Pootle appeared to have an API in the 2.5 release, but there is no mention of an API in the 2.8.x release.

**Therefore I think the export should use a GET request to download the `.zip` file.**

1. _NOTE_ for this step, I don't whether it would be best to do "Skills" on the outer loop and "Languages" on the inner loop, or the other way around.

* Set up a GitHub API v3 connection - https://developer.github.com/v3/?
* For each **language**, for each **Mycroft-controlled Skill** (because we won't have GitHub API access to Skills submitted by other Skill Authors)
  - BEGIN for each language loop
  - Do a https GET request to get the zip file for that language
  - Unpack that zip file to the Skill level
    - BEGIN for each skill loop
    - For each line of the `.po` file for a Skill,
      - Check to see whether there is a `locale/LANGUAGE` directory in the repo for the Skill, and if not create that directory
      - If the string in the `.po` file IS NOT NULL, DO:
      - Check to see whether there is an existing string for the vocab or dialog in the `.po` file, and if not create it
      - Both of these actions probably need to use some sort of raise-a-PR API call - https://developer.github.com/v3/pulls/#create-a-pull-request - followed by some form of automated merge API call - https://developer.github.com/v3/pulls/#merge-a-pull-request-merge-button

1. Unknown step - how do we handle this for repositories that Mycroft AI does not control - we could _probably_ raise the PR but just not automatically merge it?

1.  Ensure that the script exited successfully, or report an exception
