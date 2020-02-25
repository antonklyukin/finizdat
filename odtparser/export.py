#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exports data from one file in param. Example: python -m odtparser.export ./odtparser/test_odt/ia.odt 
"""

from odtparser.journals_info import MONTHS_EN_LIST, RUBRICS_DICT, JOURNAL_ABBRVS
import odtparser.odtparser as odt
import os
import sys
import re
import json
import pickle

def get_ru_rubric_from_en_rubric(en_rubric):
    ru_rubric = ""
    for k, v in RUBRICS_DICT.items():
        if v == en_rubric:
            ru_rubric = k
    return ru_rubric

def get_ru_date_from_en_date(en_date):

    ru_fulldate = ""
    en_date_regex = re.compile(r"(\d+)\s+([a-zA-Z]+)\s+(\d+)")

    date_list = en_date_regex.fullmatch(en_date)

    if date_list != None:
        ru_date = date_list.group(1).rjust(2, "0")
        ru_month = int(MONTHS_EN_LIST.index(str.lower(date_list.group(2)))) + 1
        ru_month_str = str(ru_month).rjust(2, "0")
        ru_year = date_list.group(3)
        ru_fulldate = f"{ru_date}.{ru_month_str}.{ru_year}"

    return ru_fulldate

def get_full_path_to_file(path_to_file):
    """
    Returns an odt file full path
    """

    cur_dir = os.getcwd()
    full_path_to_file = ""

    # Relative path
    if re.fullmatch(r"^\.\/.*", path_to_file) or (
            re.fullmatch(r"^[^\/\.].*\/.*", path_to_file)):
        path_to_file = re.sub(r"^\.\/", "", path_to_file)
        full_path_to_file = os.path.join(cur_dir, path_to_file)

    # Local file
    elif re.fullmatch(r"^[^\/\.].*", path_to_file):
        full_path_to_file = os.path.join(cur_dir, path_to_file)

    # Absolute path
    else:
        full_path_to_file = path_to_file

    return full_path_to_file


def get_issue_data(path_to_file):

    issue_data = {"issue_info": {}, "articles_info": []}

    full_path_to_file = get_full_path_to_file(path_to_file)

    odt_file = odt.OdtParser(full_path_to_file)

    journal_name = odt_file.get_journal_name()
    issue_pub_dates = odt_file.get_issue_pub_dates_dict()
    through_issue_number = odt_file.get_through_issue_number()
    number_of_articles = odt_file.get_number_of_articles_in_issue()
    article_rubrics_list = odt_file.get_article_rubrics_list()
    article_citiation_info_list = odt_file.get_citation_paragraphs_list()
    article_abstracts_list = odt_file.get_article_abstracts_list()
    article_full_texts_list = odt_file.get_article_full_texts_list()
    article_full_author_names_list = odt_file.get_full_author_names_list()
    article_affiliation_info_list = odt_file.get_affiliation_info_list()
    article_info_list = odt_file.get_article_info_list()
    article_references_list = odt_file.get_article_references_list()

    # TEST
    # print(article_info_list)
    # TEST


    # --- Gathering the information about journal issue ---

    issue_dict = {
        "journal_name_ru": journal_name["journal_name_ru"],
        "journal_name_en": journal_name["journal_name_en"],
        "through_issue_number": through_issue_number,
        "volume_ru": issue_pub_dates["ru"]["volume_ru"],
        "volume_en": issue_pub_dates["en"]["volume_en"],
        "issue_number_ru": issue_pub_dates["ru"]["issue_ru"],
        "issue_number_en": issue_pub_dates["en"]["issue_en"],
        "issue_month_ru": issue_pub_dates["ru"]["month_ru"],
        "issue_month_en": issue_pub_dates["en"]["month_en"],
        "year_ru": issue_pub_dates["ru"]["year_ru"],
        "year_en": issue_pub_dates["en"]["year_en"]
    }

    # --- Gathering the information about articles ---
    for i in range(number_of_articles):

        article = {}

        if article_citiation_info_list[i]['article_lang'] == "ru":

            # Авторский блок

            authors_list = []

            authors_short_names_ru_list = str.split(
                article_citiation_info_list[i]["ru"]["authors_ru"], ",")
            authors_short_names_en_list = str.split(
                article_citiation_info_list[i]["en"]["authors_en"], ",")

            authors_full_names_ru_list = article_full_author_names_list[i]["ru"]
            authors_full_names_en_list = article_full_author_names_list[i]["en"]
            authors_affiliation_ru_list = article_affiliation_info_list[i]["ru"]
            authors_affiliation_en_list = article_affiliation_info_list[i]["en"]

            for j in range(len(authors_short_names_ru_list)):

                author_orcid_ru = authors_affiliation_ru_list[j]["orcid"]
                author_orcid_en = authors_affiliation_en_list[j]["orcid"]
                author_spin = authors_affiliation_ru_list[j]["spin"]

                if re.search("отсутствует", author_orcid_ru):
                    author_orcid_ru = None

                if re.search("available", author_orcid_en):
                    author_orcid_en = None

                if re.search("отсутствует", author_spin):
                    author_spin = None
                else:
                    author_spin = re.sub(
                        r"SPIN-код:\s+([\-\d]+)", r"\1", author_spin)

                authors_dict = {
                    "author_short_name_ru": str.strip(authors_short_names_ru_list[j]),
                    "author_short_name_en": str.strip(authors_short_names_en_list[j]),
                    "author_full_name_ru": str.strip(authors_full_names_ru_list[j]),
                    "author_full_name_en": str.strip(authors_full_names_en_list[j]),
                    "author_workplace_ru": str.strip(authors_affiliation_ru_list[j]["workplace"]),
                    "author_workplace_en": str.strip(authors_affiliation_en_list[j]["workplace"]),
                    "author_email_ru": str.strip(authors_affiliation_ru_list[j]["email"]),
                    "author_email_en": str.strip(authors_affiliation_en_list[j]["email"]),
                    "author_orcid_ru": author_orcid_ru,
                    "author_orcid_en": author_orcid_en,
                    "author_spin": author_spin
                }

                authors_list.append(authors_dict)


            # Авторский блок - КОНЕЦ

            article_reg_number = None

            if article_info_list[i]["ru"]["reg_number"] != "":
                article_reg_number = re.sub(
                r"^(.*?)\d", r"", article_info_list[i]["ru"]["reg_number"])

            article = {
                "article_lang": "ru",
                "article_name_ru": article_citiation_info_list[i]["ru"]["article_name_ru"],
                "article_name_en": article_citiation_info_list[i]["en"]["article_name_en"],
                "article_rubric_ru": article_rubrics_list[i]["ru"],
                "article_rubric_en": article_rubrics_list[i]["en"],
                "article_astract_ru": article_abstracts_list[i]["ru"],
                "article_astract_en": article_abstracts_list[i]["en"],
                "article_date_received_ru": article_info_list[i]["ru"]["received_date_ru"],
                "article_date_received_en": article_info_list[i]["en"]["received_date_en"],
                "article_date_revised_ru": article_info_list[i]["ru"]["revised_date_ru"],
                "article_date_revised_en": article_info_list[i]["en"]["revised_date_en"],
                "article_date_accepted_ru": article_info_list[i]["ru"]["accepted_date_ru"],
                "article_date_accepted_en": article_info_list[i]["en"]["accepted_date_en"],
                "article_date_available_ru": article_info_list[i]["ru"]["available_date_ru"],
                "article_date_available_en": article_info_list[i]["en"]["available_date_en"],
                "article_reg_number": article_reg_number,
                "article_udk": article_info_list[i]["ru"]["UDK"],
                "article_jel_ru": article_info_list[i]["ru"]["JEL"],
                "article_jel_en": article_info_list[i]["en"]["JEL"],
                "article_keywords_ru": article_info_list[i]["ru"]["keywords_ru"],
                "article_keywords_en": article_info_list[i]["en"]["keywords_en"],
                "article_pages_range_ru": article_citiation_info_list[i]["ru"]["pages_range"],
                "article_pages_range_en": article_citiation_info_list[i]["en"]["pages_range"],

                "article_authors": authors_list,

                "article_full_text": article_full_texts_list[i]["ru"],
                "article_references_ru_list": article_references_list[i]["ru"],
                "article_references_en_list": article_references_list[i]["en"]
            }

        elif article_citiation_info_list[i]['article_lang'] == "en":

            authors_list = []

            authors_short_names_ru_list = str.split(
                article_citiation_info_list[i]["en"]["authors_en"], ",")
            authors_short_names_en_list = str.split(
                article_citiation_info_list[i]["en"]["authors_en"], ",")
            authors_full_names_ru_list = article_full_author_names_list[i]["en"]
            authors_full_names_en_list = article_full_author_names_list[i]["en"]
            authors_affiliation_ru_list = article_affiliation_info_list[i]["en"]
            authors_affiliation_en_list = article_affiliation_info_list[i]["en"]

            for j, author_short_name_en in enumerate(authors_short_names_en_list):

                author_orcid_ru = authors_affiliation_en_list[j]["orcid"]
                author_orcid_en = authors_affiliation_en_list[j]["orcid"]
                author_spin = None

                if re.search("отсутствует", author_orcid_ru):
                    author_orcid_ru = None

                if re.search("available", author_orcid_en):
                    author_orcid_en = None

                author_dict = {
                    "author_short_name_ru": str.strip(author_short_name_en),
                    "author_short_name_en": str.strip(authors_short_names_en_list[j]),
                    "author_full_name_ru": str.strip(authors_full_names_en_list[j]),
                    "author_full_name_en": str.strip(authors_full_names_en_list[j]),
                    "author_workplace_ru": str.strip(authors_affiliation_en_list[j]["workplace"]),
                    "author_workplace_en": str.strip(authors_affiliation_en_list[j]["workplace"]),
                    "author_email_ru": str.strip(authors_affiliation_en_list[j]["email"]),
                    "author_email_en": str.strip(authors_affiliation_en_list[j]["email"]),
                    "author_orcid_ru": author_orcid_ru,
                    "author_orcid_en": author_orcid_en,
                    "author_spin": author_spin
                }

                authors_list.append(author_dict)

            article_reg_number = None

            if article_info_list[i]["en"]["reg_number"] != "":
                article_reg_number = re.sub(
                r"^(.*?)\d", r"", article_info_list[i]["en"]["reg_number"])

            article_date_received_ru =  get_ru_date_from_en_date(article_info_list[i]["en"]["received_date_en"])
            article_date_revised_ru =  get_ru_date_from_en_date(article_info_list[i]["en"]["revised_date_en"])
            article_date_accepted_ru =  get_ru_date_from_en_date(article_info_list[i]["en"]["accepted_date_en"])
            article_date_available_ru =  get_ru_date_from_en_date(article_info_list[i]["en"]["available_date_en"])

            article = {
                "article_lang": "en",
                "article_name_ru": article_citiation_info_list[i]["en"]["article_name_en"],
                "article_name_en": article_citiation_info_list[i]["en"]["article_name_en"],
                "article_rubric_ru": get_ru_rubric_from_en_rubric(article_rubrics_list[i]["en"]),
                "article_rubric_en": article_rubrics_list[i]["en"],
                "article_astract_ru": article_abstracts_list[i]["en"],
                "article_astract_en": article_abstracts_list[i]["en"],
                "article_date_received_ru": article_date_received_ru,
                "article_date_received_en": article_info_list[i]["en"]["received_date_en"],
                "article_date_revised_ru": article_date_revised_ru,
                "article_date_revised_en": article_info_list[i]["en"]["revised_date_en"],
                "article_date_accepted_ru": article_date_accepted_ru,
                "article_date_accepted_en": article_info_list[i]["en"]["accepted_date_en"],
                "article_date_available_ru": article_date_available_ru,
                "article_date_available_en": article_info_list[i]["en"]["available_date_en"],
                # "article_reg_number": article_reg_number,
                # "article_udk": None,
                "article_jel_ru": article_info_list[i]["en"]["JEL"],
                "article_jel_en": article_info_list[i]["en"]["JEL"],
                "article_keywords_ru": article_info_list[i]["en"]["keywords_en"],
                "article_keywords_en": article_info_list[i]["en"]["keywords_en"],

                "article_authors": authors_list,

                "article_full_text": article_full_texts_list[i]["en"],
                "article_references_ru_list": article_references_list[i]["en"],
                "article_references_en_list": article_references_list[i]["en"]
            }


        issue_data["issue_info"] = issue_dict
        issue_data["articles_info"].append(article)

    return issue_data

def write_issue_info_to_json(issue_data, journal_acronym):
    with open(f"{journal_acronym}.json", "a+", encoding="utf-8") as write_file:
        json.dump(issue_data, write_file, indent=4, ensure_ascii=False)


json_data = []

if len(sys.argv) > 1:
    list_of_files = sys.argv[1:]

    for odt_file in list_of_files:
        print(f"Получаем данные из файла {odt_file}")
        issue_data = get_issue_data(odt_file)

        journal_name = issue_data["issue_info"]["journal_name_ru"]

        journal_abbr = JOURNAL_ABBRVS[journal_name]
        issue_year = issue_data["issue_info"]["year_ru"]
        issue_number = issue_data["issue_info"]["issue_number_ru"]

        journal_acronym = f"{journal_abbr}-{issue_year}-{issue_number}"
        write_issue_info_to_json(issue_data, journal_acronym)


else:
    print("Searching all odt files in directory...")

# write_json_to_file(json_data)
