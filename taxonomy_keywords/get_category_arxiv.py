import requests
from bs4 import BeautifulSoup
import random
import os
import logging
import sys
# from expressvpn import wrapper
import json
import urllib.parse


def parse_html_response(html):
    data = []
    parsed_html = BeautifulSoup(html, features="lxml")
    li_list = [li for li in parsed_html.body.find_all('li') if li.text.startswith('astro-ph.')]
    for li in li_list:
        li_dict = {}
        li_id, li_name = li.text.split('\n')[0].split(' - ')
        li_dict["name-category"] = li_name.strip()
        li_dict["id-category"] = li_id.strip()
        t = li.find('div', attrs={'class': "description"})
        if t.text != "":
            t = t.text.strip()
            li_dict["descr-category"] = t + '.' if t[-1] != '.' else t
        else:
            li_dict["descr-category"] = ""
        # print(li_dict)
        data.append(li_dict)
    return data


# function to add to JSON
def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
        logging.info("Json file updated.\n")


if __name__ == '__main__':
    request_url = 'https://arxiv.org/archive/astro-ph'
    response = requests.get(request_url)
    res = parse_html_response(response.text)
    print(json.dumps(res, indent=2))
