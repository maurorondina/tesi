import os
import logging
import re

logging.basicConfig(filename='./log_categorized_papers.log', level=logging.DEBUG)


if __name__ == '__main__':

    # GENERATE A LIST OF ARXIV PAPERS CONTAINING THE WORDS: "CCS CONCEPTS", "KEYWORDS", "INDEX TERMS", "CONTENT AREAS"
    paper_list = "../data/LIST_PAPERS.txt"
    paper_line_list = []
    with open(paper_list, 'r') as in_file:
        paper_line_list = in_file.readlines()

    data_dir = "../data/papers"
    out_file_1 = "./resources/LIST_PAPERS_keywords.txt"

    with open(out_file_1, "w") as out_1:
        for paper_line in paper_line_list:
            info_paper = paper_line.split("\t\t")
            if 'arxiv.org' in info_paper[1]:
                path_dir = os.path.join(data_dir, "paper_" + info_paper[0])
                if os.path.isdir(path_dir):
                    # if not os.path.isfile(os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable.xml")):
                    #     #logging.info('Paper "%s" is not processed.' % (info_paper[0]))
                    #     continue
                    txt_path = os.path.join(path_dir, "paper_" + info_paper[0] + ".txt")
                    if os.path.isfile(txt_path):
                        with open(txt_path, "r") as txt_f:
                            text = txt_f.read()
                            found_ccs = re.search("ccs\s+concepts", text, re.IGNORECASE)
                            found_keyw = re.search("keywords|key\s?word(s)?:", text, re.IGNORECASE)
                            found_ind_term = re.search("index\s+terms", text, re.IGNORECASE)
                            found_areas = re.search("content\s+areas:", text, re.IGNORECASE)
                            line = ''
                            if found_ccs is not None and found_ccs.group() != found_ccs.group().lower() and found_ccs.span()[0] < 10000:
                                line = line + '\t/\t' + found_ccs.group() + " - " + str(found_ccs.span())
                            if found_keyw is not None and found_keyw.group() != found_keyw.group().lower() and found_keyw.span()[0] < 10000:
                                line = line + '\t/\t' + found_keyw.group() + " - " + str(found_keyw.span())
                            if found_ind_term is not None and found_ind_term.group() != found_ind_term.group().lower() and found_ind_term.span()[0] < 10000:
                                line = line + '\t/\t' + found_ind_term.group() + " - " + str(found_ind_term.span())
                            if found_areas is not None and found_areas.group() != found_areas.group().lower() and found_areas.span()[0] < 10000:
                                line = line + '\t/\t' + found_areas.group() + " - " + str(found_areas.span())
                            if line != '':
                                out_1.write(info_paper[0] + line + '\n')
                    else:
                        logging.error('File TXT "%s" for paper %s not found.' % (txt_path, info_paper[0]))
                else:
                    logging.error('Directory "%s" for paper %s not found.' % (path_dir, info_paper[0]))
