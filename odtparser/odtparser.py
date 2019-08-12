#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import sys


from odtparser.odtfile import OdtFile
from odtparser.journals_info import journal_names_ru_list


def clear_text(text):
    """
    Функция удаляет двойные пробелы, пробелы в начале и конце текста и прочее
    """

    stripped_text = text.strip()
    cleared_text = re.sub(r' +', ' ', stripped_text)
    cleared_text = re.sub(r'\xa0', ' ', cleared_text)
    cleared_text = re.sub(r'\s\.', '.', cleared_text)
    cleared_text = re.sub(r'<text:line-break/>', ' ', cleared_text)
    cleared_text = re.sub(r'·', 'X', cleared_text)
    cleared_text = re.sub(r'(№)(\S)', r'\1 \2', cleared_text)
    cleared_text = re.sub(r'\s,', ',', cleared_text)

    return cleared_text


def correct_tree(odt_content, style_name, tag_name):
    """
    Normalizes odt content adding text:style-name element.
    """

    nodes_list = odt_content.find_all('style:style',
                                      {'style:parent-style-name':
                                       style_name})
    list_of_node_number_styles = []

    for node in nodes_list:
        if node['style:name'] not in list_of_node_number_styles:
            list_of_node_number_styles.append(node['style:name'])

    for number_style in list_of_node_number_styles:
        nodes_list = odt_content.find_all(tag_name,
                                          {'text:style-name': number_style})
        for node in nodes_list:
            element = odt_content.find(
                tag_name, {'text:style-name': number_style})
            element['text:style-name'] = style_name


def clear_ref_element(element, content_data):
    for tag in element:
        if tag.name == 'span':

            style_name = tag['text:style-name']

            style_element = content_data.find('style:style',
                                              {'style:name': style_name})

            font_type = style_element.find('style:text-properties')

            if font_type.get('fo:font-style') == 'italic':
                tag.name == 'i'
            else:
                tag.extract()

    return element


class OdtParser:

    def __init__(self, full_path_to_file):
        file = OdtFile(full_path_to_file)

        # Хак - Предварительная чистка файла: замена тегов, удаление мусора
        content_data = clear_text(file.get_content_data())

        self.content_data = BeautifulSoup(content_data, 'lxml-xml')
        self.styles_data = BeautifulSoup(file.get_styles_data(), 'lxml-xml')

    def get_journal_name_ru(self):
        """
        Метод получения названия журнала на русском из стиля нижнего
        колонтитула макета.
        """

        # Получаем список всех элементов style:footer и style:footer-left
        # для дальнейшего поиска назаний журналов
        footer_styles = self.styles_data.find_all(
            ['style:footer-left', 'style:footer'])

        # Формируем регулярное выражение для поиска
        journal_names_ru_string = '|'.join(journal_names_ru_list)
        regex_string = '(?:' + journal_names_ru_string + ')'

        # Собираем названия журнала в нижнем колонтитуле каждого из стилей
        # страниц макета в список cur_journal_names_list
        cur_journal_names_list = []

        for footer_style in footer_styles:
            footer_text = footer_style.get_text()
            res = re.search(regex_string, footer_text)

            try:
                if res:
                    cur_journal_names_list.append(res.group())
                else:
                    # Еcли встречается хоть один колонтитул с названием не из
                    # списка, выкидываем исключение
                    raise ValueError()
            except ValueError:
                print(' Найденное название журнала отсутствует в списке.\n',
                      'Неверно оформлен колонтитул макета.\n',
                      'Программа аварийно завершена.')
                sys.exit(0)

        # Множество уникальных названий в нижнем колонтитуле макета
        cur_journal_names_set = set(cur_journal_names_list)

        # Редакторы иногда оставляют стиль страницы из шаблона-примера.
        # Чтобы выбрать правильное название журнала, вводим алгоритм выбора
        # наиболее часто встречающегося названия.

        # Собираем количество вхождений каждого названия в cur_journals_dict.

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

        return journal_name_ru

    def get_number_of_articles_in_journal(self):
        """
        Метод подсчета количества статей в журнале. Подсчитывает количество
        абзацев, содержащих "Для цитирования".
        """

        number_of_articles = 0
        for element in self.content_data.find_all('text:p'):
            if 'Для цитирования' in element.get_text():
                number_of_articles += 1

        return number_of_articles

    def get_info_list_from_citation_paragraph_ru(self):
        """
        Метод из строк "Для цитирования" статьи всего журнала возвращает
        список свойств вида: [authors_ru, article_name_ru, year,
        volume, number, pages_range] для каждой статьи.
        """

        citation_info_list = []
        # TODO: Доработать регулярку для вылавливания китайских фамилий
        regex_ru_citation = re.compile(r'^Для цитирования:\s(.*?[А-ЯЁA-Z]\.)[\s]+(.*)'
                                       r'[\s]+//[\s]+?.*([2][0][1-9][0-9]).*Т\.'
                                       r'[\s]+?([\d][\d]),[\s]+?№\s?(\d\d?)\..*'
                                       r'С\.?[\s]+?([\d\s–-]+)')

        for element in self.content_data.find_all('text:p'):
            if 'Для цитирования' in element.get_text():

                result = regex_ru_citation.match(
                    element.get_text())

                if result is None:
                    print('Что-то не так со строкой для цитирования - {0}.'
                          ' Программа аварийно завершена.'.format(
                           element.get_text()))
                    sys.exit(1)

                authors_ru = result.group(1)
                article_name_ru = result.group(2)
                year = result.group(3)
                volume = result.group(4)
                number = result.group(5)
                pages_range = result.group(6)

                citation_info_list.append([authors_ru, article_name_ru, year,
                                           volume, number, pages_range])

        return citation_info_list

    def get_article_abstracts_ru_html(self):

        p_tags = self.content_data.find_all('text:p')
        abstracts_list = []  # Список аннотаций ко всем статьям выпуска
        for p_tag in p_tags:
            if 'Аннотация' in p_tag.get_text():
                abstract = ''
                abstract_paragraphs = []  # Список всех абзацев аннотации
                for sibling in p_tag.next_siblings:  # Собираем все абзацы
                    # того же уровня вложенности, что и "Аннотация"
                    paragraph_text = sibling.get_text()

                    if ('Издательский дом ФИНАНСЫ и КРЕДИТ' not in
                            paragraph_text and paragraph_text != ''):
                        abstract_paragraphs.append('<p>')  # Добавляем теги
                        abstract_paragraphs.append(paragraph_text)
                        abstract_paragraphs.append('</p>\n')

                abstracts_list.append(abstract.join(abstract_paragraphs))

        return abstracts_list

    def get_article_rubrics_ru(self):

        style_name_ru = 'СтатьяРубрикаРус'
        style_name_en = 'СтатьяРубрикаАнгл'

        correct_tree(self.content_data, style_name_ru, 'text:p')
        correct_tree(self.content_data, style_name_en, 'text:p')

        rubric_nodes_list = self.content_data.find_all(
            'text:p', {'text:style-name': re.compile(r'СтатьяРубрика')})

        rubric_names_list = []
        for element in rubric_nodes_list:
            rubric_names_list.append(element.get_text())

        try:
            if len(rubric_names_list) % 2 != 0:
                raise ValueError
        except ValueError:
            print('Ошибка в разметке рубрик.\n'
                  'Возможно, перепутаны русский и английский стили. \n'
                  'Программа аварийно завершена.')

        return rubric_names_list

    def get_article_keywords_ru(self):
        """
        Метод собирает ключевые слова из пристатейной информации всех статей
        выпуска в возвращаемый список.
        """
        # Очень медленная функция,
        # переписать

        style_name_ru = 'СтатьяИнфоРус'

        correct_tree(self.content_data, style_name_ru, 'text:p')

        info_ru_list = self.content_data.find_all(
            'text:p', {'text:style-name': style_name_ru})

        keywords_ru_list = []

        for element in info_ru_list:
            if 'Ключевые слова:' in (element.get_text()):
                element_string = element.get_text()
                cleared_string = element_string.replace('Ключевые слова: ', '')
                keywords_ru_list.append(cleared_string)

        return keywords_ru_list

    def get_article_text_ru_list(self):
        """
        Метод возвращает список полных текстов всех статей выпуска журнала.
        """

        full_texts_list = []

        full_text_nodes_list = self.content_data.find_all(
            'text:section')

        for text_node in full_text_nodes_list:

            # Добавляем пробелы и скобки перед и после подстраничных сносок.
            footnotes_list = text_node.find_all('text:note',
                                                {'text:note-class':
                                                 'footnote'})
            for note in footnotes_list:
                note_body = note.find('text:note-body')
                text = note_body.get_text()
                note.string = ' (' + text + ') '

            # Добавляем тире перед элементами списка
            list_tags_list = text_node.find_all('text:list-item')

            for list_tag in list_tags_list:
                text = list_tag.get_text()
                list_tag.string = '- ' + text + '\n'

            # Добавляем пробелы перед и после тега text:p
            p_tags_list = text_node.find_all('text:p')

            for p_tag in p_tags_list:
                text = p_tag.get_text()
                p_tag.string = text + '\n'

            # Добавляем пробелы перед и после тега text:span
            span_tags_list = text_node.find_all('text:span')

            for span_tag in span_tags_list:
                text = span_tag.get_text()
                span_tag.string = ' ' + text + ' '

            cleared_text = clear_text(text_node.get_text())

            full_texts_list.append(cleared_text)

        return full_texts_list

    def get_references_ru_list(self):
        ref_nodes_list = self.content_data.find_all(
            'text:list', {'text:style-name': 'СтатьяСписокЛитРус'})

        first_ref_node = ref_nodes_list[0]

        first_ref_element = first_ref_node.find_all('text:p')[2]

        print(first_ref_element, '\n')

        res_element = clear_ref_element(first_ref_element, self.content_data)
        print(res_element)

        # print(first_ref_element.get_text())

        # for el in first_ref_element:
        #     print(el, '\n')

        # ref_list = first_ref_node.find_all('text:p')

        # for element in ref_list[1]:
        #     children = element.findChildren()
        #     for child in children:
        #         print(child)
        # return len(ref_list)
