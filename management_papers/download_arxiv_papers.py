import pandas as pd
import requests
from bs4 import BeautifulSoup
from random import choice
import os
import logging
import sys

logging.basicConfig(filename='./log_download_pdf_arxiv.txt', level=logging.DEBUG)


def get_proxy_list():
    url = "https://www.sslproxies.org/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    ip_port_list = list(
        zip(map(lambda x: x.text, soup.findAll('td')[::8]), map(lambda x: x.text, soup.findAll('td')[1::8])))
    ip_port_list = list(map(lambda x: x[0] + ':' + x[1], ip_port_list))
    ip_port_list = list(filter(lambda x: '.' in x and ':' in x, ip_port_list))
    return ip_port_list


def get_proxy():
    url = "https://www.sslproxies.org/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    ip_port_list = list(
        zip(map(lambda x: x.text, soup.findAll('td')[::8]), map(lambda x: x.text, soup.findAll('td')[1::8])))
    ip_port_list = list(map(lambda x: x[0] + ':' + x[1], ip_port_list))
    ip_port_list = list(filter(lambda x: '.' in x and ':' in x, ip_port_list))
    return {'https': choice(ip_port_list)}


def proxy_request(request_type, url, proxy=None, **kwargs):
    error = False
    while 1:
        try:
            attempt_proxy = get_proxy() if proxy is None or error is True else proxy
            logging.info("Using proxy: {}".format(attempt_proxy))
            r = requests.request(request_type, url, proxies=attempt_proxy, timeout=5, **kwargs)
            break
        except Exception as e:
            logging.error("Exception raised with proxy %s: %s" % (attempt_proxy, str(e)))
            error = True
            pass
    return r, attempt_proxy


if __name__ == '__main__':

    if len(sys.argv) > 2:
        print("Error: too much arguments.\nUsage:\n\tpython download_arxiv_papers.py [directory_path]\n")
        sys.exit(1)
    elif len(sys.argv) < 2:
        print("Error: missing directory to save papers.\nUsage:\n\tpython download_arxiv_papers.py [directory_path]\n")
        sys.exit(1)
    else:
        dir_path = sys.argv[1]
        if not os.path.isdir(dir_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython download_arxiv_papers.py [directory_path]\n" % dir_path)
            sys.exit(2)

    # Load data set.
    name_csv = '../data/papers.csv'
    df = pd.read_csv(name_csv, sep=',', low_memory=False)
    total_papers = df['_id'].count()
    print("Total papers: %d" % total_papers)

    # Remove all records which don't contain the url.
    df = df.dropna(axis=0, subset=['url'])
    print("Removing all records which don't contain the url ...")
    print("Papers: {}/{}".format(df['_id'].count(), total_papers))

    # Remove all records which don't contain 'pdf' in url. (INDIRECT LINKS)
    df = df.loc[df['url'].str.contains('pdf')]
    print("Removing all records with indirect links ...")
    print("Papers: {}/{}".format(df['_id'].count(), total_papers))

    # Select records of 'arxiv.org'.
    df = df.loc[df['url'].str.contains('arxiv.org')]
    print("Selecting records of 'arxiv.org' ...")
    print("Papers: {}/{}".format(df['_id'].count(), total_papers))

    # output file:
    out_file = open("./out_arxiv.txt", "w", buffering=1)

    # Downloading:
    current_proxy = None
    for index, row in df.iterrows():
        name_pdf = 'paper_' + str(row['_id']) + '.pdf'
        logging.info("Attempt to download %s:" % name_pdf)
        # Chose proxy
        response, proxy = proxy_request('get', row['url'], proxy=current_proxy)
        if response.status_code == 200:
            # Save PDF
            paper_pdf_path = os.path.join(dir_path, name_pdf)
            with open(paper_pdf_path, 'wb') as f:
                f.write(response.content)
                logging.info("Paper '%s' saved.\n" % name_pdf)
                out_file.write("{}\t\t{}\t\t{}\n".format(row['_id'], row['url'], row['title']))
            # Save the current proxy (because it's working)
            current_proxy = proxy
        else:
            # PDF not saved
            logging.error("Paper '%s' not saved, and its response is: %s.\n" % (name_pdf, response))
            # Forget the proxy
            current_proxy = None

    out_file.close()

    sys.exit(0)
