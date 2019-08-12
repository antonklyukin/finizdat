import unittest

from odtparser.odtparser import OdtParser
import tests.testdata as td

odt_parser_ni = OdtParser('/home/user035/projects/finizdat/\
odtparser/test_odt/ni.odt')

odt_parser_ea = OdtParser('/home/user035/projects/finizdat/\
odtparser/test_odt/ea.odt')

odt_parser_re = OdtParser('/home/user035/projects/finizdat/\
odtparser/test_odt/re.odt')


class TestOdtParserJournalNameRu(unittest.TestCase):

    def test_get_journal_name_ru_ni(self):
        global odt_parser_ni
        parsed_journal_name_ru = odt_parser_ni.get_journal_name_ru()
        self.assertEqual(parsed_journal_name_ru, 'Национальные интересы: приори\
теты и безопасность')

    def test_get_journal_name_ru_ea(self):
        global odt_parser_ea
        parsed_journal_name_ru = odt_parser_ea.get_journal_name_ru()
        self.assertEqual(parsed_journal_name_ru, 'Экономический анализ: теория \
и практика')

    def test_get_journal_name_ru_re(self):
        global odt_parser_re
        parsed_journal_name_ru = odt_parser_re.get_journal_name_ru()
        self.assertEqual(parsed_journal_name_ru, 'Региональная экономика: \
теория и практика')


class TestOdtParserNumberOfArticles(unittest.TestCase):

    def test_get_number_of_articles_ni(self):
        global odt_parser_ni
        parsed_number_of_articles_ni = (odt_parser_ni.
                                        get_number_of_articles_in_journal())
        self.assertEqual(parsed_number_of_articles_ni, 11)

    def test_get_number_of_articles_ea(self):
        global odt_parser_ea
        parsed_number_of_articles_ea = (odt_parser_ea.
                                        get_number_of_articles_in_journal())
        self.assertEqual(parsed_number_of_articles_ea, 11)

    def test_get_number_of_articles_re(self):
        global odt_parser_re
        parsed_number_of_articles_re = (odt_parser_re.
                                        get_number_of_articles_in_journal())
        self.assertEqual(parsed_number_of_articles_re, 13)


class TestOdtParserInfoListFromCitationRu(unittest.TestCase):

    def test_get_info_list_from_citation_paragraph_ni(self):
        global odt_parser_ni
        parsed_info_list_from_citation_paragraph_ni = (odt_parser_ni.
                                    get_info_list_from_citation_paragraph_ru())
        self.assertEqual(parsed_info_list_from_citation_paragraph_ni, eval(td.
            parsed_info_list_from_citation_paragraph_ni))

    def test_get_info_list_from_citation_paragraph_ea(self):
        global odt_parser_ea
        parsed_info_list_from_citation_paragraph_ea = (odt_parser_ea.
                                    get_info_list_from_citation_paragraph_ru())
        self.assertEqual(parsed_info_list_from_citation_paragraph_ea, eval(td.
            parsed_info_list_from_citation_paragraph_ea))

    def test_get_info_list_from_citation_paragraph_re(self):
        global odt_parser_re
        parsed_info_list_from_citation_paragraph_re = (odt_parser_re.
                                    get_info_list_from_citation_paragraph_ru())
        self.assertEqual(parsed_info_list_from_citation_paragraph_re, eval(td.
            parsed_info_list_from_citation_paragraph_re))


if __name__ == '__main__':

    unittest.main()
