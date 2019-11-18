#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import odtparser.odtparser as odt
import os


if __name__ == '__main__':
    # Получаем полный путь до файла модуля
    module_filepath = os.path.realpath(__file__)

    # Получаем полный путь до директории модуля
    module_dirpath = os.path.dirname(module_filepath)

    # Добавляем директорию и файл с тестовыми верстками
    test_odt_filepath = os.path.join(module_dirpath, 'test_odt', 'ea.odt')
    odt_parser = odt.OdtParser(test_odt_filepath)

    #Testing functions


    # journal_name = odt_parser.get_journal_name()
    # print("Название журнала:\n", journal_name)

    # through_issue_number = odt_parser.get_through_issue_number()
    # print("Сквозной номер выпуска журнала:\n", through_issue_number)

    # issue_pub_dates = odt_parser.get_issue_pub_dates_list()
    # print("Даты выпуска журнала:\n", issue_pub_dates)  

    # number_of_articles = odt_parser.get_number_of_articles_in_issue()
    # print("Количество статей:\n", number_of_articles)

    # article_rubrics = odt_parser.get_article_rubrics_list()
    # print("Список названий рубрик статей:\n", article_rubrics)
    # print("Количество статей исходя из рубрик: ", len(article_rubrics))

    # article_abstracts = odt_parser.get_article_abstracts_list()
    # print("Список аннотаций к статьям:\n", article_abstracts)
    # print("Количество статей исходя из аннотаций: ", len(article_abstracts))

    citation_paragraphs = odt_parser.get_citation_paragraphs_list()
    print("Список разделов цитирования к статьям:\n", citation_paragraphs)
    print("Количество статей исходя из разделов цитирования: ", len(citation_paragraphs))

    # article_full_texts = odt_parser.get_article_full_texts_list()
    # print("Список полных текстов статей:\n", article_full_texts[0])
    # print("Количество статей исходя из количества полных текстов: ", len(article_full_texts))

    # article_full_author_names = odt_parser.get_full_author_names_list()
    # print("Список полных имен авторов статей:\n", article_full_author_names)
    # print("Количество статей исходя из количества полных имен статей: ", len(article_full_author_names))

    # article_affiliations = odt_parser.get_affiliation_info_list()
    # print("Список аффилиаций авторов статей:\n", article_affiliations)
    # print("Количество статей исходя из количества аффилиаций авторов статей: ", len(article_affiliations))

    # article_info_list = odt_parser.get_article_info_list()
    # print("Список выходной информации статей:\n", article_info_list)
    # print("Количество статей исходя из количества выходной информации статей: ", len(article_info_list))

    # article_references_list = odt_parser.get_article_references_list()
    # print("Список литературы статей:\n", article_references_list)
    # print("Количество статей исходя из количества списков литературы статей: ", len(article_references_list))


