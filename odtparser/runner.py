#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from odtparser.odtparser import OdtParser
import os


if __name__ == '__main__':
    # Получаем полный путь до файла модуля
    module_filepath = os.path.realpath(__file__)

    # Получаем полный путь до директории модуля
    module_dirpath = os.path.dirname(module_filepath)

    # Добавляем директорию и файл с тестовыми верстками
    test_odt_filepath = os.path.join(module_dirpath, 'test_odt', 'ea.odt')
    odt_parser = OdtParser(test_odt_filepath)

    print(odt_parser.get_references_ru_list())

