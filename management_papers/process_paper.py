import pathlib
import sys
import os
import re
import xml.etree.ElementTree as ET
import getopt
import logging
from bs4 import BeautifulSoup

from process_paper_utils import *

### EXAMPLES:
### python3 process_paper.py -i 42652 -u http://link.springer.com/content/pdf/10.1007/3-540-44795-4_45.pdf "/Users/maurorondina/Desktop/Tesi - Magistrale/data/papers/paper_42652/paper_42652.xml" "/Users/maurorondina/Desktop/Tesi - Magistrale/data/papers/paper_42652/paper_42652.txt"
### python3 process_paper.py -i 13056 "/Users/maurorondina/Desktop/Tesi - Magistrale/data/papers/paper_13056/paper_13056.xml" "/Users/maurorondina/Desktop/Tesi - Magistrale/data/papers/paper_13056/paper_13056.txt"
### python3 process_paper.py -i 13627 -t "The Power of Interpolation: Understanding the Effectiveness of SGOD in Modern Over-parametrized Learning" "/Users/maurorondina/Desktop/Tesi - Magistrale/data/papers/paper_13627/paper_13627.xml" "/Users/maurorondina/Desktop/Tesi - Magistrale/data/papers/paper_13627/paper_13627.txt"



def error_arguments():
    return 'process_paper.py -i <id_paper> -t <title_paper> -u <url_paper> <xml-file> <txt-file> [out-xml-file]\n' + \
           'Warnings:\n' + \
           '\t1. specify file extensions in arguments (such as .xml and .txt)\n' + \
           '\t2. if the title is not specified with the option -t, it will estimated from the xml.\n' + \
           '\t3. the id must be numeric.\n' + \
           '\nTry again.\n'


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    bs = BeautifulSoup(ET.tostring(elem), 'xml')
    return bs.prettify()


if __name__ == '__main__':

    ## CHECK ARGUMENTS
    xml_file_name = ""
    txt_file_name = ""
    out_xml_file_name = ""
    dir_name = pathlib.Path().absolute()
    id_paper = ""
    title_paper = ""
    url_paper = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:t:u:", ["help", "id-paper=", "title-paper=", "url-paper="])
    except getopt.GetoptError:
        print(error_arguments())
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(error_arguments())
            sys.exit(1)
        elif opt in ("-i", "--id-paper"):
            id_paper = arg
            try:
                val = int(id_paper)
            except ValueError:
                print('Error: id is not a number.\n')
                print(error_arguments())
                sys.exit(1)
        elif opt in ("-t", "--title-paper"):
            title_paper = arg
        elif opt in ("-u", "--url-paper"):
            url_paper = arg

    if len(args) < 2 or len(args) > 3:
        print('Error: error in specifying arguments.\n')
        print(error_arguments())
        sys.exit(1)
    xml_file_name = args[0]
    if str(xml_file_name).endswith('.xml'):
        if not os.path.isfile(xml_file_name):
            print('Error: "%s" not exists in %s .\n' % (xml_file_name, dir_name))
            print(error_arguments())
            sys.exit(1)
    else:
        print('Error: "%s" doesn\'t end with %s .\n' % (xml_file_name, '.xml'))
        print(error_arguments())
        sys.exit(1)

    txt_file_name = args[1]
    if str(txt_file_name).endswith('.txt'):
        if not os.path.isfile(txt_file_name):
            print('Error: "%s" not exists in %s .\n' % (txt_file_name, dir_name))
            print(error_arguments())
            sys.exit(1)
    else:
        print('Error: "%s" doesn\'t end with %s .\n' % (txt_file_name, '.txt'))
        print(error_arguments())
        sys.exit(1)

    if len(args) >= 3:
        out_xml_file_name = args[2]
        if str(out_xml_file_name).startswith('-'):
            out_xml_file_name = ""
        elif not str(txt_file_name).endswith('.xml'):
            print('Error: "%s" doesn\'t end with %s .\n' % (out_xml_file_name, '.xml'))
            print(error_arguments())
            sys.exit(1)
    if out_xml_file_name == "":
        out_xml_file_name = xml_file_name.replace('.xml', '_analyzable.xml')


    ## LOG FILE
    logger = logging.getLogger("Logger-" + id_paper)
    logger.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    file_handler = logging.FileHandler(filename=xml_file_name.replace('.xml', '.log'), mode='w')
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    ## CLEAN XML FOR PROPER ANALYSIS
    tmp_xml_file_name = xml_file_name.replace('.xml', '_tmp.xml')
    with open(xml_file_name, 'r', encoding='latin-1') as infile, open(tmp_xml_file_name, 'w') as tmp_xml_file:
        for line in infile.readlines():
            line = line.replace("<b>", "").replace("<i>", "").replace("</b>", "").replace("</i>", "").replace("</a>", "")
            line = re.sub("<a .+?(>=?)", "", line)
            tmp_xml_file.write(line)

    ## PARSE TEMPORARY XML
    tree = ET.parse(tmp_xml_file_name)
    root = tree.getroot()
    pages = [child for child in root]

    ## GET TITLE
    if title_paper == "":
        title, title_list = get_title(pages[0], logger=logger)
        logger.info("Title estimated for paper %s: '%s'" % (id_paper, title))
        title_paper = title

    ## CHECK IF THE INDEX WAS FOUND
    paragraph_titles_from_index = None
    if pages[-1].tag == "outline":
        outline = pages[-1]
        pages.remove(outline)
        paragraph_titles_from_index = [item for item in outline.iter("item")]
    ## GET PARAGRAPH TITLES
    paragraph_titles = get_paragraph_titles(paragraph_titles_from_index, root, pages,
                                            logger=logger, paper_title=title_paper)
    logger.info("Paragraph titles detected:\n\t- " + "\n\t- ".
                join(list(map(lambda x: x[0].text + ('\tin page: ' + x[1]), paragraph_titles))))

    ## OUT XML
    out_paper_root = ET.Element('paper')
    out_paper_root.attrib = {}
    if id_paper != "":
        out_paper_root.attrib['id'] = id_paper
    if url_paper != "":
        out_paper_root.attrib['url'] = url_paper

    ## PARSE TXT
    with open(txt_file_name, 'r') as txt_file:
        out_paper_root = parse_txt_fw_bw(out_paper_root, txt_file.readlines(), title_paper,
                                         list(map(lambda x: x[0].text, paragraph_titles)),
                                         logger=logger, page_for_title=pages[0])

    if out_paper_root is None:
        logger.critical("Error occurred. Exit..")
        sys.exit(2)

    ## PRINT OUT XML
    with open(out_xml_file_name, 'w') as out_xml_file:
        out_xml_file.write(prettify(out_paper_root))

    sys.exit(0)
