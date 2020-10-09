import os
import subprocess
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import logging
import pandas as pd
import numpy as np
import pickle

logging.basicConfig(filename='./log_analyzable_papers.log', level=logging.DEBUG)


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    bs = BeautifulSoup(ET.tostring(elem), 'xml')
    return bs.prettify()


def get_adjacent_id(_id, direction="forward"):
    current_value = _id.split(sep='.')[-1]
    offset = int(current_value) + 1 if direction == "forward" else int(current_value) - 1
    return _id[:-len(current_value)] + str(offset)


def label_adjacent_subsection(subsection, root, direction="forward"):
    next_subsection_id = get_adjacent_id(subsection.attrib['id'], "forward" if direction == "forward" else "previous")
    next_subsection = root.find(".//subsection[@id='" + next_subsection_id + "']")
    if next_subsection is None:
        logging.debug("Subsection with id=%s not labelled, because not exist." % next_subsection_id)
        return None, root
    else:
        next_subsection.attrib['label'] = "Problem"
        logging.info("Subsection with id=%s labelled." % next_subsection_id)
        return next_subsection, root


def label_subsections_problem_description(root):
    # 1- check paragraphs with name: "problem description" or "problem statement"
    out_root = root
    found_paragraphs = list(filter(lambda x: "problem description" in x.attrib['name'].lower() or
                                             "problem statement" in x.attrib['name'].lower(),
                                   out_root.findall("./paragraph")))
    if len(found_paragraphs) > 0:
        for paragraph in found_paragraphs:
            found_subsections = paragraph.findall("./subsection")
            for subsection in found_subsections:
                subsection.attrib['label'] = "Problem"
                logging.info("Subsection with id=%s labelled." % subsection.attrib['id'])
        return out_root

    # 2- find subsections with "problem description" or "problem statement" in text
    out_root = root
    found_subsections = list(filter(lambda x: "problem description" in x.text.lower() or
                                              "problem statement" in x.text.lower(),
                                    out_root.findall(".//subsection")))
    if len(found_subsections) > 0:
        for subsection in found_subsections:
            # exclude subsections in paragraph "References" and in index and subsections with -1 in id
            if '.-1.' in subsection.attrib['id']:
                logging.debug("Subsection with id=%s not labelled, because it's out of paragraph."
                              % subsection.attrib['id'])
                continue
            elif ("problem description" or "problem statement") and "....." in subsection.text:
                logging.debug("Subsection with id=%s not labelled, because it's in index." % subsection.attrib['id'])
                continue
            else:
                paragraph_id = subsection.attrib['id'][:subsection.attrib['id'].rfind('.')]
                paragraph = out_root.find("./paragraph[@id='" + paragraph_id + "']")
                if paragraph is None:
                    logging.error("Paragraph with expected id=%s not found." % paragraph_id)
                else:
                    if 'reference' in paragraph.attrib['name'].lower():
                        logging.debug("Subsection with id=%s not labelled, because in paragraph '%s'."
                                      % (subsection.attrib['id'], paragraph.attrib['name']))
                        continue
            # subsections with "problem description" or "problem statement" as word in text only
            if "problem description" in subsection.text or "problem statement" in subsection.text:
                subsection.attrib['label'] = "Problem"
                logging.info("Subsection with id=%s labelled." % subsection.attrib['id'])
                _, out_root = label_adjacent_subsection(subsection, out_root)
                _, out_root = label_adjacent_subsection(subsection, out_root, "previous")
            else:  # (sub)subsections with "problem description" or "problem statement"
                subsection.attrib['label'] = "Problem"
                logging.info("Subsection with id=%s labelled." % subsection.attrib['id'])
                next_subsection, out_root = label_adjacent_subsection(subsection, out_root)
                if next_subsection is not None:
                    next_subsection, out_root = label_adjacent_subsection(next_subsection, out_root)
                    if next_subsection is not None:
                        _, out_root = label_adjacent_subsection(next_subsection, out_root)
        return out_root

    return None



if __name__ == '__main__':

    ###################################################################################################################
    ########## GENERATE TWO LISTS OF PAPERS: PROCESSED AND NOT PROCESSED. (if you need)
    # paper_list = "../data/LIST_PAPERS.txt"
    # paper_line_list = []
    # with open(paper_list, 'r') as in_file:
    #     paper_line_list = in_file.readlines()
    #
    # data_dir = "../data/papers"
    # out_file_1 = "./papers_processed.txt"
    # out_file_2 = "./papers_not_processed.txt"
    #
    # with open(out_file_1, "w") as out_1, open(out_file_2, "w") as out_2:
    #     for paper_line in paper_line_list:
    #         info_paper = paper_line.split("\t\t")
    #         path_dir = os.path.join(data_dir, "paper_" + info_paper[0])
    #         if os.path.isdir(path_dir):
    #             if os.path.isfile(os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable.xml")):
    #                 out_1.write(paper_line)
    #             else:
    #                 out_2.write(paper_line)
    #         else:
    #             logging.error('Directory "%s" for paper %s not found.' % (path_dir, info_paper[0]))
    ###################################################################################################################

    ###################################################################################################################
    ########## GENERATE A LIST OF PROCESSED PAPERS CONTAINING THE WORDS: "problem description", "problem statement".
    # paper_list = "../data/LIST_PAPERS.txt"
    # paper_line_list = []
    # with open(paper_list, 'r') as in_file:
    #     paper_line_list = in_file.readlines()
    #
    # data_dir = "../data/papers"
    # out_file_1 = "../data/LIST_PAPERS_[problem description,problem statement].txt"
    #
    # with open(out_file_1, "w") as out_1:
    #     for paper_line in paper_line_list:
    #         info_paper = paper_line.split("\t\t")
    #         path_dir = os.path.join(data_dir, "paper_" + info_paper[0])
    #         if os.path.isdir(path_dir):
    #             if not os.path.isfile(os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable.xml")):
    #                 logging.error('Paper "%s" is not processed.' % (info_paper[0]))
    #                 continue
    #             txt_path = os.path.join(path_dir, "paper_" + info_paper[0] + ".txt")
    #             if os.path.isfile(txt_path):
    #                 with open(txt_path, "r") as txt_f:
    #                     text = txt_f.read().lower()
    #                     if "problem description" in text or "problem statement" in text:
    #                         out_1.write(paper_line)
    #             else:
    #                 logging.error('File TXT "%s" for paper %s not found.' % (txt_path, info_paper[0]))
    #         else:
    #             logging.error('Directory "%s" for paper %s not found.' % (path_dir, info_paper[0]))
    ###################################################################################################################

    ###################################################################################################################
    ########## LABELING SUBSECTIONS FOR TRAINING SET:
    # paper_list = "../data/LIST_PAPERS_[problem description,problem statement].txt"
    # paper_line_list = []
    # with open(paper_list, 'r') as in_file:
    #     paper_line_list = in_file.readlines()
    #
    # data_dir = "../data/papers"
    # for paper_line in paper_line_list:
    #     info_paper = paper_line.split("\t\t")
    #     path_dir = os.path.join(data_dir, "paper_" + info_paper[0])
    #     if os.path.isdir(path_dir):
    #         analyzable_paper_path = os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable.xml")
    #         if os.path.isfile(analyzable_paper_path):
    #             # 1- parse xml
    #             tree = ET.parse(analyzable_paper_path)
    #             root = tree.getroot()
    #             # 2- label subsections
    #             out_root = label_subsections_problem_description(root)
    #             if out_root is None:
    #                 logging.warning("Paper %s not labelled for train." % info_paper[0])
    #             else:  # - print analyzable train xml
    #                 ##to "unescape" special characters xml
    #                 # unescaped = html.unescape(str(ET.tostring(out_paper_root))); print(unescaped)
    #                 analyzable_train_paper_path = analyzable_paper_path.replace("_analyzable.xml",
    #                                                                             "_analyzable_train.xml")
    #                 with open(analyzable_train_paper_path, 'w') as analyzable_train_paper:
    #                     analyzable_train_paper.write(prettify(out_root))
    ###################################################################################################################

    ###################################################################################################################
    ########## CREATE A TRAINING SET:
    # paper_list = "../data/LIST_PAPERS_[problem description,problem statement].txt"
    # paper_line_list = []
    # with open(paper_list, 'r') as in_file:
    #     paper_line_list = in_file.readlines()
    #
    # data_dir = "../data/papers"
    # df = pd.DataFrame(columns=["id_subsection", "paragraph_name", "text_subsection", "label_subsection"])
    # for paper_line in paper_line_list:
    #     info_paper = paper_line.split("\t\t")
    #     path_dir = os.path.join(data_dir, "paper_" + info_paper[0])
    #     if os.path.isdir(path_dir):
    #         analyzable_paper_path = os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable_train.xml")
    #         if os.path.isfile(analyzable_paper_path):
    #             # 1- parse xml
    #             tree = ET.parse(analyzable_paper_path)
    #             root = tree.getroot()
    #             # 2- get all subsections
    #             found_subsections = root.findall('.//subsection')
    #             for subsection in found_subsections:
    #                 if '.-1.' in subsection.attrib['id']:
    #                     continue
    #                 else:
    #                     paragraph_id = subsection.attrib['id'][:subsection.attrib['id'].rfind('.')]
    #                     paragraph = root.find("./paragraph[@id='" + paragraph_id + "']")
    #                     if paragraph is None or 'reference' in paragraph.attrib['name'].lower():
    #                         continue
    #                     # add to dataset
    #                     df = df.append({"id_subsection": subsection.attrib['id'],
    #                                     "paragraph_name": paragraph.attrib['name'],
    #                                     "text_subsection": subsection.text,
    #                                     "label_subsection": "PD" if "label" in subsection.attrib and
    #                                                                 subsection.attrib["label"] == "Problem" else "N_PD"
    #                                     }, ignore_index=True)
    # print(df)
    # dataset_path = "../data/training_set.pkl"
    # df.to_pickle(dataset_path)  # to save it
    ##df = pd.read_pickle(dataset_path)   # to read it
    ###################################################################################################################

    ###################################################################################################################
    ########## CREATE A TEST SET:
    # testset_list = "../data/testset_list.txt"
    # paper_line_list = []
    # with open(testset_list, 'r') as in_file:
    #    paper_line_list = in_file.readlines()
    #
    # data_dir = "../data/papers"
    # df_test = pd.DataFrame(columns=["id_subsection", "paragraph_name", "text_subsection", "label_subsection"])
    # for paper_line in paper_line_list:
    #    info_paper = paper_line.split("\t\t")
    #    path_dir = os.path.join(data_dir, "paper_" + info_paper[0])
    #    if os.path.isdir(path_dir):
    #        analyzable_test_paper_path = os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable_test.xml")
    #        #analyzable_paper_path = os.path.join(path_dir, "paper_" + info_paper[0] + "_analyzable.xml")
    #        if os.path.exists(analyzable_test_paper_path) #and os.path.exists(analyzable_paper_path):
    #        ##if os.path.exists(analyzable_paper_path):
    #            # 1- parse xml
    #            tree = ET.parse(analyzable_test_paper_path)
    #            ##tree = ET.parse(analyzable_paper_path)
    #            root = tree.getroot()
    #            # 2- get all subsections
    #            found_subsections = root.findall('.//subsection')
    #            for subsection in found_subsections:
    #                if '.-1.' in subsection.attrib['id']:
    #                    continue
    #                else:
    #                    paragraph_id = subsection.attrib['id'][:subsection.attrib['id'].rfind('.')]
    #                    paragraph = root.find("./paragraph[@id='" + paragraph_id + "']")
    #                    if paragraph is None or 'reference' in paragraph.attrib['name'].lower():
    #                        continue
    #                    # add to dataset
    #                    df_test = df_test.append({"id_subsection": subsection.attrib['id'],
    #                                            "paragraph_name": paragraph.attrib['name'],
    #                                            "text_subsection": subsection.text,
    #                                            "label_subsection": np.nan
    #                                            }, ignore_index=True)
    # print(df_test)
    # dataset_path = "../data/test_set.pkl"
    # df_test.to_pickle(dataset_path)  # to save it
    # #df_test = pd.read_pickle(dataset_path)   # to read it
    ###################################################################################################################