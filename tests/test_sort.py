import unittest
from arxiv import download
 

class TestAPI(unittest.TestCase):

    def test_download_on_sort(self):
        asc_papers = download(query='rnn',
                              max_results=3,
                              sort_by='submittedDate',
                              sort_order='ascending')

        desc_papers = download(query='rnn',
                              max_results=3,
                              sort_by='submittedDate',
                              sort_order='descending')

        self.assertEqual(type(asc_papers), list)
        self.assertEqual(len(asc_papers), 3)

        self.assertEqual(type(desc_papers), list)
        self.assertEqual(len(desc_papers), 3)

        for i, paper in enumerate(asc_papers):

            self.assertIn('title', paper)
            self.assertIn('abstract', paper)
            self.assertIn('authors', paper)
            self.assertIn('publication_time', paper)
            self.assertIn('arxiv_url', paper)
            self.assertIn('pdf_url', paper)
            self.assertIn('journal_reference', paper)

            if i > 0:
                self.assertGreaterEqual(paper['publication_time'],
                    asc_papers[i-1]['publication_time'])

        for i, paper in enumerate(desc_papers):

            self.assertIn('title', paper)
            self.assertIn('abstract', paper)
            self.assertIn('authors', paper)
            self.assertIn('publication_time', paper)
            self.assertIn('arxiv_url', paper)
            self.assertIn('pdf_url', paper)
            self.assertIn('journal_reference', paper)

            if i > 0:
                self.assertGreaterEqual(desc_papers[i-1]['publication_time'],
                    paper['publication_time'])
