# arxiv-fetch[![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/downloads/release/python-270/) [![Python 3.6](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

Command line utility for [the arXiv API](http://arxiv.org/help/api/index).
Downloads PDFs and metadata for query results in parallel.

## About arXiv

[arXiv](http://arxiv.org/) is a project by the Cornell University Library that provides open access to 1,000,000+ articles in Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, and Statistics.

### Dependencies

```bash
$ pip install feedparser
$ pip install numpy # For unit-testing only
```

## Usage

### Basic
Download the first PDF to the current directory based on the search parameter.
```bash
python arxiv.py --search cnn
```

### Download metadata
Download metadata as json in additiona to the PDF.
```bash
python arxiv.py --search cnn \
                --download_meta
```

### Download multiple files in parallel
```bash
python arxiv.py --search cnn \
                --download_meta \
                --max_results 10
```

### Sort and filter
```bash
python arxiv.py --search 'Multi-Agent Reinforcement Learning' \
                --sort_by submittedDate \
                --sort_order ascending \
                --max_results 10 \
                --max_chunk_results 1000 \
                --download_meta \
                --save_path ./arxiv \
                --author devlin \
                --journal_reference nips \
                --published_before 2019-10-12 \
                --published_after 2018-10-11

```
💡 *Note on datetime filters*: for `published_before` and `published_after`, since the arxiv API does not provide a native way to query based on time, these only serve as post-processing filters. So, for example, if `max_results=100`, 100 articles may be retrieved, but if none of these articles are in the date range specified by the filter (`published_before <= publication_time <= published_after`), 0 articles would be downloaded.

### Command Line Options

```text
usage: arxiv.py [-h] -s SEARCH [-sort SORT_BY] [-order SORT_ORDER]
                [-result MAX_RESULTS] [-chunk MAX_CHUNK_RESULTS]
                [-pdf DOWNLOAD_PDF] [-meta] [-path SAVE_PATH] [-a AUTHOR]
                [-j JOURNAL_REFERENCE] [-after PUBLISHED_AFTER]
                [-before PUBLISHED_BEFORE]

Download PDF and metadata from arXiv.
```

| **Argument**   | **Type**        | **Default**    |
|----------------|-----------------|----------------|
| `search`       | string          | `""`           |
| `sort_by`      | string          | `"relevance"`  |
| `sort_order`   | string          | `"descending"` |
| `max_results`  | int             | 1              |
| `max_chunk_results` | int        | 100            |
| `download_pdf` | boolean         | `True`         |
| `download_meta`| boolean         | `False`        |
| `save_path`    | string          | `"./"`           |
| `author`       | string          | `""`           |
| `journal_reference` | string     | `""`           |
| `published_before` | string      | `""`           |
| `published_after`  | string      | `""`           |


+ `search`: query to search for in the article's title and abstract.

+ `sort_by`: the arXiv field by which the result should be sorted; `"relevance"`, `"lastUpdatedDate"`, or `"submittedDate"`.

+ `sort_order`: the sorting order, i.e. `"ascending"`, `"descending"` or `None`.

+ `max_results`: the maximum number of results to download.

+ `max_chunk_results`: the maximum number of articles to be downloaded by a single internal request to the arXiv API.

+ `download_pdf`: when `True`, received article PDFs will be downloaded.

+ `download_meta`: when `True`, received article metadata will be downloaded in a json format.
    * metadata: `title`, `abstract`, `authors`, `arxiv_url`, `journal_reference`, `publication_time`

+ `save_path`: path to save the downloaded files.

+ `author`: filter for article author.

+ `journal_reference`: filter for journal reference.

+ `published_before`: filter for publication date, a datetime string including year, month, and date (e.g. 2020-01-01).

+ `published_after`: filter for publication date, a datetime string including year, month, and date (e.g. 2020-01-01).

## Reference

This repo is modified from the [arxiv.py](https://github.com/lukasschwab/arxiv.py) repository, a Python wrapper for the [arXiv API](https://arxiv.org/help/api/index).