#!/usr/bin/python3
import copy
import os
import sys
import yaml
import json
from datetime import datetime

RECIPE_DIR = "recettes"


def export_complete_cookbook():
    """
    create a document containing quotes of the recipes contained in the cookbook.
    """

    recipes_list = lambda: "{}".format('\n'.join(files_wikilinks(sorted(CookBookRepository.RECIPES_NAMES_LIST))))

    complete_cookbook = """# Livre de recettes
    
    {}""".replace("    ", "")

    files_wikilinks = lambda files_list: \
        map(lambda file: '![[{}]]'.format(file.split('/')[-1].replace('.md\n', '')), files_list)

    with open("livre de recettes.md", 'w') as f:
        f.write(complete_cookbook.format(recipes_list()))


class CookBookRepository:
    RECIPES_NAMES_LIST = list(map(
        lambda x: x.split('/')[-1].replace('\n', '').replace('.md', ''),
        os.popen(f'find {RECIPE_DIR} -name "*.md"').readlines()
    ))

    RECIPES_TAG = "recipes"
    COOKED_DATES_TAG = "cooked dates"

    RECIPE_METADATA_TEMPLATE = {
        COOKED_DATES_TAG: []
    }

    @staticmethod
    def get_cookbook_metadata():
        with open('cookbook_metadata.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def set_cookbook_metadata(cookbook_metadata):
        with open('cookbook_metadata.json', 'w') as f:
            json.dump(cookbook_metadata, f, indent=4)  # you can add indent=4 when debugging to format the json file

    @staticmethod
    def get_recipes_cooked_dates():
        recipes_cooked_dates = {}
        for key, value in CookBookRepository.get_cookbook_metadata().items():
            recipes_cooked_dates[key] = value[CookBookRepository.COOKED_DATES_TAG]
        return recipes_cooked_dates

    @staticmethod
    def get_recipe_cooked_dates(recipe_name):
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        if recipe_name not in cookbook_metadata.keys():
            return []
        return cookbook_metadata[recipe_name][CookBookRepository.COOKED_DATES_TAG]

    @staticmethod
    def _get_metadata_from_md(path):
        """
        :param path: the path to the markdown file containing the metadata
        :return: an empty string if there is no metadata in the file. Otherwise, return a dictionary of the metadata
        """
        lines = ""
        metadata_marker = "---\n"
        with open(path, 'r') as f:
            line = f.readline()
            if line != metadata_marker:  # check if there is metadata in the file
                return ''
            while True:
                line = f.readline()
                if line == metadata_marker:
                    return yaml.safe_load(lines)
                lines += line

    @staticmethod
    def get_recipes_metadata():
        """
        :return: the metadata of all the files in a dictionary
        """
        CookBookRepository.update_cookbook_metadata()
        files_metadata = {}
        for recipe_name in CookBookRepository.get_cookbook_metadata().keys():
            file_metadata = CookBookRepository._get_metadata_from_md(f"recettes/{recipe_name}.md")
            if file_metadata != '':
                files_metadata[recipe_name] = file_metadata
        return files_metadata

    @staticmethod
    def get_recipes_times_cooked():
        recipes_cooked_dates = {}
        for key, value in CookBookRepository.get_cookbook_metadata().items():
            recipes_cooked_dates[key] = len(value[CookBookRepository.COOKED_DATES_TAG])
        return recipes_cooked_dates

    @staticmethod
    def add_recipe_cooked_date(recipe_name):
        CookBookRepository.update_cookbook_metadata()
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        if recipe_name not in cookbook_metadata.keys():
            cookbook_metadata[recipe_name] = CookBookRepository.RECIPE_METADATA_TEMPLATE
        cookbook_metadata[recipe_name][CookBookRepository.COOKED_DATES_TAG].append(
            datetime.now().isoformat())
        CookBookRepository.set_cookbook_metadata(cookbook_metadata)

    @staticmethod
    def update_cookbook_metadata():
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        for recipe in CookBookRepository.RECIPES_NAMES_LIST:
            if recipe not in cookbook_metadata.keys():
                cookbook_metadata[recipe] = CookBookRepository.RECIPE_METADATA_TEMPLATE
        CookBookRepository.set_cookbook_metadata(cookbook_metadata)


for arg in sys.argv:
    if arg == "export":
        export_complete_cookbook()
    if arg == "update":
        CookBookRepository.update_cookbook_metadata()
