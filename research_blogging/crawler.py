# -*- coding: utf-8 -*-

from __future__ import print_function
from research_blogging.scraper import ResearchBloggingScraper
from bs4 import BeautifulSoup

import time
import traceback
import json

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError


class ResearchBloggingCrawler:

    FINISH_CRAWL = "Finish crawl!"

    def __init__(self, target_url, save_dir="./data", page_count=1):
        self.target_url = target_url
        self.before_url = None
        self.save_dir = save_dir
        self.page_count = page_count

    def _make_soup(self, url):

        max_retries = 3
        retries = 0

        while True:
            try:
                with urlopen(url) as res:
                    html = res.read()
                return BeautifulSoup(html, "lxml")

            except HTTPError as err:
                print("[ EXCEPTION ] in {}#make_soup: {}".format(self.__class__.__name__, err))

                retries += 1
                if retries >= max_retries:
                    raise Exception("Too many retries.")

                wait = 2 ** (retries - 1)
                print("[ RETRY ] Waiting {} seconds...".format(wai))
                time.sleep(wait)

    def get_next_page_link(self, url):

        self.before_url = url
        soup = self._make_soup(self.target_url)
        ul_pageBrowser = soup.find("ul", {"class": "pageBrowser"})
        try:
            a_nexts = ul_pageBrowser.find_all("a", {"class": "underlined"})
            a_next = a_nexts[1]
        except:
            a_next = ul_pageBrowser.find("a", {"class": "underlined"})

        if a_next is not None and "href" in a_next.attrs:
            next_page_url = a_next["href"]

            if self.before_url != next_page_url:
                print("[ PROCESS ] Next article list page: {}".format(url))
                return next_page_url

        return None

    def crawl(self):

        try:
            while True:
                start = time.time()
                print("[ PROCESS ] Now page {} PROCESSING".format(self.page_count))
                scraper = ResearchBloggingScraper(self.target_url, self.save_dir)
                scraper.scrap()
                self.target_url = self.get_next_page_link(self.target_url)

                if self.target_url is None:
                    break

                self.page_count += 1
                time.sleep(2)
                end = time.time()

                elapsed_sec = end - start
                elapsed_min = elapsed_sec / 60

                if elapsed_min < 1:
                    print("[ TIME ] Elapsed time: {:.2f} [sec]".format(elapsed_sec))
                else:
                    print("[ TIME ] Elapsed time: {:.2f} [min]".format(elapsed_min))

        except Exception as err:
            print("[ EXCEPTION ] Exception occured: {}".format(err))
            traceback.print_tb(err.__traceback__)

            self.save_status()

        return self.FINISH_CRAWL

    def save_status(self):

        status_dict = {}
        status_dict["target_url"] = self.target_url
        status_dict["page_count"] = self.page_count

        with open("status.json", "w") as wf:
            json.dump(status_dict, wf, indent=2)

        print("[ DUMP ] Dump status.json")
