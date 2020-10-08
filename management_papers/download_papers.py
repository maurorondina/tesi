import pandas as pd
import requests
import os
import multiprocessing
import numpy as np
import sys
import random
import time
import math

#print(pd.__version__)
#print(requests.__version__)


def find_paper(log_file, paper, dir_path):

    response = ''
    while response == '':
        try:
            response = requests.get(paper['url'])
            break
        except requests.exceptions.ConnectionError:
            r = random.randint(3, 6)
            log_file.write("Connection refused by the server. Let me sleep for {} seconds.. ZZzzzz...\n".format(r))
            time.sleep(r)
            log_file.write("Retrying for paper {} at url {}\n".format(paper['_id'], paper['url']))
            continue

    if response.status_code == 200:
        # write/download pdf:
        paper_pdf_path = os.path.join(dir_path, 'paper_' + str(paper['_id']) + '.pdf')
        with open(paper_pdf_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        return False


def work(name, dataset, dir_path):
    print("Start Process %s" % name)
    print("Process %d: total_papers=%d, last_index=%d" % (name, dataset['_id'].count(),
                                                          dataset.index.values.tolist()[-1]))

    # output file:
    out_file = open("./out_"+str(name)+".txt", "w", buffering=1)
    #out_file = open("./out_" + str(name) + ".txt", "a+", buffering=1)
    log_file = open("./log_" + str(name) + ".txt", "w", buffering=1)
    log_file.write("LOG - Process {}:\n".format(name))

    paper_examinated = 0
    paper_requested = 0
    for index, row in dataset.iterrows():
        # print(row['_id'], row['url'], index)
        # sys.stdout.flush()
        if find_paper(log_file, row, dir_path):
            out_file.write("{}\t\t{}\t\t{}\n".format(row['_id'], row['url'], row['title']))
            paper_examinated = paper_examinated + 1
        else:
            log_file.write("Paper {} not saved.\n".format(row['_id']))
        paper_requested = paper_requested + 1
        if paper_requested % 100 == 0:
            log_file.write("Process {} - papers: examinated {} / requested {} "
                           "/ total {}.\n".format(name, paper_examinated, paper_requested, dataset['_id'].count()))

    out_file.close()
    log_file.write("Process {} - papers: examinated {} / requested {} "
                   "/ total {}.\n".format(name, paper_examinated, paper_requested, dataset['_id'].count()))
    log_file.write("Closing Process {} ...\n".format(name))
    log_file.close()



if __name__ == '__main__':

    if len(sys.argv) > 2:
        print("Error: too much arguments.\nUsage:\n\tpython download_papers.py [directory_path]\n")
        sys.exit(1)
    elif len(sys.argv) < 2:
        print("Error: missing directory to save papers.\nUsage:\n\tpython download_papers.py [directory_path]\n")
        sys.exit(1)
    else:
        dir_path = sys.argv[1]
        if not os.path.isdir(dir_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython download_papers.py [directory_path]\n" % dir_path)
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

    # Remove all records of 'arxiv.org'.
    df = df.loc[~df['url'].str.contains('arxiv.org')]
    print("Removing all records of 'arxiv.org' ...")
    print("Papers: {}/{}".format(df['_id'].count(), total_papers))

    # Downloading:
    n = multiprocessing.cpu_count()
    print("Number of cpu : ", n)
    slice_indexes = []
    for i in range(1, n):
        slice_indexes.append(math.trunc(len(df) / n) * i)
    dfs = np.split(df, slice_indexes)
    # Processes instantiated:
    procs = []
    for i in range(0, n):
        proc = multiprocessing.Process(target=work, args=(i + 1, dfs[i], dir_path))
        procs.append(proc)
        time.sleep(random.randrange(5))
        proc.start()
    # Processes completed:
    for proc in procs:
        proc.join()
        print("Process %s complete!" % proc)
