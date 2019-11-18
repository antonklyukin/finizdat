#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import odtparser.odtparser as odt
import os
import json
import pickle

# Acronym of journal name (Example: 'FC')
journal_acronym = "RE"

# Получаем полный путь до файла модуля
module_filepath = os.path.realpath(__file__)

# Получаем полный путь до директории модуля
module_dirpath = os.path.join(os.path.dirname(module_filepath), "test_odt")

def write_issue_info_to_json(f, issue_data):
    with open(f"{journal_acronym}.json", "a+", encoding="utf-8") as write_file:
        json.dump(issue_data, write_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":

    dir_gen = os.walk(module_dirpath)

    file_list = []

    # Append all files in 'test_odt' folder to file_list

    for element in dir_gen:
        if element[0] == module_dirpath:
            file_list = element[2]
        break

    # Select files with interested filenames only (containing journal name
    # acronym)
    file_list = [f for f in file_list if journal_acronym in f]

    # all_journals_info_list = list(odt_info_generator(sorted(file_list)))

    f = 'RE-2019-01.odt'

    print(file_list)

    if not os.path.isfile(f'{journal_acronym}_issues_dump.pkl'):
        print(f'Serializing {f} issue file name')
        print("Serializing empty issues_list")

        print(f'Getting info from {f}')
        issue_info = get_issue_info(f)


    

    for issue_file in file_list:
        if not os.path.isfile(f'{journal_acronym}_issues_dump.pkl'):
            try:
                dump_current_state(issue_file, issues_struct)
            except():
                pass
            finally:
                pass
        else:
            load_state()


def load_module_data():
    pass


def dump_module_data():
    pass


def get_issue_info(issue_filename):
    print("Parsing ", f_name)
    issue_info = {}
    odt_parser = odt.OdtParser(os.path.join(module_dirpath, f_name))

    citation_info_list = odt_parser.get_info_list_from_citation_paragraph_ru()
    # print('Цитирований: ', len(citation_info_list))

    article_rubrics_list_ru = [
    name
    for i, name in enumerate(odt_parser.get_article_rubrics_list())
    if i % 2 == 0
    ]
    article_info_list = odt_parser.get_article_info_ru()
    article_abstracts_list = odt_parser.get_article_abstracts_ru_html()
    article_texts_list = odt_parser.get_article_text_ru_list()
    article_ref_list = odt_parser.get_references_ru_list()
    # print('Списков литературы: ', len(article_ref_list))

    through_issue_number = odt_parser.get_article_through_issue_number()

    issue_info["journal_name"] = odt_parser.get_journal_name_ru()
    issue_info["issue_year"] = citation_info_list[0]["publication_year"]
    issue_info["issue_volume"] = citation_info_list[0]["issue_volume"]
    issue_info["issue_number_in_year"] = citation_info_list[0][
    "issue_number_in_year"
    ]
    issue_info["through_issue_number"] = through_issue_number

    issue_info["articles"] = []

    article_list = []

    for i in range(len(citation_info_list)):
        article_list.append(
            {
                "name": citation_info_list[i]["article_name_ru"],
                "short_author_names": citation_info_list[i][
                    "authors_shortnames_ru"
                ],
                "pages": citation_info_list[i]["pages_range"],
                "rubric": article_rubrics_list_ru[i],
                "received_date": article_info_list[i]["received_date"],
                "revised_date": article_info_list[i]["revised_date"],
                "accepted_date": article_info_list[i]["accepted_date"],
                "available_date": article_info_list[i]["available_date"],
                "UDK": article_info_list[i]["UDK"],
                "JEL": article_info_list[i]["JEL"],
                "keywords_ru": article_info_list[i]["keywords_ru"],
                "abstract_html": article_abstracts_list[i],
                "full_text": article_texts_list[i],
                "references_list_html": article_ref_list[i],
            }
        )

        issue_info["articles"] = article_list

    return issue_info

issue_filename, issues_data_list = load_module_data()

