from builtins import *
from pprint import pprint as pp
import os
import sys
import logging
import pdfminer
import json
import pdfquery
import string


logging.basicConfig(filename='./log_extract_keywords_papers.log', level=logging.WARNING)


# function to add to JSON
def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
        logging.info("Json file write.\n")


# function to add to JSON
def append_json(data, filename):
    with open(filename, 'rb+') as filehandle:
        filehandle.seek(-2, os.SEEK_END)
        filehandle.truncate()
    json_data = json.dumps(data)
    json_data = json_data[json_data.find('[') + 1:]
    with open(filename, 'a+') as f:
        f.write(', ' + json_data)  # + ']}')
        logging.info("Json file updated.\n")


if __name__ == '__main__':

    if len(sys.argv) > 3:
        print("Error: too much arguments.\nUsage:\n"
              "\tpython extract_keywords.py [directory_path_pdf] [papers_to_extract_keywords_list.txt]\n")
        sys.exit(1)
    elif len(sys.argv) < 3:
        print("Error: missing arguments.\nUsage:\n"
              "\tpython extract_keywords.py [directory_path_pdf] [papers_to_extract_keywords_list.txt]\n")
        sys.exit(1)
    else:
        dir_pdf_path = sys.argv[1]
        if not os.path.isdir(dir_pdf_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython extract_keywords.py [directory_path_pdf]"
                  " [papers_to_extract_keywords_list.txt]\n" % dir_pdf_path)
            sys.exit(2)
        papers_list_path = sys.argv[2]
        if not os.path.isfile(papers_list_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython extract_keywords.py [directory_path_pdf]"
                  " [papers_to_extract_keywords_list.txt]\n" % papers_list_path)
            sys.exit(2)

    outfile = './resources/papers_keywords.json'
    data = {'papers': []}

    with open(papers_list_path, 'r') as paper_list_file:

        while True:
            # Get next line from file
            line = paper_list_file.readline()
            # if line is empty, end of file is reached
            if line == "":
                logging.info("EOF reached. Bye...\n")
                break
            # Processing line: _id , relevant words
            info_paper = line.split("/")
            paper_id = info_paper[0].strip()
            name_pdf = 'paper_' + paper_id + '.pdf'
            # Check if paper pdf is downloaded
            paper_pdf_path = os.path.join(dir_pdf_path, name_pdf)
            if not os.path.isfile(paper_pdf_path):
                logging.error("Paper '%s': not found in directory %s.\n" % (name_pdf, dir_pdf_path))
                continue

            paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
            # print(paper_id, ':\t', paper_words)

            try:
                pdf = pdfquery.PDFQuery(paper_pdf_path)
                pdf.load([0])
                # pdf.tree.write("./test.xml", pretty_print=True, encoding="utf-8")

                paper_keyword_dict = {'id': paper_id}
                for word, pos in paper_words:
                    # "CCS CONCEPTS", "KEYWORDS", "INDEX TERMS", "CONTENT AREAS"
                    word_tmp = word.replace(" ", "").replace(":", "").lower()
                    if word_tmp in 'keywords' or word_tmp == 'indexterms':
                        paper_keyword_dict['keywords'] = None
                        word_tmp = 'keywords'
                    else:
                        paper_keyword_dict[word_tmp] = None
                    # search in pdf:
                    res = pdf.extract([(word_tmp, ':contains("' + word + '")',)])
                    print(paper_id, '---->', res)
                    for box in res[word_tmp]:
                        if pdfminer.layout.LTTextBoxHorizontal == type(box.layout):
                            paper_keyword_dict[word_tmp] = "".join(list(map(lambda x: x[:-1] if x[-1] == '-' else x,
                                                                            [box_text.strip() for box_text in
                                                                             box.itertext() if
                                                                             box_text.strip() != ""])))
                            # manage text
                            if paper_keyword_dict[word_tmp].startswith(word):
                                paper_keyword_dict[word_tmp] = paper_keyword_dict[word_tmp][len(word):]
                                if paper_keyword_dict[word_tmp].startswith(':') or paper_keyword_dict[
                                    word_tmp].startswith('—'):
                                    paper_keyword_dict[word_tmp] = paper_keyword_dict[word_tmp][1:].strip()
                                # separation
                                if word_tmp == 'ccsconcepts':
                                    paper_keyword_dict[word_tmp] = [k.strip() for k in
                                                                    paper_keyword_dict[word_tmp].split('•') if
                                                                    k.strip() != ""]
                                else:
                                    punctuation_dict = {s: 0 for s in list(string.punctuation)}
                                    for s in list(paper_keyword_dict[word_tmp]):
                                        if s in punctuation_dict.keys(): punctuation_dict[s] += 1
                                    max_punctuation = max(punctuation_dict, key=punctuation_dict.get)
                                    if punctuation_dict[max_punctuation] == 0:
                                        logging.warning('No separator found in "%s" for paper "%s".' % (word, paper_id))
                                    else:
                                        paper_keyword_dict[word_tmp] = [k.strip() for k in
                                                                        paper_keyword_dict[word_tmp].split(
                                                                            max_punctuation)
                                                                        if k.strip() != ""]

                            else:
                                logging.error('Text for paper "%s" doesn\'t start with "%s":\t%s' % (
                                paper_id, word, paper_keyword_dict[word_tmp]))
                                paper_keyword_dict[word_tmp] = ""
                    if word_tmp in paper_keyword_dict and paper_keyword_dict[word_tmp] is None:
                        logging.error('"%s" for paper "%s" not found.' % (word, paper_id))
                        paper_keyword_dict[word_tmp] = ""

                # pp(paper_keyword_dict)
                if len(paper_keyword_dict.keys()) == 1 and 'id' in paper_keyword_dict:
                    logging.warning('Dict for paper "%s" not append.' % paper_id)
                else:
                    data['papers'].append(paper_keyword_dict)

            except Exception as e:
                with open(outfile, 'w') as f:
                    json.dump(data, f, indent='\t')
                logging.warning('Json wrote. Exception at paper "%s": %s' % (paper_id, e))

    with open(outfile, 'w') as f:
        json.dump(data, f, indent='\t')
