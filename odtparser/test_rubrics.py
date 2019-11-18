#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
from odtparser.journals_info import MONTHS_EN_LIST, RUBRICS_DICT

en_rubric = "Regional Strategic Planning"

def get_ru_rubric_from_en_rubric(en_rubric):
    ru_rubric = ""
    for k, v in RUBRICS_DICT.items():
        if v == en_rubric:
            ru_rubric = k
    return ru_rubric
