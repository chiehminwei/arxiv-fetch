import unittest
from datetime import datetime
from arxiv import download, construct_query

 
class TestAPI(unittest.TestCase):

    def test_download_on_filters(self):
        
        search = 'Multi-Agent Reinforcement Learning'
        author = 'devlin'
        journal = 'nips'
        query = construct_query(search, author, journal)

        before = "2019-10-12"
        after = "2018-10-11"
        _before = datetime.strptime(before, "%Y-%m-%d")
        _after = datetime.strptime(after, "%Y-%m-%d")

        papers = download(query=query, max_results=1, before=_before, after=_after)

        self.assertEqual(type(papers), list)
        self.assertEqual(len(papers), 1)

        for paper in papers:

            self.assertIn('title', paper)
            self.assertIn('abstract', paper)
            self.assertIn('authors', paper)
            self.assertIn('publication_time', paper)
            self.assertIn('arxiv_url', paper)
            self.assertIn('pdf_url', paper)
            self.assertIn('journal_reference', paper)

            self.assertTrue(search in paper['title'] or search in paper['abstract'])
            self.assertTrue(any([author.lower() in a.lower() for a in paper['authors']]))
            self.assertIn(journal.lower(), paper['journal_reference'].lower())

            self.assertGreaterEqual(before, paper['publication_time'])
            self.assertGreaterEqual(paper['publication_time'], after)
