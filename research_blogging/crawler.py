# -*- coding: utf-8 -*-

from __future__ import print_function
from research_blogging.scraper import ResearchBloggingScraper
from bs4 import BeautifulSoup

import time

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError


class ResearchBloggingCrawler:

    page_count = 1
    FINISH_CRAWL = "Finish crawl!"

    def __init__(self, target_url, save_dir="./data"):
        self.target_url = target_url
        self.before_url = None
        self.save_dir = save_dir

    def _make_soup(self, url):
        try:
            with urlopen(url) as response:
                html = response.read()

            return BeautifulSoup(html, "lxml")

        except HTTPError as e:
            print("[ DEBUG ] in {}#make_soup: {}".format(self.__class__.__name__, e))
            return None

    def get_next_page_link(self, url):

        self.before_url = url
        soup = self._make_soup(self.target_url)
        ul_pageBrowser = soup.find("ul", {"class": "pageBrowser"})
        a_next = ul_pageBrowser.find("a", {"class": "underlined"})

        if a_next is not None and "href" in a_next.attrs:
            next_page_url = a_next["href"]

            if self.before_url != next_page_url:
                print("[ DEBUG ] Next article list page: {}".format(url))
                return next_page_url

        return None

    def crawl(self):

        while True:
            start = time.time()
            print("[ DEBUG ] Now page {} PROCESSING".format(self.page_count))
            scraper = ResearchBloggingScraper(self.target_url, self.save_dir)
            scraper.scrap()
            self.target_url = self.get_next_page_link(self.target_url)

            if self.target_url is None:
                break

            self.page_count += 1
            time.sleep(2)

            end = time.time()
            print("[ DEBUG ] Elapsed time: {:.3f} [min]".format((end - start) / 60))

        return self.FINISH_CRAWL
