import argparse
import os
from typing import List
from urllib.parse import urljoin
import requests
import validators
from bs4 import BeautifulSoup
from tqdm import tqdm

parser = argparse.ArgumentParser(description='BASIC SCRAPER IMPLEMENTATION')
parser.add_argument('-scraping-source', type=str, default='websites.txt', metavar='D',
                    help='file or string containing websites path/s')
parser.add_argument('--depth', type=int, default=2, metavar='N', help='scrapper depth')
args = parser.parse_args()


def basic_scraper_run():
    """
    Main scraper function which iterates over the given url/s, extract and save all urls found up to specified depth.
    """
    if validators.url(args.scraping_source):
        url_list = [args.scraping_source]
    elif os.path.isfile(args.scraping_source):
        f = open(args.scraping_source, "r")
        url_list = f.read().splitlines()
    else:
        raise NotImplementedError('Scraping source data is not a valid source option (file/url string)')

    full_urls_list = []
    curr_urls_to_scrap = url_list

    for curr_depth in range(args.depth):
        # Scrap current depth level
        next_urls_to_scrap = []
        for url in tqdm(curr_urls_to_scrap):
            next_urls_to_scrap.extend(get_urls_from_page(url))
        full_urls_list.extend(next_urls_to_scrap)
        print(f'Scraped current depth: {curr_depth + 1} and found {len(next_urls_to_scrap)} urls')

        # In next depth we pass trough the new urls we scraped
        curr_urls_to_scrap = next_urls_to_scrap

    save_results(full_urls_list)


#<a> = anchor, holds hyper link to other websites/files and so on
def get_urls_from_page(page: str) -> List[str]:
    """
    Scrap a given page and extract all urls for that page
    :param page: page to scrap
    :return: list of all urls in this current page
    """
    page_req = requests.get(page).text
    soup = BeautifulSoup(page_req, "html.parser")
    url_list = []
    for element in soup.find_all("a", href=True):
        url = element.get('href')
        url = fix_URL(page, url)
        url_list.append(url)
    return url_list


def save_results(url_list: list) -> None:
    """
    Save all urls that were found in a text file
    :param url_list: list of unique urls found during scraping
    """
    with open("res.txt", "w", encoding="utf-8") as f:
        for url in url_list:
            f.write(url + "\n")

    print("number of links found:" + str(len(url_list)))


def fix_URL(base: str, url: str) -> str:
    """
    Fix url by attaching relative url to base path in order to create absolute url path
    :param base: base web path
    :param url: current url from href
    :return: full fixed url
    """
    if len(url) > 2 and url[0] == "/" and url[1] == "/":
        return "http:" + url
    return urljoin(base, url)


if __name__ == '__main__':
    basic_scraper_run()
