# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from research_blogging.crawler import ResearchBloggingCrawler

if __name__ == '__main__':

    RESEARCHBLOGGING_URL = "http://www.researchblogging.org/"
    crawler = ResearchBloggingCrawler(RESEARCHBLOGGING_URL, "./dump_files")
    crawler.crawl()
