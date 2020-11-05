import requests
from bs4 import BeautifulSoup
import random
import os
import logging
import sys
from expressvpn import wrapper
import json
import urllib.parse
import time

logging.basicConfig(filename='./log_download_info_arxiv.log', level=logging.DEBUG)

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


def get_id_arxiv(url_pdf):
    # e.g.
    # https://arxiv.org/pdf/1606.07419.pdf
    # https://arxiv.org/pdf/1301.3764
    # https://arxiv.org/pdf/1502.02127v2
    # https://arxiv.org/pdf/quant-ph/0011122v2
    id_arxiv = url_pdf[url_pdf.rfind('pdf/')+len('pdf/'):]
    if '.pdf' in id_arxiv:
        id_arxiv = id_arxiv[:id_arxiv.find('.pdf')]
    # elif 'v' in id_arxiv:
    #     id_arxiv = id_arxiv[:id_arxiv.find('v')]
    return id_arxiv.strip()


# def encode_request_url_by_title(title):
#     title = title.replace('?', '')
#     #url_dict = {'query': urllib.parse.quote_plus(title), 'searchtype': 'title', 'source': 'header'}
#     url_dict = {'query': title, 'searchtype': 'title', 'source': 'header'}
#     return urllib.parse.urlencode(url_dict)


def encode_request_url_by_arxiv_id(arxiv_id):
    url_dict = {'query': arxiv_id, 'searchtype': 'paper_id', 'source': 'header'}
    return urllib.parse.urlencode(url_dict)


def parse_html_response(html):
    parsed_html = BeautifulSoup(html, features="html.parser")  #"html.parser" "lxml"
    info_dict = {}
    info_dict["title"] = parsed_html.body.find('h1', attrs={'class': "title mathjax"}).text.split('Title:')[1]
    info_dict["authors"] = [a.strip() for a in parsed_html.body.find('div', attrs={'class': "authors"}).text.split('Authors:')[1].split(',')]
    info_dict["abstract"] = parsed_html.body.find('blockquote', attrs={'class': "abstract mathjax"}).text.split('Abstract:')[1].replace('\n', ' ').strip()
    return info_dict


def download_info(paper_id, url_pdf):
    id_arxiv = get_id_arxiv(url_pdf)
    request_url = 'https://arxiv.org/search/?' + encode_request_url_by_arxiv_id(id_arxiv)

    response = ''
    while response == '':
        try:
            response = requests.get(request_url)
            if response.status_code == 403:
                logging.error("Exception banned.")
                change_ip()
                response = ''
                continue
            break
        except Exception as e:
            logging.error("Exception in response for paper '%s': %s" % (paper_id, str(e)))
            r = random.randint(3, 6)
            logging.info("Connection refused by the server. Let me sleep for {} seconds.. ZZzzzz...\n".format(r))
            time.sleep(r)
            logging.info("Retrying for paper {} with url {}\n".format(paper_id, request_url))
            response = ''
            continue

    if response.status_code == 200:
        return parse_html_response(response.text)
    else:
        # Response error
        logging.error("Info not saved for paper '%s', and its response is: %s.\n" % (paper_id, response))

    return None


# function to add to JSON
def write_json(data, filename):
    with open(filename,'w') as f:
        json.dump(data, f)
        logging.info("Json file write.\n")

# function to add to JSON
def append_json(data, filename):
    with open(filename, 'rb+') as filehandle:
        filehandle.seek(-2, os.SEEK_END)
        filehandle.truncate()
    json_data = json.dumps(data)
    json_data = json_data[json_data.find('[') + 1:]
    with open(filename,'a+') as f:
        f.write(', ' + json_data) #+ ']}')
        logging.info("Json file updated.\n")


if __name__ == '__main__':

    if len(sys.argv) > 3:
        print("Error: too much arguments.\nUsage:\n"
              "\tpython get_info_arxiv_papers_vpn.py [directory_path_pdf] [papers_to_get_info_list.txt]\n")
        sys.exit(1)
    elif len(sys.argv) < 3:
        print("Error: missing arguments.\nUsage:\n"
              "\tpython get_info_arxiv_papers_vpn.py [directory_path_pdf] [papers_to_get_info_list.txt]\n")
        sys.exit(1)
    else:
        dir_pdf_path = sys.argv[1]
        if not os.path.isdir(dir_pdf_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython get_info_arxiv_papers_vpn.py [directory_path_pdf]"
                  " [papers_to_get_info_list.txt]\n" % dir_pdf_path)
            sys.exit(2)
        papers_list_path = sys.argv[2]
        if not os.path.isfile(papers_list_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython get_info_arxiv_papers_vpn.py [directory_path_pdf]"
                  " [papers_to_get_info_list.txt]\n" % papers_list_path)
            sys.exit(2)


    # out file
    outfile = './resources/papers_info.json'
    wrapper.connect()
    papers_info = {'papers': []}
    count = 0
    # arxiv will block your ip every 500-600 paper requests approximately.. change your ip every 't_count'
    t_count = random.randint(300, 400)
    update_count = 0

    with open(papers_list_path, 'r') as paper_list_file:

        while True:
            # Get next line from file
            line = paper_list_file.readline()
            # if line is empty, end of file is reached
            if line == "":
                logging.info("EOF reached. Bye...\n")
                break
            # Processing line: _id , url , title
            info_paper = line.split("\t\t")
            name_pdf = 'paper_' + info_paper[0] + '.pdf'
            # Check if paper pdf is downloaded
            paper_pdf_path = os.path.join(dir_pdf_path, name_pdf)
            if not os.path.isfile(paper_pdf_path):
                logging.error("Paper '%s': not found in directory %s.\n" % (name_pdf, dir_pdf_path))
                continue

            # Request
            count += 1
            # Connect expressvpn - Change IP ; update json_file
            if count > t_count:
                append_json(papers_info, outfile) if update_count > 0 else write_json(papers_info, outfile)
                update_count += 1
                print("Update %s: paper stored = %s - %s."
                      % (update_count, t_count, time.strftime("%H:%M:%S", time.localtime())))
                papers_info = {'papers': []}
                count = 1
                t_count = random.randint(300, 400)
                change_ip()
            print(time.strftime("%H:%M:%S", time.localtime()), "- %s/%s - '%s'" %(count, t_count, info_paper[0]))
            logging.info("Attempt to request info for paper '%s':" % info_paper[0])
            info_dict = download_info(info_paper[0], info_paper[1])
            if info_dict is None:
                logging.warning("NO info downloaded for paper '%s'.\n" % info_paper[0])
            else:
                # Add info for the paper
                info_dict['id'] = info_paper[0]
                papers_info['papers'].append(info_dict)
                logging.info("Info stored for paper '%s'.\n" % info_paper[0])

    append_json(papers_info, outfile)
    wrapper.disconnect()
    sys.exit(0)
