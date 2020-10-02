import argparse
from datetime import datetime
import os
import sys
import logging
import time
import re
import feedparser
import json
from urllib.parse import quote
from urllib.request import urlretrieve
from multiprocessing.pool import ThreadPool

# Logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logger = root


class Search(object):
    """
    Class to search and download abstracts and pdfs from the arXiv
    Args:
        query (string): the user query
        downloadPDF (bool): whether to download PDF
        downloadMeta (bool): whether to download metadata
        save_path (str): where to save the downloaded files
        max_results (int): The maximum number of abstracts to retrieve. Defaults to 10.
        sort_by (string): The arXiv field by which the result should be sorted.
        sort_order (string): The sorting order, i.e. "ascending", "descending" or None.
        max_chunk_results (int): Internally, a arXiv search query is split up into smaller
            queries that download the data iteratively in chunks. This parameter sets an upper
            bound on the number of abstracts to be retrieved in a single internal request.
        time_sleep (int): Time (in seconds) between two subsequent arXiv REST calls. Defaults to
            :code:`3`, the recommendation of arXiv.
        before (str): Filter for articles published before the specified datetime.
            Defaults to None.
        after (str): Filter for articles published after the specified datetime.
            Defaults to None.
    """

    root_url = 'http://export.arxiv.org/api/'

    def __init__(self, query=None, downloadPDF=True, downloadMeta=False,
                 save_path='./', max_results=1, sort_by=None, sort_order=None, 
                 max_chunk_results=100, time_sleep=3, before=None, after=None):

        self.query = query
        self.downloadPDF = downloadPDF
        self.downloadMeta = downloadMeta
        self.save_path = save_path
        self.before = before
        self.after = after
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.time_sleep = time_sleep
        self.max_chunk_results = max_chunk_results        
        self.max_results = max_results

    def _get_url(self, start=0, max_results=None):

        url_args = 'search_query={}&start={}&max_results={}&sortBy={}&sortOrder={}'.format(
            self.query, start, max_results, self.sort_by, self.sort_order
        )

        return self.root_url + 'query?' + url_args

    def _parse(self, url):
        """
        Download the data provided by the REST endpoint given in the url.
        """
        result = feedparser.parse(url)

        if result.get('status') != 200:
            logger.error(
                "HTTP Error {} in query".format(result.get('status', 'no status')))
            return []
        return result['entries']

    def _process_result(self, result):
        """
        Process a single result
        """
        parsed = {}
        parsed['title'] = result['title'].rstrip('\n')
        parsed['abstract'] = result['summary'].rstrip('\n')
        parsed['authors'] = [d['name'] for d in result['authors']]
        parsed['publication_time'] = result['published']
        parsed['arxiv_url'] =  result['link']
        parsed['pdf_url'] = None
        for link in result['links']:
            if 'title' in link and link['title'] == 'pdf':
                parsed['pdf_url'] = link['href']
        if 'arxiv_journal_ref' in result:
            parsed['journal_reference'] = result.pop('arxiv_journal_ref')
        else:
            parsed['journal_reference'] = None

        return parsed

    def _in_range(self, publication_time):
        """
        Helper function for determining whether an article's publication time meets the criteria
        """
        inRange = True
        index = publication_time.find('T')
        publication_time = datetime.strptime(publication_time[:index], "%Y-%m-%d")
        if self.before:
            inRange &= publication_time <= self.before
        if self.after:
            inRange &= publication_time >= self.after
        return inRange

    def _get_next(self):

        n_left = self.max_results
        start = 0

        while n_left > 0:

            if n_left < self.max_results:
                logger.info('... play nice on the arXiv and sleep a bit ...')
                time.sleep(self.time_sleep)

            logger.info('Fetch from arxiv ({} results left to download)'.format(n_left))
            url = self._get_url(
                start=start,
                max_results=min(n_left, self.max_chunk_results))

            results = self._parse(url)

            # Process results
            results = [self._process_result(r) for r in results if r.get("title", None)]
            filtered_results = [r for r in results if self._in_range(r['publication_time'])]
            
            # Update the entries left to download
            n_fetched = len(results)
            logger.info('Received {} entries'.format(n_fetched))

            if n_fetched == 0:
                logger.info('No more entries left to fetch.')
                logger.info('Fetching finished.')
                break

            # Update the number of results left to download
            n_left = n_left - n_fetched
            start = start + n_fetched

            yield filtered_results

    def _download_single(self, obj):
        """
        Download the .pdf or  corresponding to the result object 'obj'.
        """
        def slugify(obj):
            """ 
            Remove special characters from object title
            """
            filename = '_'.join(re.findall(r'\w+', obj.get('title', 'UNTITLED')))
            return filename

        dirpath=self.save_path
        if dirpath[-1] != '/':
            dirpath += '/'

        if self.downloadPDF:            
            if not obj.get('pdf_url', ''):
                print("Object has no PDF URL.")
                return
            url = obj['pdf_url']
            path = dirpath + slugify(obj) + '.pdf'
            urlretrieve(url, path)

        if self.downloadMeta:
            path = dirpath + slugify(obj) + '.json'
            with open(path, 'w') as f:
                json.dump(obj, f, indent=4, sort_keys=True)

        return path


    def download(self):
        """
        Triggers the download of the result of the given search query.
        """
        logger.info('Start downloading')
        for result in self._get_next():
            paths = ThreadPool(8).imap_unordered(self._download_single, result)
            for path in paths:
                logger.info(path)

def download(query="", downloadPDF=True, downloadMeta=False, save_path='./',
             sort_by="relevance", sort_order="descending", max_results=None,
             max_chunk_results=100, before=None, after=None):
    """
    See :py:class:`arxiv.Search` for a description of the parameters.
    """

    search = Search(
        query=query,
        downloadPDF=downloadPDF,
        downloadMeta=downloadMeta,
        save_path=save_path,
        sort_by=sort_by,
        sort_order=sort_order,
        max_results=max_results,
        max_chunk_results=max_chunk_results,
        before=before,
        after=after)

    search.download()   

def construct_query(search, author, journal):
    """ 
    Construct arXiv API query based on user input.
    Search in title and abstract by default.
    """
    title = 'ti:' + quote(search)
    abstract = 'abs:' + quote(search)
    query = '(' + '+OR+'.join([title, abstract]) + ')'

    filters = []
    if author:
        author = 'au:' + quote(author)
        filters.append(author)
    if journal:
        journal = 'jr:' + quote(journal)
        filters.append(journal)
    query += '+AND+'.join(filters)
    return query

def main(**kwargs):
    # Construct query
    search = kwargs['search']
    author = kwargs['author']
    journal = kwargs['journal_reference']
    query = construct_query(search, author, journal)

    # Download flags
    downloadPDF = kwargs['download_pdf']
    downloadMeta = kwargs['download_meta']
    save_path = kwargs['save_path']
    
    # Query
    sort_by = kwargs['sort_by']
    sort_order = kwargs['sort_order']
    max_results = kwargs['max_results']
    max_chunk_results= kwargs['max_chunk_results']

    # Filters
    before = kwargs['published_before']
    after = kwargs['published_after']
    
    download(query,
             downloadPDF, downloadMeta, save_path,
             sort_by, sort_order,
             max_results, max_chunk_results,
             before, after)

if __name__ == '__main__':
    # Argparse types
    def dir_path(string):
        if os.path.isdir(string):
            return string
        else:
            raise NotADirectoryError(string)

    def sort_by(string):
        if string in ['relevance', 'lastUpdatedDate', 'submittedDate']:
            return string
        else:
            msg = "sort_by must be either 'relevance', 'lastUpdatedDate', or 'submittedDate'"
            raise argparse.ArgumentTypeError(msg)

    def sort_order(string):
        if string in ['ascending', 'descending']:
            return string
        else:
            msg = "sort_order must be either 'ascending' or 'descending'"
            raise argparse.ArgumentTypeError(msg)

    def valid_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    parser = argparse.ArgumentParser(description='Download PDF and metadata from arXiv.')

    # Query
    parser.add_argument('-s', '--search', type=str, required=True,
        help="Query to search for in the article's title and abstract.")
    parser.add_argument('-sort', '--sort_by', type=sort_by, default='relevance',
        help="Either 'relevance', 'lastUpdatedDate', or 'submittedDate'. Defaults to relevance.")
    parser.add_argument('-order', '--sort_order', type=sort_order, default='descending',
        help="Either 'ascending' or 'descending'.")
    parser.add_argument('-result', '--max_results', type=int, default=1,
        help="The max number of results to retrieve. Defaults to 1.")
    parser.add_argument('-chunk', '--max_chunk_results', type=int, default=100,
        help="The max number of articles to batch-download at a time. Defaults to 100.")

    # Download
    parser.add_argument('-pdf', '--download_pdf', type=bool, default=True, 
        help='Flag for whether to download query results as pdf files.')
    parser.add_argument('-meta', '--download_meta', action='store_true',
        help='Flag for whether to download metadata (title, abstract, authors, arxiv_url, journal_reference, publication_time).')
    parser.add_argument('-path', '--save_path', type=dir_path, default='./',
        help='Directory for saving the downloaded articles.')

    # Filters
    parser.add_argument('-a', '--author', type=str, default='',
        help='Filter for article author.')
    parser.add_argument('-j', '--journal_reference', type=str, default='',
        help='Filter for journal reference.')
    parser.add_argument('-after', '--published_after', type=valid_date, default=None,
        help='Filter for publication date (e.g. 2020-01-01).')
    parser.add_argument('-before', '--published_before', type=valid_date, default=None,
        help='Filter for publication date (e.g. 2020-01-01).')

    kwargs = parser.parse_args()
    main(**vars(kwargs))
