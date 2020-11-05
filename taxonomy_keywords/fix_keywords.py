import json
import sys
import os
import xml.etree.ElementTree as ET

if __name__ == '__main__':

    ##################################################
    # # 'paper_keywords_r.json' is a copy of 'paper_keywords.json' with the correct paper keywords and/or CCS CONCEPTS
    # # up to the paper 68199; the information of papers with an id greater than 68199 was not checked
    # # 'papers_keywords_r_out.json' is the out_file with the information correctly restructured
    # in_file = './resources/papers_keywords_r.json'
    # out_file = './resources/papers_keywords_r_out.json'
    # #max_id = 68199
    #
    # data = {}
    # with open(in_file, 'r') as f:
    #     data = json.load(f)
    #
    # for paper in data['papers']:
    #     #if int(paper['id']) <= max_id:
    #     try:
    #         if 'keywords' in paper.keys():
    #             if type(paper['keywords']) == list and len(paper['keywords']) == 1:
    #                 paper['keywords'] = [k.strip() for k in paper['keywords'][0].split(',') if k.strip() != '']
    #             elif type(paper['keywords']) == str:
    #                 paper['keywords'] = [k.strip() for k in paper['keywords'].split(',') if k.strip() != '']
    #             # print(paper['keywords'])
    #     except Exception as e:
    #         print(paper['id'], ":\t", str(e))
    #
    # with open(out_file, 'w') as f:
    #     json.dump(data, f, indent='\t')
    ##################################################

    ##################################################
    # # 'papers_keywords_r_out.json' is the file with all the information correctly restructured
    # # 'papers_keywords_OK.json' is the out_file with papers until 68199, because they've checked information
    # in_file = './resources/papers_keywords_r_out.json'
    # out_file = './resources/papers_keywords_OK.json'
    #
    # max_id = 68199
    #
    # data = {}
    # with open(in_file, 'r') as f:
    #     data = json.load(f)
    #
    # data_ok = {'papers': []}
    # for paper in data['papers']:
    #     if int(paper['id']) <= max_id:
    #         data_ok["papers"].append(paper)
    ##################################################

    ##################################################
    # # 'papers_keywords_r_out.json' is the file with all the information correctly restructured
    # # 'papers_keywords_point.json' is the out_file with the last keyword followed by a period
    # in_file = './resources/papers_keywords_r_out.json'
    # out_file = './resources/papers_keywords_point.json'
    #
    # min_id = 68199
    #
    # data = {}
    # with open(in_file, 'r') as f:
    #     data = json.load(f)
    #
    # data_ok = {'papers': []}
    # for paper in data['papers']:
    #     if int(paper['id']) > min_id:
    #         try:
    #             if 'keywords' in paper.keys() \
    #                     and type(paper['keywords']) == list and len(paper['keywords']) > 0 \
    #                     and paper['keywords'][-1].strip()[-1] == '.':
    #                 data_ok["papers"].append(paper)
    #         except Exception as e:
    #             print("%s: %s" % (paper['id'], e))
    ##################################################

    ##################################################
    # # all papers in 'papers_keywords_point.json' have been checked
    # # to merge papers in 'papers_keywords_point.json' and 'papers_keywords_OK.json'
    # ok_file = './resources/papers_keywords_OK.json'
    # merge_to_ok = './resources/papers_keywords_point.json'
    # out_file = './resources/papers_keywords_OK.json'
    #
    # data_ok = {}
    # with open(ok_file, 'r') as f:
    #     data_ok = json.load(f)
    #
    # with open(merge_to_ok, 'r') as f:
    #     data_tmp = json.load(f)
    #     data_ok['papers'].extend(data_tmp['papers'])
    #
    # print("Papers OK: %s" % len(data_ok['papers']))
    # with open(out_file, 'w') as f:
    #     json.dump(data_ok, f, indent='\t')
    ##################################################

    ##################################################
    # # 'papers_keywords_r_out.json' contains all papers
    # # 'papers_keywords_OK.json' contains only papers checked
    # # 'papers_keywords_remain.json' is the out_file with the papers in 'papers_keywords_r_out.json',
    # # not in 'papers_keywords_OK.json' and the remaining in 'LIST_PAPERS_categorized.txt'
    # ok_file = './resources/papers_keywords_OK.json'
    # paper_list = './resources/LIST_PAPERS_keywords.txt'
    # start_file = './resources/papers_keywords_r_out.json'
    # remain_file = './resources/papers_keywords_remain.json'
    #
    # data_start = {}
    # with open(start_file, 'r') as f:
    #     data_start = json.load(f)
    # #ids_start = [p['id'] for p in data_start['papers']]
    #
    # data_ok = {}
    # with open(ok_file, 'r') as f:
    #     data_ok = json.load(f)
    # ids_ok = [p['id'] for p in data_ok['papers']]
    #
    # data_remain = {'papers': []}
    # for paper in data_start['papers']:
    #     if paper['id'] in ids_ok:
    #         continue
    #     else:
    #         data_remain['papers'].append(paper)
    # ids_remain = [p['id'] for p in data_remain['papers']]
    #
    # with open(paper_list, 'r') as paper_list_file:
    #     while True:
    #         # Get next line from file
    #         line = paper_list_file.readline()
    #         # if line is empty, end of file is reached
    #         if line == "":
    #             break
    #         # Processing line: _id , relevant words
    #         info_paper = line.split("/")
    #         paper_id = info_paper[0].strip()
    #
    #         if paper_id in ids_ok:
    #             continue
    #         elif paper_id in ids_remain:
    #             continue
    #         else:
    #             paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #             paper_keyword_dict = {'id': paper_id}
    #             for word, pos in paper_words:
    #                 # "CCS CONCEPTS", "KEYWORDS", "INDEX TERMS", "CONTENT AREAS"
    #                 word_tmp = word.replace(" ", "").replace(":", "").lower()
    #                 if word_tmp in 'keywords' or word_tmp == 'indexterms':
    #                     paper_keyword_dict['keywords'] = ""
    #                     word_tmp = 'keywords'
    #                 else:
    #                     paper_keyword_dict[word_tmp] = ""
    #             data_remain['papers'].append(paper_keyword_dict)
    #
    # print("Papers OK: %s" % len(data_ok['papers']))
    # print("Papers REMAIN: %s" % len(data_remain['papers']))
    # with open(remain_file, 'w') as f:
    #     json.dump(data_remain, f, indent='\t')
    ##################################################

    ##################################################
    # # for each paper in 'papers_keywords_remain.json' that has the correspondent '_analyzable.xml',
    # # the keywords are extracted
    # # 'papers_keywords_analyzable.json' is the out_file
    # paper_list = './resources/LIST_PAPERS_keywords.txt'
    # remain_file = './resources/papers_keywords_remain.json'
    # papers_path = '../data/papers'
    # analyzable_file = './resources/papers_keywords_analyzable.json'
    #
    # data_remain = {}
    # with open(remain_file, 'r') as f:
    #     data_remain = json.load(f)
    # ids_remain = [p['id'] for p in data_remain['papers']]
    #
    # data_analyzable = {'papers': []}
    #
    # count = 0
    # with open(paper_list, 'r') as paper_list_file:
    #     while True:
    #         # Get next line from file
    #         line = paper_list_file.readline()
    #         # if line is empty, end of file is reached
    #         if line == "":
    #             break
    #         # Processing line: _id , relevant words
    #         info_paper = line.split("/")
    #         paper_id = info_paper[0].strip()
    #
    #         if paper_id in ids_remain:
    #             paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #             path_paper_analyzable = os.path.join(papers_path,
    #                                                  'paper_' + paper_id + '/' + 'paper_' + paper_id + '_analyzable.xml')
    #             if os.path.isfile(path_paper_analyzable):
    #                 count += 1
    #                 paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #                 try:
    #                     # parse analyzable
    #                     tree = ET.parse(path_paper_analyzable)
    #                     root = tree.getroot()
    #                     paper_add = False
    #                     paper_keyword_dict = {'id': paper_id}
    #                     for word, pos in paper_words:
    #                         # "CCS CONCEPTS", "KEYWORDS", "INDEX TERMS", "CONTENT AREAS"
    #                         word_tmp = word.replace(" ", "").replace(":", "").lower()
    #                         if word_tmp in 'keywords' or word_tmp == 'indexterms':
    #                             paper_keyword_dict['keywords'] = ""
    #                             word_tmp = 'keywords'
    #                         else:
    #                             paper_keyword_dict[word_tmp] = ""
    #                         # search subsection that start with 'word'
    #                         sub_list = list(filter(lambda x: x.text.strip().startswith(word), root.findall(".//subsection")))
    #                         if len(sub_list) > 0:
    #                             #print(paper_id, ":\n\t", sub_list[0].text.strip()[len(word):])
    #                             paper_keyword_dict[word_tmp] = sub_list[0].text.strip()[len(word):]
    #                             paper_add = True
    #                     if paper_add is True:
    #                         data_analyzable['papers'].append(paper_keyword_dict)
    #                 except Exception as e:
    #                     print(paper_id, ":\t", str(e))
    #
    # print("\n\nPapers ANALYZABLE: %s" % len(data_analyzable['papers']))
    # with open(analyzable_file, 'w') as f:
    #     json.dump(data_analyzable, f, indent='\t')
    ##################################################

    ##################################################                     TRANSFORM TO LIST       ########
    # # all papers in 'papers_keywords_analyzable.json' have been checked
    # # 'papers_keywords_analyzable_out.json'is the out_file with all the information correctly restructured
    # analyzable_file = './resources/papers_keywords_analyzable.json'
    # analyzable_out_file = './resources/papers_keywords_analyzable_out.json'
    #
    # data_analyzable = {}
    # with open(analyzable_file, 'r') as f:
    #     data_analyzable = json.load(f)
    # #ids_analyzable = [p['id'] for p in data_analyzable['papers']]
    #
    # for paper in data_analyzable['papers']:
    #     # CCSCONCECPTS
    #     if 'ccsconcepts' in paper.keys() and type(paper['ccsconcepts']) == str:
    #         paper['ccsconcepts'] = paper['ccsconcepts'].strip()
    #         paper['ccsconcepts'] = [concept.strip() for concept in paper['ccsconcepts'].split('\u2022')
    #                                 if concept.strip() != ""]
    #         new_concepts_list = []
    #         for concept in paper['ccsconcepts']:
    #             try:
    #                 if concept[-1] == '.':
    #                     concept = concept[:-1] + ';'
    #                 elif concept[-1] != ';':
    #                     concept = concept + ';'
    #             except Exception as e:
    #                 print(concept, ",", paper['id'], ":\tECCEZIONE ->", str(e))
    #                 sys.exit(1)
    #             new_concepts_list.append(concept)
    #         paper['ccsconcepts'] = new_concepts_list
    #     # KEYWORDS
    #     if 'keywords' in paper.keys() and type(paper['keywords']) == str:
    #         paper['keywords'] = paper['keywords'].strip()
    #         if paper['keywords'][-1] == '.' or paper['keywords'][-1] == ';' or paper['keywords'][-1] == ',':
    #             paper['keywords'] = paper['keywords'][:-1]
    #         if '\u00b7' in paper['keywords']:
    #             paper['keywords'] = [keyw.strip() for keyw in paper['keywords'].split('\u00b7') if keyw.strip() != ""]
    #         elif ';' in paper['keywords']:
    #             paper['keywords'] = [keyw.strip() for keyw in paper['keywords'].split(';') if keyw.strip() != ""]
    #         elif ',' in paper['keywords']:
    #             paper['keywords'] = [keyw.strip() for keyw in paper['keywords'].split(',') if keyw.strip() != ""]
    #         else:
    #             pass    # only one keyword
    #             # print("ERROR SPLIT 'keywords' for paper '%s'" % paper['id'])
    #             # sys.exit(2)
    #
    # # print("\n\nPapers ANALYZABLE: %s" % len(data_analyzable['papers']))
    # with open(analyzable_out_file, 'w') as f:
    #     json.dump(data_analyzable, f, indent='\t')
    ##################################################

    ##################################################        ADD TO 'OK' and CLEAR 'REMAIN'  #########
    # # to merge papers in 'papers_keywords_analyzable_out.json' and in 'papers_keywords_OK.json' ->
    # # -> it generated 'papers_keywords_OK_2.json'
    # # to clear papers in 'papers_keywords_OK_2.json' from 'papers_keywords_remain.json' ->
    # # -> it generates 'papers_keywords_remain_2.json
    # add_to_ok = './resources/papers_keywords_analyzable_out.json'
    # ok = "./resources/papers_keywords_OK.json"
    #
    # data_to_add = {}
    # with open(add_to_ok, 'r') as f:
    #     data_to_add = json.load(f)
    #
    # data_ok = {}
    # with open(ok, 'r') as f:
    #     data_ok = json.load(f)
    # data_ok['papers'].extend(data_to_add['papers'])
    #
    # ok_2 = "./resources/papers_keywords_OK_2.json"
    # with open(ok_2, 'w') as f:
    #     json.dump(data_ok, f, indent='\t')
    #
    # # remove from 'remain'
    # remain = './resources/papers_keywords_remain.json'
    # data_remain = {}
    # with open(remain, 'r') as f:
    #     data_remain = json.load(f)
    #
    # ids_ok = [p['id'] for p in data_ok['papers']]
    # ids_remain = [p['id'] for p in data_remain['papers']]
    # print("Before deleting: OK = %s, REMAIN = %s" %(len(ids_ok), len(ids_remain)))
    #
    # data_remain_2 = {'papers': []}
    # for paper in data_remain['papers']:
    #     if paper['id'] not in ids_ok:
    #         data_remain_2['papers'].append(paper)
    # print("After deleting: OK = %s, REMAIN = %s" % (len(ids_ok), len(data_remain_2['papers'])))
    #
    # remain_2 = "./resources/papers_keywords_remain_2.json"
    # with open(remain_2, 'w') as f:
    #     json.dump(data_remain_2, f, indent='\t')
    # ##################################################

    ##################################################
    # # for each paper in 'papers_keywords_remain_2.json' that has the correspondent '_analyzable.xml',
    # # the keywords are extracted
    # # 'papers_keywords_analyzable_2.json' is the out_file
    # paper_list = './resources/LIST_PAPERS_keywords.txt'
    # remain_file = './resources/papers_keywords_remain_2.json'
    # papers_path = '../data/papers'
    # analyzable_file = './resources/papers_keywords_analyzable_2.json'
    #
    # data_remain = {}
    # with open(remain_file, 'r') as f:
    #     data_remain = json.load(f)
    # ids_remain = [p['id'] for p in data_remain['papers']]
    #
    # data_analyzable = {'papers': []}
    #
    # count = 0
    # with open(paper_list, 'r') as paper_list_file:
    #     while True:
    #         # Get next line from file
    #         line = paper_list_file.readline()
    #         # if line is empty, end of file is reached
    #         if line == "":
    #             break
    #         # Processing line: _id , relevant words
    #         info_paper = line.split("/")
    #         paper_id = info_paper[0].strip()
    #
    #         if paper_id in ids_remain:
    #             paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #             path_paper_analyzable = os.path.join(papers_path,
    #                                                  'paper_' + paper_id + '/' + 'paper_' + paper_id + '_analyzable.xml')
    #             if os.path.isfile(path_paper_analyzable):
    #                 count += 1
    #                 paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #                 try:
    #                     # parse analyzable
    #                     tree = ET.parse(path_paper_analyzable)
    #                     root = tree.getroot()
    #                     paper_add = False
    #                     paper_keyword_dict = {'id': paper_id}
    #                     for word, pos in paper_words:
    #                         # "CCS CONCEPTS", "KEYWORDS", "INDEX TERMS", "CONTENT AREAS"
    #                         word_tmp = word.replace(" ", "").replace(":", "").lower()
    #                         if word_tmp in 'keywords' or word_tmp == 'indexterms':
    #                             paper_keyword_dict['keywords'] = ""
    #                             word_tmp = 'keywords'
    #                         else:
    #                             paper_keyword_dict[word_tmp] = ""
    #                         # search subsection that start with 'word'
    #                         sub_list = list(filter(lambda x: word in x.text.strip(), root.findall(".//subsection"))) # x.text.strip().startswith(word)
    #                         if len(sub_list) > 0:
    #                             #print(paper_id, ":\n\t", sub_list[0].text.strip()[len(word):])
    #                             paper_keyword_dict[word_tmp] = sub_list[0].text.strip()#[len(word):]
    #                             paper_add = True
    #                     if paper_add is True:
    #                         data_analyzable['papers'].append(paper_keyword_dict)
    #                 except Exception as e:
    #                     print(paper_id, ":\t", str(e))
    #
    # print("\n\nPapers ANALYZABLE: %s" % len(data_analyzable['papers']))
    # with open(analyzable_file, 'w') as f:
    #     json.dump(data_analyzable, f, indent='\t')
    ##################################################

    ##################################################
    # run TRANSFORM TO LIST with:
    # analyzable_file = './resources/papers_keywords_analyzable_2.json'
    # analyzable_out_file = './resources/papers_keywords_analyzable_out_2.json'
    ##################################################

    ##################################################
    # run ADD TO 'OK' and CLEAR 'REMAIN' with:
    # add_to_ok = './resources/papers_keywords_analyzable_out_2.json'
    # ok = "./resources/papers_keywords_OK_2.json"
    # ok_2 = "./resources/papers_keywords_OK_3.json"
    # remain = './resources/papers_keywords_remain_2.json'
    # remain_2 = './resources/papers_keywords_remain_3.json'
    ##################################################

    ##################################################
    # # for each paper in 'papers_keywords_remain_3.json' that has the correspondent '.txt', the keywords are extracted
    # # 'papers_keywords_analyzable_3.json' is the out_file
    # paper_list = './resources/LIST_PAPERS_keywords.txt'
    # remain_file = './resources/papers_keywords_remain_3.json'
    # papers_path = '../data/papers'
    # analyzable_file = './resources/papers_keywords_analyzable_3.json'
    #
    # data_remain = {}
    # with open(remain_file, 'r') as f:
    #     data_remain = json.load(f)
    # ids_remain = [p['id'] for p in data_remain['papers']]
    #
    # data_analyzable = {'papers': []}
    #
    # count = 0
    # with open(paper_list, 'r') as paper_list_file:
    #     while True:
    #         # Get next line from file
    #         line = paper_list_file.readline()
    #         # if line is empty, end of file is reached
    #         if line == "":
    #             break
    #         # Processing line: _id , relevant words
    #         info_paper = line.split("/")
    #         paper_id = info_paper[0].strip()
    #
    #         if paper_id in ids_remain:
    #             paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #             path_paper_txt = os.path.join(papers_path,
    #                                           'paper_' + paper_id + '/' + 'paper_' + paper_id + '.txt')
    #             if os.path.isfile(path_paper_txt):
    #                 count += 1
    #                 paper_words = [tuple(w.strip().split(' - ')) for w in info_paper[1:]]
    #                 try:
    #                     # parse txt
    #                     text = ""
    #                     with open(path_paper_txt) as f:
    #                         text = ''.join(f.readlines())
    #                     paper_add = False
    #                     paper_keyword_dict = {'id': paper_id}
    #                     for word, pos in paper_words:
    #                         # "CCS CONCEPTS", "KEYWORDS", "INDEX TERMS", "CONTENT AREAS"
    #                         word_tmp = word.replace(" ", "").replace(":", "").lower()
    #                         if word_tmp in 'keywords' or word_tmp == 'indexterms':
    #                             paper_keyword_dict['keywords'] = ""
    #                             word_tmp = 'keywords'
    #                         else:
    #                             paper_keyword_dict[word_tmp] = ""
    #                         # search part of text that start with 'word'
    #                         #if paper_id == '66124':
    #                         l_index_word = text.find(word)
    #                         if l_index_word == -1:
    #                             print("'%s' not found in '%s'" % (word, paper_id))
    #                         else:
    #                             # extract from text
    #                             text = text[l_index_word:].strip()
    #                             if text[0] == '.':
    #                                 text = text[1:]
    #                             #print(text[:1000])
    #                             point_index_word = text.find('.')
    #                             if point_index_word == -1:
    #                                 print("No point found in '%s'" % paper_id)
    #                             else:
    #                                 #print('\n', point_index_word)
    #                                 r_index_word = text[point_index_word:].strip().find('\n')
    #                                 if r_index_word == -1:
    #                                     print("No new line found in '%s'" % paper_id)
    #                                 else:
    #                                     #print('\n', r_index_word)
    #                                     text = text[:point_index_word+r_index_word].strip()
    #                                     #print('\n', text)
    #                                     paper_keyword_dict[word_tmp] = text
    #                                     paper_add = True
    #                             #sys.exit(1)
    #
    #                     if paper_add is True:
    #                         data_analyzable['papers'].append(paper_keyword_dict)
    #                 except Exception as e:
    #                     print(paper_id, ":\t", str(e))
    #
    # print("\n\nPapers ANALYZABLE: %s" % len(data_analyzable['papers']))
    # with open(analyzable_file, 'w') as f:
    #     json.dump(data_analyzable, f, indent='\t')
    ##################################################

    ##################################################
    # run TRANSFORM TO LIST with:
    # analyzable_file = './resources/papers_keywords_analyzable_3.json'
    # analyzable_out_file = './resources/papers_keywords_analyzable_out_3.json'
    ##################################################

    ##################################################
    # run ADD TO 'OK' and CLEAR 'REMAIN' with:
    # add_to_ok = './resources/papers_keywords_analyzable_out_3.json'
    # ok = "./resources/papers_keywords_OK_3.json"
    # ok_2 = "./resources/papers_keywords_OK_4.json"
    # remain = './resources/papers_keywords_remain_3.json'
    # remain_2 = './resources/papers_keywords_remain_4.json'
    ##################################################

    ##################################################
    # rename "./resources/papers_keywords_OK_4.json" in "./resources/papers_keywords.json"
    ##################################################