#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile


class OdtFile:

    def __init__(self, odt_filename):
        self.odt_filename = odt_filename
        self.odt_file_as_zip = zipfile.ZipFile(odt_filename, 'r')
        self.content_file_bytes = None
        self.styles_file_bytes = None

    def get_content_data(self):
        self.content_file_bytes = self.odt_file_as_zip.read('content.xml')
        return(self.content_file_bytes.decode('utf-8'))

    def get_styles_data(self):
        self.styles_file_bytes = self.odt_file_as_zip.read('styles.xml')
        return(self.styles_file_bytes.decode('utf-8'))
