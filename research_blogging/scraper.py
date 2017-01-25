# -*- coding: utf-8 -*-

from __future__ import print_function
from bs4 import BeautifulSoup
from readability.readability import Document

import os
import csv

try:
    from urllib.request import urlopen, Request
    from urllib.parse import urljoin, urlencode
    from urllib.error import HTTPError
    from http.client import IncompleteRead
except ImportError:
    from urllib2 import urlopen
    from urllib2 import urljoin
    from urllib2 import HTTPError
    from httplib import IncompleteRead


class ResearchBloggingScraper:

    base_url = "http://www.researchblogging.org/"
    user_agent = "Mozilla/5.0 (Windows U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
    headers = {"User-Agent": user_agent, }

    def __init__(self, target_url, save_dir):
        self.target_url = target_url
        self.save_dir = save_dir

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
                print("[ RETRY ] Waiting {} seconds...".format(wait))
                time.sleep(wait)

    def scrap(self):

        article_detail_url_list = self.get_article_detail_urls()

        article_detail_info = []
        for article_url in article_detail_url_list:
            article_dict = self.get_article_detail_info_dict(article_url)
            article_detail_info.append(article_dict)

        self.save_article_detail_info_list(article_detail_info)

    def get_article_detail_urls(self):

        soup = self._make_soup(self.target_url)

        # 記事概要のそれぞれのデータを取得する
        div_leftCol = soup.find("div", {"id": "leftCol"})

        div_mainArticles = div_leftCol.find_all("div", {"class": "mainArticle"})
        div_mainArticleBottom = div_leftCol.find("div", {"id": "mainArticleBottom"})

        div_main_article_list = [div_mainArticle for div_mainArticle in div_mainArticles]

        div_main_article_list.append(div_mainArticleBottom)

        article_detail_url_list = []
        for div_main_article in div_main_article_list:
            detail_url = div_main_article.find("h1").find("a")
            abs_url = detail_url["href"]
            url = urljoin(self.base_url, abs_url)
            print("[ GET ] Get URL: {}".format(url))

            # ページ構成の都合上、ここでタイトルを取得する。
            title = detail_url.get_text().strip()

            # [(url1, title1), (url2, title2), ]の形でリストに追加していく
            article_detail_url_list.append((url, title))

        return article_detail_url_list

    def get_article_detail_info_dict(self, article_url):

        article_dict = {}
        title = article_url[1].strip()

        url = article_url[0]
        article_dict["url"] = url

        print("[ GET ] Title: {}".format(title))
        article_dict["title"] = title

        try:
            request = Request(url, None, self.headers)

            with urlopen(request) as res:
                attempt = 0
                while attempt < 3:
                    try:
                        html = res.read()
                    except IncompleteRead as e:
                        attempt += 1
                    else:
                        break

            readable_article = Document(html).summary()
            readable_soup = BeautifulSoup(readable_article, "lxml")
            article_dict["article"] = readable_soup.get_text()

        except Exception as e:
            print("{:9}".format("", e))
            article_dict["article"] = None

        return article_dict

    def save_article_detail_info_list(self, article_detail_info_list):

        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        for article_detail_dict in article_detail_info_list:
            article_title = article_detail_dict["title"]
            csv_filename = self._convert_filename(article_title)
            csv_filename = "{}.csv".format(csv_filename)

            with open(os.path.join(self.save_dir, csv_filename), "w") as wf:
                writer = csv.writer(wf)
                writer.writerow([article_detail_dict["title"],
                                 article_detail_dict["url"],
                                 article_detail_dict["article"]])

    def _convert_filename(self, article_title):

        filename = article_title.replace(" ", "_")
        filename = filename.replace("/", "")
        filename = filename.replace("?", "")

        if len(filename) > 250:
            filename = filename[:250]
        return filename
