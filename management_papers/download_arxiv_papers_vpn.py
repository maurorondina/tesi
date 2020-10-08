import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import os
import logging
import sys
import time
from expressvpn import wrapper

logging.basicConfig(filename='./log_download_pdf_arxiv.txt', level=logging.DEBUG)

def change_ip():
    max_attempts = 10
    attempts = 0
    while True:
        attempts += 1
        try:
            logging.info('GETTING NEW IP')
            wrapper.random_connect()
            logging.info('SUCCESS')
            return
        except Exception as e:
            if attempts > max_attempts:
                logging.error('Max attempts reached for VPN. Check its configuration.')
                logging.error('Program will exit.')
                sys.exit(1)
            logging.error(e)
            logging.error('Skipping exception.')
    
def download_paper(_id, url):
    response = ''
    while response == '':
        try:
            response = requests.get(url)
            if response.status_code == 403:
                logging.error("Exception banned: %s" % str(e))
                change_ip()
                response = ''
                continue
            break
        except Exception as e:
            logging.error("Exception in download: %s" % str(e))
            r = random.randint(3, 6)
            logging.info("Connection refused by the server. Let me sleep for {} seconds.. ZZzzzz...\n".format(r))
            time.sleep(r)
            logging.info("Retrying for paper {} at url {}\n".format(_id, url))
            continue
    return response


if __name__ == '__main__':

    if len(sys.argv) > 2:
        print("Error: too much arguments.\nUsage:\n\tpython download_arxiv_papers_vpn.py [directory_path]\n")
        sys.exit(1)
    elif len(sys.argv) < 2:
        print("Error: missing directory to save papers.\nUsage:\n\tpython download_arxiv_papers_vpn.py [directory_path]\n")
        sys.exit(1)
    else:
        dir_path = sys.argv[1]
        if not os.path.isdir(dir_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython download_arxiv_papers_vpn.py [directory_path]\n" % dir_path)
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
    wrapper.connect()
    count = 0
    # arxiv will block your ip every 500-600 papers approximately.. change your ip every 't_count'
    t_count = random.randint(250, 450)
    for index, row in df.iterrows():
        name_pdf = 'paper_' + str(row['_id']) + '.pdf'
        logging.info("Attempt to download %s:" % name_pdf)
        count += 1
        # Connect expressvpn - Change IP
        if count >= t_count:
            count = 0
            change_ip()
        # Download pdf
        response = download_paper(row['_id'], row['url'])
        if response.status_code == 200:
            # Save PDF
            paper_pdf_path = os.path.join(dir_path, name_pdf)
            with open(paper_pdf_path, 'wb') as f:
                f.write(response.content)
                logging.info("Paper '%s' saved.\n" % name_pdf)
                out_file.write("{}\t\t{}\t\t{}\n".format(row['_id'], row['url'], row['title']))
        else:
            # PDF not saved
            logging.error("Paper %s not saved, and its response is: %s.\n" % (name_pdf, response))

    wrapper.disconnect()
    sys.exit(0)
