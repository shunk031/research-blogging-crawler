# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from research_blogging.scraper import ResearchBloggingScraper

if __name__ == '__main__':

    RESEARCHBLOGGING_URL = "http://www.researchblogging.org/"
    scraper = ResearchBloggingScraper(RESEARCHBLOGGING_URL, "./dump_files")
    scraper.scrap()
