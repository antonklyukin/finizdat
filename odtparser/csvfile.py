#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import odtparser


journal_info = odtparser.gather_journal_info('./test_file/re.odt')
path = './test_file/re.csv'
flattened_journal_info = odtparser.flatten_journal_info_dict(journal_info)


def csv_writer(data, path):
    """
    Write data to a CSV file path
    """
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        for line in data:
            writer.writerow(line)


csv_writer(flattened_journal_info, path)
