#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import sys
from typing import Type

import bs4
import langdetect
from transliterate import translit
from collections import OrderedDict

from odtparser.odtfile import OdtFile
from odtparser.journals_info import JOURNAL_NAMES_RU_LIST,\
    JOURNAL_NAMES_EN_LIST, MONTHS_RU_LIST, MONTHS_EN_LIST


def clear_text(text: str) -> str:
    """
    Clears text data
    """

    stripped_text = text.strip()
    cleared_text = re.sub(r"\s+", " ", stripped_text)
    cleared_text = re.sub(r"\xa0", " ", cleared_text)
    cleared_text = re.sub(r"\s\.", ".", cleared_text)
    cleared_text = re.sub(r"<text:line-break/>", " ", cleared_text)
    cleared_text = re.sub(r"·", "X", cleared_text)
    cleared_text = re.sub(r"(№)(\S)", r"\1 \2", cleared_text)
    cleared_text = re.sub(r"\s,", ",", cleared_text)

    return cleared_text


def correct_tree(odt_content: bs4.BeautifulSoup, style_name: str, tag_name: str):
    """
    Normalizes odt content adding text:style-name element.
    """

    nodes_list = odt_content.find_all(
        "style:style", {"style:parent-style-name": style_name}
    )

    list_of_node_number_styles = []

    for node in nodes_list:
        if node["style:name"] not in list_of_node_number_styles:
            list_of_node_number_styles.append(node["style:name"])

    for number_style in list_of_node_number_styles:
        nodes_list = odt_content.find_all(
            tag_name, {"text:style-name": number_style})

        for node in nodes_list:
            element = odt_content.find(
                tag_name, {"text:style-name": number_style})
            element["text:style-name"] = style_name


def clear_ref_element(element, content_data):
    """
    Clears reference element from odt tags and adds HTML tags 
    """

    el_string = "<p>"

    for el in element:
        if isinstance(el, bs4.element.Tag):

            if el.name == "soft-page-break":
                el_string = el_string + " "
                continue

            if el.name in ("bookmark", "s"):
                continue

            el_pattern = re.compile(r"^T[\d]+")

            if el_pattern.search(el["text:style-name"]):
                style_name = el["text:style-name"]

                style_element = content_data.find(
                    "style:style", {"style:name": style_name}
                )

                font_type = style_element.find("style:text-properties")

                if font_type.get("fo:font-style") == "italic":
                    el_string = el_string + "<i>" + el.text + "</i>"
                else:
                    el_string += el.text

            else:
                el_string += el.text

        if isinstance(el, bs4.element.NavigableString):
            el_string = el_string + (el.string)

    el_string = el_string + "</p>"

    # Join doubled, trippled i in getted string and delete spaces

    el_string = el_string.replace("</i><i>", "")
    el_string = re.sub(r"</i>\s+<i>", " ", el_string)
    el_string = re.sub(r"<i>\s+</i>", " ", el_string)
    el_string = re.sub(r"\s+", " ", el_string)
    el_string = re.sub(r"<p>\s+(.+)", r"<p>\1", el_string)

    return el_string


def get_ref_header(ref_node: bs4.BeautifulSoup):
    """
    Gets a node with references list and returns name
    """

    ref_header = ref_node.previous_element

    while ref_header == "":
        ref_header = ref_header.previous_element

    return ref_header


def get_ref_list_html(ref_node, content_data):
    """
    Gets reference node and returns string containing reference list in HTML
    format
    """

    ref_node_str_html = ""
    ref_element = ref_node.find_all("text:p")

    for element in ref_element:
        ref_node_str_html = (
            ref_node_str_html + clear_ref_element(element, content_data) + "\n"
        )

    return ref_node_str_html


def get_info_from_citation_str_ru(citation_ru_str: str) -> dict:
    """
    Gets Russian citation string and returns dictionary of article params
    """

    citation_info_ru_dict = {}

    regex_ru_citation = re.compile(
        r"^Для цитирования:\s+(.*?[А-ЯЁ]\.)\s+(.*)\s+\/\/.*\s+–\s+(\d\d\d\d)"
        r"\.\s+–\s+Т\.\s+(\d+)\,\s+№\s+(\d+)\.\s+\–\s+С\.\s+(\d+\s\–\s+\d+)"
    )

    citation_ru_str = translit(citation_ru_str, "ru")

    result = regex_ru_citation.match(citation_ru_str)

    if result is None:
        print(
            "Что-то не так со строкой для цитирования - {0}."
            " Программа аварийно завершена.".format(citation_ru_str)
        )
        sys.exit(1)

    citation_info_ru_dict["authors_ru"] = re.sub(r"\s+", " ", result.group(1))
    citation_info_ru_dict["article_name_ru"] = re.sub(
        r"\s+", " ", result.group(2))
    citation_info_ru_dict["year"] = result.group(3)
    citation_info_ru_dict["volume"] = result.group(4)
    citation_info_ru_dict["number_in_year"] = result.group(5)
    citation_info_ru_dict["pages_range"] = re.sub(
        r"^(\d+)[^\d]+(\d+)", r"\1–\2", result.group(6)
    )

    return citation_info_ru_dict


def get_info_from_citation_str_en(citation_en_str: str) -> dict:

    citation_info_en_dict = {}

    regex_en_citation = re.compile(
        r"Please cite this article as:\s+([a-zA-Z\s\.\'\,]+[A-Z][a-z]?\.)"
        r"\s+(.*)\.\s+(Finance and Credit|Economic Analysis: Theory and "
        r"Practice|Regional Economics: Theory and Practice|National "
        r"Interests: Priorities and Security|Financial Analytics: Science "
        r"and Experience|International Accounting|Digest Finance|Accounting "
        r"in Budgetary and Non-Profit Organizations)\,\s+(\d\d\d\d)\,\svol\."
        r"\s+(\d+)\,\s+iss\.\s+(\d+)\,\s+pp\.\s+(.*)\."
    )

    citation_en_str = translit(citation_en_str, "ru", reversed=True)

    result = regex_en_citation.match(citation_en_str)

    if result is None:
        print(
            "Что-то не так со строкой для цитирования - {0}."
            " Программа аварийно завершена.".format(citation_en_str)
        )
        sys.exit(1)

    citation_info_en_dict["authors_en"] = re.sub(r"\s+", " ", result.group(1))
    citation_info_en_dict["article_name_en"] = re.sub(
        r"\s+", " ", result.group(2))
    citation_info_en_dict["year"] = result.group(4)
    citation_info_en_dict["volume"] = result.group(5)
    citation_info_en_dict["number_in_year"] = result.group(6)
    citation_info_en_dict["pages_range"] = re.sub(
        r"^(\d+)[^\d]+(\d+)", r"\1–\2", result.group(7)
    )

    return citation_info_en_dict


def compose_by_article_info_list(raw_info_list):

    composed_by_article_info_list = []

    for i, cit_element in enumerate(raw_info_list):

        # Keeps language of previous citation language
        prev_cit_el_lang = None

        if i > 0:
            prev_cit_el_lang = raw_info_list[i - 1][0]

        if cit_element[0] == "ru":
            next_cit_element = raw_info_list[i + 1]

            article_citation_dict = {
                "article_lang": cit_element[0],
                "ru": cit_element[1],
                "en": next_cit_element[1],
            }

            composed_by_article_info_list.append(article_citation_dict)

        if (cit_element[0] == "en" and i == 0) or (
            cit_element[0] == "en" and prev_cit_el_lang == "en"
        ):

            article_citation_dict = {
                "article_lang": cit_element[0],
                "en": cit_element[1],
            }

            composed_by_article_info_list.append(article_citation_dict)

    return composed_by_article_info_list


def parse_authors_list(authors_string):
    # Функция разбирает строку ФИО авторов в разделе аффилиации и возвращает
    # список с отдельным элементом для каждого ФИО

    authors_list = []

    authors_string = re.sub(r"•,", "", authors_string)
    authors_string = re.sub(r"•", "", authors_string)

    authors_list = authors_string.split(",")

    lang = ""

    if len(authors_list) > 1:
        for i, author in enumerate(authors_list):
            # Если в результате преобразований в списке появился элемент
            # с пустой строкой, то удаляем его и переходим к следующему элементу
            # списка
            if authors_list[i] == "" or authors_list[i] == " ":
                del authors_list[i]
                continue

            cleared_author_name = re.sub(r"(.*)[a-zа-я]$", r"\1", author)
            cleared_author_name = cleared_author_name.rstrip()
            cleared_author_name = cleared_author_name.strip()
            authors_list[i] = cleared_author_name

    author_name_ru_regex = re.compile(r"[а-яА-ЯёЁ\s\-\.]+")

    lang = author_name_ru_regex.search(authors_list[0])

    if lang[0] == authors_list[0]:
        for i, author in enumerate(authors_list):
            authors_list[i] = translit(author, "ru")

        authors_list = ("ru", authors_list)
    else:
        for i, author in enumerate(authors_list):
            authors_list[i] = translit(author, "ru", reversed=True)

        authors_list = ("en", authors_list)

    return authors_list


class OdtParser:
    def __init__(self, full_path_to_file):
        file = OdtFile(full_path_to_file)

        # Clear data text from unwanted symbols, tags, etc.
        content_data = clear_text(file.get_content_data())

        self.content_data = bs4.BeautifulSoup(content_data, "lxml-xml")
        self.styles_data = bs4.BeautifulSoup(
            file.get_styles_data(), "lxml-xml")

    def get_article_references_list(self) -> list:
        """
        Returns a list with lists, containing both English an Russian
        (or English only) references list in HTML format for each
        article of issue.
        """

        references_list = []

        ref_nodes_list = self.content_data.find_all(
            "text:list", {"text:style-name": re.compile("СтатьяСписокЛит")}
        )

        for ref_node in ref_nodes_list:

            try:
                ref_header = get_ref_header(ref_node).strip()

            except TypeError:

                print("Ошибка в оформлении списка литературы."
                      " Программа аварийно завершена." 
                      f" См. ниже: \n{ref_node.text}")
                sys.exit(1)

            if ref_header == "Список литературы":
                ref_lang = "ru"
            else:
                ref_lang = "en"

            ref_str = get_ref_list_html(ref_node, self.content_data)

            references_list.append((ref_lang, ref_str))

        composed_ref_list = compose_by_article_info_list(references_list)

        return composed_ref_list

    def get_journal_name(self) -> dict:
        """
            Gets journal names from colontitle in Russian and English. Returns
            tuple journal names.
            """

        # Получаем список всех элементов style:footer и style:footer-left
        # для дальнейшего поиска назаний журналов
        footer_styles = self.styles_data.find_all(
            ["style:footer-left", "style:footer"])

        # Формируем регулярное выражение для поиска
        journal_names_ru_string = "|".join(JOURNAL_NAMES_RU_LIST)
        regex_string = "(?:" + journal_names_ru_string + ")"

        # Собираем названия журнала в нижнем колонтитуле каждого из стилей
        # страниц макета в список cur_journal_names_list
        cur_journal_names_list = []

        for footer_style in footer_styles:
            footer_text = footer_style.text
            res = re.search(regex_string, footer_text)

            try:
                if res:
                    cur_journal_names_list.append(res.group())
                else:
                    # Еcли встречается хоть один колонтитул с названием не
                    # из списка, выкидываем исключение
                    raise ValueError()
            except ValueError:
                print(
                    " Найденное название журнала отсутствует в списке.\n",
                    "Неверно оформлен колонтитул макета.\n",
                    "Программа аварийно завершена.",
                )
                sys.exit(1)

        # Множество уникальных названий в нижнем колонтитуле макета
        cur_journal_names_set = set(cur_journal_names_list)

        # Редакторы иногда оставляют стиль страницы из шаблона-примера.
        # Чтобы выбрать правильное название журнала, вводим алгоритм выбора
        # наиболее часто встречающегося названия.

        # Собираем количество вхождений каждого названия
        # в cur_journals_dict.

        # Словарь содержащий название журнала и количество его вхождений
        # в колонтитулы журнала.
        uniq_journals_dict = {}

        for uniq_journal_value in cur_journal_names_set:
            number_of_entries = 0

            for name in cur_journal_names_list:
                if name == uniq_journal_value:
                    number_of_entries += 1

            uniq_journals_dict[uniq_journal_value] = number_of_entries
        # Выбираем наиболее часто встречающееся название журнала через
        # функцию max()
        journal_name_ru = max(uniq_journals_dict.keys())

        i = JOURNAL_NAMES_RU_LIST.index(journal_name_ru)

        journal_name_en = JOURNAL_NAMES_EN_LIST[i]

        journal_name_dict = {
            "journal_name_ru": journal_name_ru, "journal_name_en": journal_name_en
        }

        return journal_name_dict

    def get_number_of_articles_in_issue(self) -> int:
        """
        Gets quantity of articles in issue
        """

        number_of_articles = 0
        for element in self.content_data.find_all("text:p"):
            if "Please cite this article as:" in element.text:
                number_of_articles += 1

        return number_of_articles

    def get_citation_paragraphs_list(self) -> list:
        """
        Gets citation paragraphs from entire issue and returns dictionary with
        keys.
        For Russian citation:
        authors_ru, article_name_ru, year, volume, number_in_year,
        pages_range
        For English citation:
        authors_en, article_name_ru, year, volume, number_in_year, pages_range

        """

        raw_info_list = []

        citation_regex = re.compile(
            r"Для цитирования:|Please cite this " r"article as:"
        )

        for element in self.content_data.find_all("text:p"):

            ru_citation_regex = re.compile(r"Для цитирования")
            search_result = citation_regex.search(element.text)

            if search_result:
                citation_element_str = clear_text(element.text)
                if ru_citation_regex.search(citation_element_str):
                    raw_info_list.append(
                        ("ru", get_info_from_citation_str_ru(citation_element_str))
                    )
                else:
                    raw_info_list.append(
                        ("en", get_info_from_citation_str_en(citation_element_str))
                    )

        composed_cit_info_list = compose_by_article_info_list(raw_info_list)

        return composed_cit_info_list

    def get_article_abstracts_list(self) -> list:
        """
        Gets article abstracts in English and Russian (if exists). 
        """

        p_tags = self.content_data.find_all("text:p")

        abstracts_list = []  # List of annotations to all articles of issue

        for p_tag in p_tags:
            if re.search(r"Аннотация|Abstract", p_tag.text):
                lang = ""
                abstract = ""
                abstract_paragraphs = []  # List of all abstracts of
                # paragraph

                if "Аннотация" in p_tag.text:
                    lang = "ru"
                else:
                    lang = "en"

                for sibling in p_tag.next_siblings:  # Gather all siblings
                    # of p tag, containing string "Abstract" or
                    # "Аннотация"
                    paragraph_text = re.sub(r"\s+", " ", sibling.text)

                    if (
                        re.search(
                            r"Издательский дом ФИНАНСЫ и КРЕДИТ|"
                            r"Publishing house FINANCE and CREDIT",
                            paragraph_text,
                        )
                        == None
                        and paragraph_text != ""
                    ):
                        abstract_paragraphs.append("<p>")  # Add HTML tags
                        abstract_paragraphs.append(paragraph_text)
                        abstract_paragraphs.append("</p>\n")

                abstracts_list.append(
                    (lang, abstract.join(abstract_paragraphs)))

        composed_abstracts_list = compose_by_article_info_list(abstracts_list)

        return composed_abstracts_list

    def get_article_rubrics_list(self):

        style_name_ru = "СтатьяРубрикаРус"
        style_name_en = "СтатьяРубрикаАнгл"

        correct_tree(self.content_data, style_name_ru, "text:p")
        correct_tree(self.content_data, style_name_en, "text:p")

        rubric_nodes_list = self.content_data.find_all(
            "text:p", {"text:style-name": re.compile(r"СтатьяРубрика")}
        )

        rubric_names_list = []
        composed_rubric_names_list = []

        ru_regex = re.compile(r"^[а-яА-ЯёЁ\s\.\,\-]+")

        for element in rubric_nodes_list:

            element = element.text

            res = ru_regex.fullmatch(element[0].strip())

            if element != "":
                if res != None:
                    rubric_names_list.append(("ru",
                                    translit(element, "ru")))
                else:
                    rubric_names_list.append(("en", 
                                    translit(element, "ru", reversed=True)))

        composed_rubric_names_list = compose_by_article_info_list(
            rubric_names_list)

        return composed_rubric_names_list

    def get_article_full_texts_list(self) -> list:
        """
            Метод возвращает список полных текстов всех статей выпуска журнала.
            """

        full_texts_list = []

        full_text_nodes_list = self.content_data.find_all(
            "text:section", {"text:name": re.compile(r"Раздел|Статья")}
        )

        for text_node in full_text_nodes_list:

            # Добавляем пробелы и скобки перед и после подстраничных сносок.
            footnotes_list = text_node.find_all(
                "text:note", {"text:note-class": "footnote"}
            )
            for note in footnotes_list:
                note_body = note.find("text:note-body")
                text = note_body.get_text()
                note.string = " (" + text + ") "

            # Добавляем тире перед элементами списка
            list_tags_list = text_node.find_all("text:list-item")

            for list_tag in list_tags_list:
                text = list_tag.get_text()
                list_tag.string = "- " + text + "\n"

            # Добавляем пробелы перед и после тега text:p
            p_tags_list = text_node.find_all("text:p")

            for p_tag in p_tags_list:
                text = p_tag.get_text()
                p_tag.string = text + "\n"

            # Добавляем пробелы перед и после тега text:span
            span_tags_list = text_node.find_all("text:span")

            for span_tag in span_tags_list:
                text = span_tag.get_text()
                span_tag.string = " " + text + " "

            cleared_text = clear_text(text_node.get_text())

            short_text = cleared_text[:1000]
            article_lang = langdetect.detect(short_text)
            try:
                if article_lang not in ["ru", "en"]:
                    raise ValueError
            except ValueError:
                print(r"Язык основного текста статьи не распознан. Программа"
                      r" остановлена.")
                sys.exit(1) 

            full_texts_list.append(
                {"article_lang": article_lang, article_lang: cleared_text}
            )

        return full_texts_list

    def get_full_author_names_list(self):
        # Метод возвращает список списков полных авторских ФИО, взятых из
        # аффилиации. Пример: ['Евгений Васильевич ПОПОВ',
        # 'Виктория Львовна СИМОНОВА', 'Анна Дмитриевна ТИХОНОВА']
        style_name_ru = r"СтатьяАвторыРус"
        style_name_en = r"СтатьяАвторыАнгл"

        correct_tree(self.content_data, style_name_ru, "text:p")
        correct_tree(self.content_data, style_name_en, "text:p")

        style_name_regex = re.compile(r"СтатьяАвторыРус|СтатьяАвторыАнгл")

        author_nodes_list = self.content_data.find_all(
            "text:p", {"text:style-name": style_name_regex}
        )

        author_strings_list = []
        for authors in author_nodes_list:
            author_strings_list.append(parse_authors_list(re.sub(
                r"\s+", " ", authors.text)))

        composed_authors_names_list = compose_by_article_info_list(
            author_strings_list)

        return composed_authors_names_list

    def get_affiliation_info_list(self):
        """
        Метод возвращает список списков словарей данных об авторах (место
        работы, e-mail, ORCID и SPIN-код)
        """

        style_name_ru = "СтатьяАффилиацияРус"
        style_name_en = "СтатьяАффилиацияАнгл"

        # Корректируем контент-файл для однообразности именования стилей тега p
        correct_tree(self.content_data, style_name_ru, "text:p")
        correct_tree(self.content_data, style_name_en, "text:p")

        # Список, содержащий данные из аффилиаций всех статей
        issue_affiliation_list = []

        # Создаем словарь, в котором ключами будут стили таблиц, содержащих
        # аффилиацию, а значениями списки всех нод стиля СтатьяАффилиацияРус.
        # Тем самым мы группируем ноды (тег p), относящиеся к одной статье
        articles_affiliation_dict = OrderedDict()

        affiliation_regex = re.compile(r"СтатьяАффилиация")

        # Список всех тегов p со стилем СтатьяАффилиацияРус и
        # СтатьяАффилиацияАнгл
        affiliation_nodes_list = self.content_data.find_all(
            "text:p", {"text:style-name": affiliation_regex}
        )

        # Распределяем теги по принадлежности к статьям (через parent-тег
        # table:style-name)
        for node in affiliation_nodes_list:
            table = node.parent  # Узел элемента table, в котором находится
            # аффилиация
            table_style_name = table["table:style-name"]  # Имя стиля таблицы
            # Add space to every node to prevent joining of strings
            node.append(bs4.BeautifulSoup(
                "<text:span> </text:span>", "lxml-xml"))

            if table_style_name in articles_affiliation_dict:
                articles_affiliation_dict[table_style_name].append(node)
            else:
                articles_affiliation_dict[table_style_name] = node

        # Собираем список элементов для каждой статьи
        for affiliation in articles_affiliation_dict.keys():
            affiliation_text = articles_affiliation_dict[affiliation].text
            affiliation_text = str.strip(re.sub(r"\s+", " ", affiliation_text))

            # Удаляем из абзаца подстроку "• Ответственный автор"
            affiliation_text = re.sub(
                r"•[\s]+Ответственный[\s]+автор|•[\s]+Corresponding[\s]"
                r"+author",
                "",
                affiliation_text,
            )

            # Массив информации об авторах для данного блока аффилиацции
            article_authors_list = []

            # Выбираем в параграфе список строк авторских данных: место
            # работы, e-mail, ORCID, SPIN - все авторы для одной статьи
            author_data_list = re.findall(
                r"(?P<workplace>[0-9a-zA-Zа-яА-ЯёЁ\s,\(\)\.\«\»\-\;]+?)\b"
                r"(?P<email>[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~\-]+@[a-zA-Z0-9.\-]"
                r"+\.[a-zA-Z]{2,})\b\s+\b(?P<orcid>https://orcid.org[/\dX\-]"
                r"+|ORCID:\snot\savailable|ORCID:\sотсутствует)?\s"
                r"(?P<spin>SPIN-код:\s\d\d\d\d-\d\d\d\d|SPIN-код:\s"
                r"отсутствует)?",
                str.strip(affiliation_text) + " ",
            )

            author_data_lang = ""

            for author in author_data_list:
                workplace = re.sub(
                    r"^([a-zаесор]\s)?(.*)", r"\2", str.strip(author[0]))

                author_dict = {
                    "workplace": re.sub(r"\s+", " ", workplace),
                    "email": str.strip(author[1]),
                    "orcid": str.strip(author[2]),
                    "spin": str.strip(author[3]),
                }

                if author_data_lang == "":
                    if author_dict["spin"] == "":
                        author_data_lang = "en"
                    else:
                        author_data_lang = "ru"

                article_authors_list.append(author_dict)

            issue_affiliation_list.append(
                (author_data_lang, article_authors_list))

        composed_info = compose_by_article_info_list(issue_affiliation_list)

        return composed_info

    def get_through_issue_number(self):
        """
        Метод возвращает сквозной номер выпуска 
        """

        through_issue_number = ""

        p_list = self.content_data.find_all("text:p")

        for p in p_list:
            res = re.search(
                r".*Валовый\s+\(сквозной\)\s+номер\s+(\d+)\s+", p.text)
            if res != None:
                through_issue_number = res.group(1)
                break

        return through_issue_number

    def get_article_info_list(self):
        """
        Метод получает информацию из ячейки таблицы, содержащей строку
        'История статьи:' - Даты истории статьи, УДК, JEL, ключевые слова.
        Возвращает список словарей.
        """

        issue_articles_info_list = []

        article_info_list = []

        re_text = re.compile(r"История статьи:|Article history:")

        article_info_list = self.content_data.find_all("text:p", text=re_text)

        for p_el in article_info_list:

            article_info_list = []

            article_info_lang = ""

            article_p_list = []

            article_info_dict = {}

            if str.strip(p_el.text) == "История статьи:":
                article_info_lang = "ru"
            else:
                article_info_lang = "en"

            for el in p_el.next_siblings:
                article_p_list.append(el.text)

            article_info_str = " ".join(article_p_list)

            article_info_str = re.sub(r"\s+", " ", article_info_str)

            article_info_ru_regex = re.compile(
                r"(.*)?Получена\s+(\d\d.\d\d.\d\d\d\d).*Получена.*?"
                r"(\d\d.\d\d.\d\d\d\d).*Одобрена.*?(\d\d.\d\d.\d\d\d\d).*"
                r"Доступна онлайн.*?(\d\d.\d\d.\d\d\d\d).*?УДК\s(.*)\s+JEL:\s+"
                r"(.*)\s+Ключевые слова:\s+(.*)"
            )

            article_info_en_regex = re.compile(
                r"(.*)?Received\s+(\d?\d\s\S+\s\d\d\d\d)\s+Received\sin\srevised."
                r"*?(\d?\d\s\S+\s\d\d\d\d)\s+Accepted\s.*?(\d?\d\s\S+\s\d\d\d"
                r"\d)\s+Available\sonline\s.*?(\d?\d\s\S+\s\d\d\d\d)\s+JEL"
                r"\sclassification:\s+(.*)\s+Keywords:\s(.*)"
            )

            if article_info_lang == "ru":
                res = article_info_ru_regex.findall(article_info_str)
                if res != None:
                    article_info_dict = {
                        "reg_number": str.strip(res[0][0]),
                        "received_date_ru": res[0][1],
                        "revised_date_ru": res[0][2],
                        "accepted_date_ru": res[0][3],
                        "available_date_ru": res[0][4],
                        "UDK": re.sub(r"\s+", " ", res[0][5]),
                        "JEL": re.sub(r"\s+", " ", res[0][6]),
                        "keywords_ru": re.sub(r"\s+", " ", res[0][7])
                    }
            else:
                res = article_info_en_regex.findall(article_info_str)
                if res != None:
                    article_info_dict = {
                        "reg_number": str.strip(res[0][0]),
                        "received_date_en": res[0][1],
                        "revised_date_en": res[0][2],
                        "accepted_date_en": res[0][3],
                        "available_date_en": res[0][4],
                        "JEL": re.sub(r"\s+", " ", res[0][5]),
                        "keywords_en": re.sub(r"\s+", " ", translit(res[0][6],
                                                        "ru", reversed=True))
                    }

            issue_articles_info_list.append((article_info_lang,
                                             article_info_dict))

        composed_info = compose_by_article_info_list(issue_articles_info_list)

        return composed_info

    def get_issue_pub_dates_dict(self):

        re_text = re.compile(r"Титу.?Номер.*|Титу.?Год.*")

        pub_dates_list = self.content_data.find_all("text:p",
                                                    {"text:style-name": re_text})

        pub_dates_text_list = [str.lower(x.text) for x in pub_dates_list]

        date_str_ru = " ".join(pub_dates_text_list[:2])

        date_str_en = " ".join(pub_dates_text_list[-2:])

        ru_regex = re.compile(r"том\s+(\d+),\s+выпуск\s+(\d+)\s+"
                              r"([а-яА-ЯёЁ\-\–]+)\s+(\d\d\d\d)")

        en_regex = re.compile(r"volume\s+(\d+),\s+issue\s+(\d+)\s+"
                              r"([a-z\-\–]+)\s+(\d\d\d\d)")

        res_ru = ru_regex.fullmatch(date_str_ru)
        res_en = en_regex.fullmatch(date_str_en)

        pub_dates_ru_dict = {}
        pub_dates_en_dict = {}

        if res_ru != None:
            pub_dates_ru_dict = {
                "volume_ru": res_ru[1],
                "issue_ru": res_ru[2],
                "month_ru": res_ru[3],
                "year_ru":  res_ru[4]
            }

        if res_en != None:
            pub_dates_en_dict = {
                "volume_en": res_en[1],
                "issue_en": res_en[2],
                "month_en": res_en[3],
                "year_en":  res_en[4]
            }

        articles_pub_dates_dict = {"ru": pub_dates_ru_dict,
                                   "en": pub_dates_en_dict}

        return articles_pub_dates_dict
