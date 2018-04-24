
#   Copyright (c) 2018 Alexander L. Hayes (@batflyer)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import print_function
from __future__ import division

from bs4 import BeautifulSoup as bs

# progress.py is used under the terms of the MIT license
from progress import progress

import argparse
import re
import requests
import time

__author__ = 'Alexander L. Hayes (@batflyer)'
__copyright__ = 'Copyright (c) 2018 Alexander L. Hayes'
__license__ = 'Apache'
__version__ = '0.0.1'
__maintainer__ = __author__
__email__ = 'alexander@batflyer.net'
__status__ = 'Prototype'

def FanfictionScraper(storyid, rate_limit=3):
    """
    Scrapes data from a story on FanFiction.Net

    @method FanfictionScraper
    @param  {str}               storyid         the id for a particular story
    @param  {int}               rate_limit      rate limit (in seconds)
    @return {dict}              story           dictionary of data and metadata
    """

    # Rate limit
    time.sleep(rate_limit)

    # Make a request to the site, create a BeautifulSoup instance for the html
    r = requests.get('https://www.fanfiction.net/s/' + storyid)
    html = r.text
    soup = bs(html, 'html.parser')

    # Get the category and fandom information.
    c_f = soup.find('div', {'id': 'pre_story_links'}).find_all('a', href=True)
    category = c_f[0].text
    fandom = c_f[1].text

    # Get the metadata describing properties of the story.
    # This should contain the metadata line (e.g. rating, genre, words, etc.)
    metadata_html = soup.find('span', {'class': 'xgray xcontrast_txt'})
    metadata = metadata_html.text.replace('Sci-Fi', 'SciFi')
    metadata = [s.strip() for s in metadata.split('-')]

    # Title from <b class='xcontrast_txt'>...</b>
    title = soup.find('b', {'class': 'xcontrast_txt'}).text

    # Abstract and story are identified by <div class='xcontrast_txt'>...</div>
    abstract_and_story = soup.find_all('div', {'class': 'xcontrast_txt'})
    abstract = abstract_and_story[0].text
    story_text = abstract_and_story[1].text

    # 'Publication' and 'last updated' are the two timestamps which are available.
    # If only one timestamp is listed, the story's update and publication time
    # should be the same.
    timestamps = metadata_html.find_all(attrs={'data-xutime': True})
    if len(timestamps) == 1:
        when_updated = timestamps[0]['data-xutime']
        when_published = when_updated
    else:
        when_updated = timestamps[0]['data-xutime']
        when_published = timestamps[1]['data-xutime']

    # There are several links on the page, the 2nd is a link to the author's
    # page. Get the second link href tag (which will look something like '/u/1838183/thisname')
    authorid = soup.find_all('a', {'class': 'xcontrast_txt'})[2].get('href').split('/')[2]

    #print(metadata_html.find_all(attrs={'data-xutime': True}))
    story = {
        'sid': storyid,
        'aid': authorid,
        #'category': category,
        #'fandom': fandom,
        #'title': title,
        #'published': when_published,
        #'updated': when_updated,
        'rating': metadata[0],
        'genre': metadata[2]
        #'metadata': metadata,
        #'abstract': abstract,
        #'story_text': story_text
    }

    #print(metadata)

    #print(soup.prettify())
    return story

def ReviewScraper(storyid, reviews_num, rate_limit=3):
    """
    Scrapes the reviews for a certain story.

    @method ReviewScraper
    @param  {str}               storyid         The id for a particular story.
    @param  {int}               reviews_num     The number of reviews in metadata
    @param  {int}               rate_limit      rate limit (in seconds)
    @return {}

    Discussion:
        * Reviews on FanFiction.Net may either be anonymous or tied to the user
          who left the review.
        * Reviews for a story are located at address:
          https://www.fanfiction.net/r/[sid]/0/1/
        * /0/ represents all reviews for a story, /1/ is a page, and there are
          up to 15 reviews per page.
        * Incrementing the 0 gives the reviews for a particular chapter.

    Page Layout:
        * Reviews are stored in an html table of up to 15 elements.
        * A review may be thought of as a 4-tuple:
            (userid, chapter_reviewed, date, review_text)
    """

    # There may be up to 15 reviews on a single page, therefore the number of
    # pages the reviews  are stored on is equal to the following:
    number_of_pages = (reviews_num // 15) + 1

    exit()

    for p in range(number_of_pages):

        r = requests.get('https://www.fanfiction.net/r/' + storyid + '/0/' + str(p))
        html = r.text
        soup = bs(html, 'html.parser')

        print(p)

def PredicateLogicBuilder(type, id, value):
    """
    Converts inputs into (id, value) pairs, creating positive examples
    and facts in predicate-logic format.

    @method PredicateLogicBuilder
    @param  {str}   type                type of the predicate
    @param  {str}   id                  identifier attribute
    @param  {str}   value               value of the identifier
    @return {str}   ret                 string of the form 'A(B,C).'

    Example:
    >>> f = RelationalPredicateLogic('author', '123', '456')
    >>> print(f)
    author("123","456").
    """

    ret = ''

    if value:
        ret += type
        ret += '("'
        ret += id.replace(' ', '')
        ret += '","'
        ret += value.replace(' ', '')
        ret += '").'
    else:
        ret += type
        ret += '("'
        ret += id.replace(' ', '')
        ret += '").'

    return ret

def ImportStoryIDs(path_to_file):
    """
    Reads FanFiction.Net story-ids from a file, where each story-id is on
    a separate line. Returns a list of strings representing story-ids.

    @method ImportStoryIDs
    @param  {str}               path_to_file    path to sid file.
    @return {list}              sids            list of strings (sids)

    Example:
    $ cat sids.txt
    123
    344
    $ python
    >>> import FanfictionScraper as fs
    >>> sids = fs.ImportStoryIDs('sids.txt')
    >>> sids
    ['123', '344']
    """

    with open(path_to_file) as f:
        sids = f.read().splitlines()

    return sids

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''Scraper for FanFiction.Net.''',
        epilog='''Copyright (c) 2018 Alexander L. Hayes. Distributed under the
                  terms of the Apache 2.0 License. A full copy of the license is
                  available at the base of this repository.'''
    )

    mode = parser.add_mutually_exclusive_group()

    mode.add_argument('-s', '--sid', type=str,
        help='Scrape a single story.')
    mode.add_argument('-f', '--file', type=str,
        help='Scrape all sids contained in a file.')
    mode.add_argument('-r', '--review', type=str,
        help='Scrape the reviews for a particular story.')

    args = parser.parse_args()

    if args.sid:
        # Scrape the contents of a single file from FanFiction.Net
        story = FanfictionScraper(args.sid)

        predicates = []
        predicates.append(PredicateLogicBuilder('author', story['aid'], story['sid']))
        predicates.append(PredicateLogicBuilder('rating', story['sid'], story['rating']))
        predicates.append(PredicateLogicBuilder('genre', story['sid'], story['genre']))

        for p in predicates:
            print(p)

    elif args.review:
        # !!! In progress
        print(args.review)
        print(type(args.review))

        ReviewScraper(args.review, 16)
        print('Reached?')
        exit()

    elif args.file:
        # Import the sids from the file and scrape each of them.

        sids = ImportStoryIDs(args.file)

        # Values for the progress bar.
        number_of_sids = len(sids)
        counter = 0

        for sid in sids:

            # Helpful progress bar
            progress(counter, number_of_sids, status='Currently on: {0}'.format(sid))
            counter += 1

            story = FanfictionScraper(sid)

            predicates = []
            predicates.append(PredicateLogicBuilder('author', story['aid'], story['sid']))
            predicates.append(PredicateLogicBuilder('rating', story['sid'], story['rating']))
            predicates.append(PredicateLogicBuilder('genre', story['sid'], story['genre']))

            with open('facts.txt', 'a') as f:
                for p in predicates:
                    f.write(p + '\n')
