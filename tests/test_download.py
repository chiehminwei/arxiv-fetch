import arxiv
import os
import shutil
import tempfile
import unittest


class TestDownload(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        search = 'Multi-Agent Reinforcement Learning'
        author = 'devlin'
        journal = 'nips'
        self.paper_query = arxiv.construct_query(search, author, journal)

    @classmethod
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_download_from_query(self):
        arxiv.download(self.paper_query, max_results=1, save_path=self.temp_dir)
        self.assertTrue(
                os.path.exists(
                    os.path.join(
                        self.temp_dir,
                        'The_Multi_Agent_Reinforcement_Learning_in_MalmÖ_MARLÖ_Competition.pdf')
                )
        )