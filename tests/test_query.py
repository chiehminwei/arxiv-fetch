import unittest
from arxiv import download
 

class TestAPI(unittest.TestCase):

    def test_download_on_query(self):
        papers = download(query='rnn', max_results=2)

        self.assertEqual(type(papers), list)
        self.assertEqual(len(papers), 2)

        for paper in papers:

            self.assertIn('title', paper)
            self.assertIn('abstract', paper)
            self.assertIn('authors', paper)
            self.assertIn('publication_time', paper)
            self.assertIn('arxiv_url', paper)
            self.assertIn('pdf_url', paper)
            self.assertIn('journal_reference', paper)
