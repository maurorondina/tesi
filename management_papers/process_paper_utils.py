import string
import sys
import re
import logging
import xml.etree.ElementTree as ET
import heapq


def print_message(logger, status, message):
    """
    print_message() uses the logger to log a message with the given status.
    """
    if logger is not None:
        caller_function = sys._getframe(1).f_code.co_name
        logger.log(status, caller_function + "() - " + message)


def replace_special_chars_xml(text):
    special_chars_xml = {'&amp;': '&',
                         '&lt;': '<',
                         '&gt;': '>',
                         '&quot;': '\"',
                         '&apos;': '\''
                         }
    for k, i in special_chars_xml.items():
        text = text.replace(k, i)
    return text


def printable_chars(text):
    line = "".join(c for c in text if c in string.printable)
    return line


def extract_children_text(root):
    # print(root.tag, root.attrib, root.text, root.tail)
    if root.text is not None:
        yield root.text
    children = root.findall("*")
    for child in children:
        yield from extract_children_text(child)
    if root.tail is not None:
        yield root.tail


def get_title(first_page, **kwargs):
    """
    get_title() try to find the title searching for font with the highest size.
    :param first_page: first paper's page, in which the search is performed.
    :param kwargs: 'logger' for logging.
    :return: the title.
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None

    fonts = first_page.findall("./fontspec")
    fonts_size = list(map(lambda x: int(x.attrib['size']), fonts))
    index_max_size = fonts_size.index(max(fonts_size))
    font_to_search = fonts[index_max_size].attrib['id']
    l = list(filter(lambda x: x.attrib['font'] == font_to_search, first_page.findall("./text[@font]")))
    if len(l) == 1:  # title in one line
        return l[0].text, l
    else:  # title in more lines
        title = ""
        l = list(map(lambda x: x.text, l))
        print_message(logger, logging.DEBUG, "All the lines detected for the title:\n- " + "\n- ".join(l))
        for i, line in enumerate(l):
            # if first_page.findall("./text[" + str(i + 1) + "]")[0].text in l:
            title = title + " " + l[i]
        return title.strip(), l
    # else:                 # return the line with max height
    # print(list(map(lambda x: x.text, first_page.findall("./text[3]"))))
    # height_l = list(map(lambda x: x.attrib['height'], l))
    # index = height_l.index(max(height_l))
    # return l[index].text


def order_paragraph_titles(paragraph_titles, pages, **kwargs):
    res = []
    for p_title in paragraph_titles:
        if p_title.tag == 'item':
            res.append((p_title, p_title.attrib['page']))
        else:
            for p in pages:
                found = list(
                    filter(lambda x: x.attrib == p_title.attrib and x.text == p_title.text, p.findall("./text")))
                if len(found) > 0:
                    res.append((p_title, p.attrib['number']))
    return sorted(res, key=lambda tup: int(tup[1]))


def get_font_title(text_to_find, root, **kwargs):  # ex: "1.  Introduction.." / "Introduction.." / "ntroduction.."
    """
    get_font_title() try to extract the font of a text in the xml.
    :param text_to_find: the paragraph title to search.
    :param root: the xml page used to search the text_to_find.
    :param kwargs: 'logger' for logging.
    :return: the font if found, otherwise None.
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None

    # ex: "1.  Introduction.." , " Introduction.." , "Introduction.."
    to_search = ".//text[.='" + text_to_find + "']"
    found = [t for t in root.findall(to_search)]
    if len(found) > 0:
        print_message(logger, logging.DEBUG, 'font found for the searching title "' + text_to_find + '".')
        return found[0].attrib['font']
    else:
        print_message(logger, logging.DEBUG, 'nothing found for the searching title "' + text_to_find + '".')

    # ex: "Introduction.."
    possible_number = str.split(text_to_find.strip(), sep=" ")[0]
    number = re.match("^((\\d+|[MDCLXVI]+|[mdclxvi])\\.?)+$", possible_number)
    if number is not None:
        to_search = ".//text[.='" + text_to_find[len(possible_number):].strip() + "']"
        found = [t for t in root.findall(to_search)]
        if len(found) > 0:
            print_message(logger, logging.DEBUG, 'font found for the searching title "' +
                          text_to_find[len(possible_number):].strip() + '".')
            return found[0].attrib['font']
        else:
            print_message(logger, logging.DEBUG, 'nothing found for the searching title "' +
                          text_to_find[len(possible_number):].strip() + '".')

    # ex: "ntroduction.."
    to_search = ".//text[.='" + text_to_find.strip()[1:] + "']"
    found = [t for t in root.findall(to_search)]
    if len(found) > 0:
        print_message(logger, logging.DEBUG, 'font found for the searching title "' +
                      text_to_find.strip()[1:] + '".')
        return found[0].attrib['font']
    else:
        print_message(logger, logging.DEBUG, 'nothing found for the searching title "' +
                      text_to_find.strip()[1:] + '".')

    # title not found
    return None


def get_valid_titles_by_font(font_title, root, **kwargs):
    """

    :param font_title:
    :param root:
    :param kwargs:
    :return:
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    possible_paragraph_titles = list(filter(lambda x: x.attrib['font'] == font_title and x.text.strip() != "",
                                            root.findall(".//text[@font]")))

    # ex. ['1   Introduction', '2', 'Estimation of the Class Distribution on an Unlabeled Data Set', '3',
    # 'Improving Classification Based on Class Probability Estimates', '4', 'Experimental Results', '5', 'Conclusions',
    # 'References']
    # -> ['1   Introduction', 'Estimation of the Class Distribution on an Unlabeled Data Set', 'Improving
    # Classification Based on Class Probability Estimates', 'Experimental Results', 'Conclusions', 'References']
    valid_titles = []
    take_into_account = False
    for title in possible_paragraph_titles:
        if not take_into_account:
            if title.text.strip().lower().startswith("abstract") or "ntroduction" in title.text.lower():
                take_into_account = True
        if take_into_account:
            possible_number = str.split(title.text.strip(), sep=" ")[0]
            number = re.match("^((\\d+|[MDCLXVI]+|[mdclxvi])\\.?)+$", possible_number)
            if number is not None and len(number.group(0)) == len(title.text.strip()):
                pass  # invalid title: it contains only the index number
            else:
                valid_titles.append(title)

    return valid_titles


def find_abstract(root, **kwargs):
    """
    find_abstract() try to extract the "Abstract" title in the xml.
    :param root: xml iin which perform the search.
    :param kwargs: 'logger' for logging.
    :return: the "Abstract" if found, otherwise None.
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    # ex: "Abstract"/"Abstract[.-] .."
    found = list(filter(lambda x: str(x.text).strip().lower() == "abstract" or
                                  (str(x.text).strip().lower().startswith("abstract") and
                                   str(x.text).strip()[len("abstract"):].strip().split(sep=" ")[0]
                                   in string.punctuation)
                        , root.findall(".//text")))

    if len(found) == 0:
        found = list(filter(lambda x: str(x.text).strip().lower() == "bstract" or
                                      (str(x.text).strip().lower().startswith("bstract") and
                                       str(x.text).strip()[len("bstract"):].strip().split(sep=" ")[0]
                                       in string.punctuation)
                            , root.findall(".//text")))

    if len(found) == 1:
        print_message(logger, logging.DEBUG, 'abstract found: "' + found[0].text + '".')
        return found[0]
    elif len(found) > 1:
        height_l = list(map(lambda x: x.attrib['height'], found))
        index = height_l.index(max(height_l))
        print_message(logger, logging.DEBUG, 'abstract found: "' + found[index].text + '".')
        return found[index]
    else:
        print_message(logger, logging.DEBUG, 'abstract not found.')
        return None


def find_references(root, **kwargs):
    """
    find_references() try to extract the "References" title in the xml.
    :param root: xml in which perform the search.
    :param kwargs:'logger' for logging.
    :return: the "References" if found, otherwise None.
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    # ex: "Reference"/"References"/"Reference List"
    found = list(filter(lambda x: str(x.text).strip().lower() == "reference" or
                                  str(x.text).strip().lower() == "references" or
                                  str(x.text).strip().lower() == "reference list", root.findall(".//text")))

    if len(found) == 0:
        found = list(filter(lambda x: str(x.text).strip().lower() == "eference" or
                                      str(x.text).strip().lower() == "eferences" or
                                      str(x.text).strip().lower() == "eference list", root.findall(".//text")))

    if len(found) == 1:
        print_message(logger, logging.DEBUG, 'references found: "' + found[0].text + '".')
        return found[0]
    elif len(found) > 1:
        height_l = list(map(lambda x: x.attrib['height'], found))
        index = height_l.index(max(height_l))
        print_message(logger, logging.DEBUG, 'references found: "' + found[index].text + '".')
        return found[index]
    else:
        print_message(logger, logging.DEBUG, 'references not found.')
        return None


def find_introduction_or_similar(root, **kwargs):
    """
    search_introduction() try to extract the "Introduction" title in the xml.
    :param root: xml in which perform the search.
    :param kwargs:'logger' for logging; 'font' to search the "Introduction using a given font.
    :return: the "Introduction" if found, otherwise another esteemed title.
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    font_title = kwargs['font'] if 'font' in kwargs else None
    paper_title = kwargs['paper_title'] if 'paper_title' in kwargs else None

    possible_paragraph_titles = []
    another_one = False
    if font_title is not None:
        possible_paragraph_titles = list(filter(lambda x: x.attrib['font'] == font_title and
                                                          "ntroduction" in str(x.text).lower(),
                                                root.findall(".//text[@font]")))
    if font_title is None or len(possible_paragraph_titles) == 0:
        possible_paragraph_titles = list(filter(lambda x: "ntroduction" in str(x.text).lower(),
                                                root.findall(".//text[@font]")))
    if len(possible_paragraph_titles) == 1:
        return possible_paragraph_titles[0]
    elif len(possible_paragraph_titles) > 1:
        print_message(logger, logging.DEBUG, "All the lines detected for the ntroduction title:\n- " +
                      "\n- ".join(list(map(lambda x: x.text, possible_paragraph_titles))))
        introduction_titles = []
        for title in possible_paragraph_titles:
            possible_number = str.split(title.text.strip(), sep=" ")[0]
            number = re.match("^((\\d+|[MDCLXVI]+|[mdclxvi])\\.?)+$", possible_number)
            if number is not None and title.text[len(number.group(0)):].strip().lower().startswith("introduction"):
                introduction_titles.append(title)
                # return title  # ex: "1.  Introduction.."
            elif title.text.strip().lower().startswith("introduction") or title.text.strip(). \
                    lower().startswith("ntroduction"):
                introduction_titles.append(title)
                # return title  # ex: " Introduction.." , "ntroduction.."
        if len(introduction_titles) > 0:
            height_l = list(map(lambda x: x.attrib['height'], introduction_titles))
            index = height_l.index(max(height_l))
            return introduction_titles[index]
        else:
            # the introduction title not found, search another one
            another_one = True
    elif another_one:
        possible_paragraph_titles = root.findall(".//text[@font]")
        possible_paragraph_titles = list(filter(lambda x: x.text.strip() != "", possible_paragraph_titles))
        height_l = list(map(lambda x: x.attrib['height'], possible_paragraph_titles))
        index = height_l.index(max(height_l))
        if paper_title.strip().startswith(possible_paragraph_titles[index].text.strip()):
            index = height_l.index(heapq.nlargest(2, height_l)[1])
        return possible_paragraph_titles[index]
    else:
        return None


def find_introduction(root, **kwargs):
    """
    search_introduction() try to extract the "Introduction" title in the xml.
    :param root: xml in which perform the search.
    :param kwargs:'logger' for logging; 'font' to search the "Introduction using a given font.
    :return: the "Introduction" if found, otherwise None.
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    font_title = kwargs['font'] if 'font' in kwargs else None
    possible_paragraph_titles = []
    if font_title is not None:
        possible_paragraph_titles = list(filter(lambda x: x.attrib['font'] == font_title and
                                                          "ntroduction" in str(x.text).lower(),
                                                root.findall(".//text[@font]")))
    else:
        possible_paragraph_titles = list(filter(lambda x: "ntroduction" in str(x.text).lower(),
                                                root.findall(".//text[@font]")))
    if len(possible_paragraph_titles) == 1:
        return possible_paragraph_titles[0]
    elif len(possible_paragraph_titles) > 1:
        print_message(logger, logging.DEBUG, "All the lines detected for the ntroduction title:\n- " +
                      "\n- ".join(list(map(lambda x: x.text, possible_paragraph_titles))))
        for title in possible_paragraph_titles:
            possible_number = str.split(title.text.strip(), sep=" ")[0]
            number = re.match("^((\\d+|[MDCLXVI]+|[mdclxvi])\\.?)+$", possible_number)
            if number is not None and title.text[len(number.group(0)):].strip().lower().startswith("introduction"):
                return title  # ex: "1.  Introduction.."
            elif title.text.strip().lower().startswith("introduction") or title.text.strip(). \
                    lower().startswith("ntroduction"):
                return title  # ex: " Introduction.." , "ntroduction.."
        return None  # return possible_paragraph_titles[0]    # the first title found
    else:
        return None


def get_paragraph_titles(paragraph_titles_from_index, root, pages, **kwargs):
    """

    :param paragraph_titles_from_index:
    :param root:
    :param pages:
    :param kwargs:
    :return:
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    paper_title = kwargs['paper_title'] if 'paper_title' in kwargs else None
    paragraph_titles = []
    search_without_index = False

    if paragraph_titles_from_index is not None:  # paragraph titles from index
        if None in list(map(lambda x: x.text, paragraph_titles_from_index)):  # corrupted index
            print_message(logger, logging.WARN, "The index is corrupted.")

            # 1-
            # find "introduction" title or take the first title
            first_title = ""
            first_title_page = None
            for title in paragraph_titles_from_index:
                if first_title == "" and first_title_page is None and title.text is not None:
                    first_title = title.text
                    first_title_page = pages[int(title.attrib['page']) - 1]
                if "ntroduction" in title.text.lower():
                    first_title = title.text
                    first_title_page = pages[int(title.attrib['page']) - 1]
                    break
            if first_title != "":
                print_message(logger, logging.DEBUG,
                              'The title of the corrupted index used to find the font is: "' + first_title + '".')
                font_title = get_font_title(first_title, first_title_page, logger=logger)
                if font_title is None:
                    print_message(logger, logging.WARN, 'No font detected for the title"' + first_title + '".')
                    # let's do as if the index doesn't exist
                    search_without_index = True
                else:
                    # 2-
                    print_message(logger, logging.DEBUG, 'Font of the title detected: "' + font_title + '".')
                    paragraph_titles = get_valid_titles_by_font(font_title, root)
                    print_message(logger, logging.INFO, "Valid paragraph titles found:\n\t- " +
                                  "\n\t- ".join(list(map(lambda x: x.text, paragraph_titles))))
                    # 3-
                    # check if "Abstract"/"Abstract[.-] .." is found, otherwise search it
                    abstract_l = list(filter(lambda x: str(x.text).strip().lower() == "abstract" or
                                                       (str(x.text).strip().lower().startswith("abstract") and
                                                        str(x.text).strip()[len("abstract"):].strip().split(sep=" ")[0]
                                                        in string.punctuation)
                                             , paragraph_titles))
                    if len(abstract_l) == 0:
                        abstract_title = find_abstract(root, logger=logger)
                        if abstract_title is None:
                            print_message(logger, logging.INFO, "Abstract not present or detected.")
                        else:
                            paragraph_titles.insert(0, abstract_title)
                            print_message(logger, logging.INFO, "Abstract added.")
                    # check if "Reference"/"References"/"Reference List" is found, otherwise search it
                    references_l = list(filter(lambda x: str(x.text).strip().lower() == "reference" or
                                                         str(x.text).strip().lower() == "references" or
                                                         str(x.text).strip().lower() == "reference list",
                                               paragraph_titles))
                    if len(references_l) == 0:
                        references_title = find_references(root, logger=logger)
                        if references_title is None:
                            print_message(logger, logging.INFO, "References not present or detected.")
                        else:
                            paragraph_titles.append(references_title)
                            print_message(logger, logging.INFO, "References added.")
            else:
                # let's do as if the index doesn't exist
                search_without_index = True

        else:  # not corrupted index
            # search in xml
            paragraph_titles = paragraph_titles_from_index
            # 3-
            # check if "Abstract"/"Abstract[.-] .." is found, otherwise search it
            abstract_l = list(filter(lambda x: x.strip().lower() == "abstract" or
                                               (x.strip().lower().startswith("abstract") and
                                                x.strip()[len("abstract"):].strip().split(sep=" ")[0]
                                                in string.punctuation)
                                     , list(map(lambda p: p.text, paragraph_titles))))
            if len(abstract_l) == 0:
                abstract_title = find_abstract(root, logger=logger)
                if abstract_title is None:
                    print_message(logger, logging.INFO, "Abstract not present or detected.")
                else:
                    paragraph_titles.insert(0, abstract_title)
                    print_message(logger, logging.INFO, "Abstract added.")
            # check if "Reference"/"References"/"Reference List" is found, otherwise search it
            references_l = list(filter(lambda x: x.strip().lower() == "reference" or
                                                 x.strip().lower() == "references" or
                                                 x.strip().lower() == "reference list"
                                       , list(map(lambda p: p.text, paragraph_titles))))
            if len(references_l) == 0:
                references_title = find_references(root, logger=logging)
                if references_title is None:
                    print_message(logger, logging.INFO, "References not present or detected.")
                else:
                    paragraph_titles.append(references_title)
                    print_message(logger, logging.INFO, "References added.")

    if paragraph_titles_from_index is None or search_without_index:
        # not paragraph titles from index
        # 3-
        abstract_title = find_abstract(root, logger=logger)
        if abstract_title is None:
            print_message(logger, logging.INFO, "Abstract not present or detected.")
        else:
            print_message(logger, logging.INFO, 'Abstract with font=' + abstract_title.attrib['font'] +
                          ' found: "' + abstract_title.text + '".')
        references_title = find_references(root, logger=logger)
        if references_title is None:
            print_message(logger, logging.INFO, "References not present or detected.")
        else:
            print_message(logger, logging.INFO, 'References with font=' + references_title.attrib['font'] +
                          ' found: "' + references_title.text + '".')
        # 1-
        # find "introduction" title with References font
        if references_title is not None:
            introduction_title = find_introduction_or_similar(root, logger=logger, font=references_title.attrib['font'],
                                                              paper_title=paper_title)
            if introduction_title is not None:
                print_message(logger, logging.INFO, 'Introduction with References font=' +
                              introduction_title.attrib['font'] + ' found: "' + introduction_title.text + '".')
                paragraph_titles = get_valid_titles_by_font(introduction_title.attrib['font'], root)
                print_message(logger, logging.INFO, "Valid paragraph titles found:\n\t- " +
                              "\n\t- ".join(list(map(lambda x: x.text, paragraph_titles))))
            else:
                print_message(logger, logging.INFO, 'Introduction with References font=' +
                              references_title.attrib['font'] + ' not found.')
        elif abstract_title is not None:
            introduction_title = find_introduction_or_similar(root, logger=logger, font=abstract_title.attrib['font'],
                                                              paper_title=paper_title)
            if introduction_title is not None:
                print_message(logger, logging.INFO, 'Introduction with Abstract font=' +
                              introduction_title.attrib['font'] + ' found: "' + introduction_title.text + '".')
                paragraph_titles = get_valid_titles_by_font(introduction_title.attrib['font'], root)
                print_message(logger, logging.INFO, "Valid paragraph titles found:\n\t- " +
                              "\n\t- ".join(list(map(lambda x: x.text, paragraph_titles))))
            else:
                print_message(logger, logging.INFO, 'Introduction with Abstract font=' +
                              abstract_title.attrib['font'] + ' not found.')
        else:
            introduction_title = find_introduction_or_similar(root, logger=logger, paper_title=paper_title)
            if introduction_title is not None:
                print_message(logger, logging.INFO, 'Introduction with font=' +
                              introduction_title.attrib['font'] + ' found: "' + introduction_title.text + '".')
                paragraph_titles = get_valid_titles_by_font(introduction_title.attrib['font'], root)
                print_message(logger, logging.INFO, "Valid paragraph titles found:\n\t- " +
                              "\n\t- ".join(list(map(lambda x: x.text, paragraph_titles))))
        if abstract_title is not None and abstract_title not in paragraph_titles:
            paragraph_titles.insert(0, abstract_title)
        if references_title is not None and references_title not in paragraph_titles:
            paragraph_titles.append(references_title)

    ordered_paragraph_titles = order_paragraph_titles(paragraph_titles, pages)
    return ordered_paragraph_titles if len(ordered_paragraph_titles) == len(paragraph_titles) else \
        [(p, "'not estimated'") for p in paragraph_titles]


def get_new_id_paragraph(current_id_paragraph):
    if current_id_paragraph is None:
        return None
    else:
        current_value = current_id_paragraph.split(sep='.')[-1]
        return current_id_paragraph[:-len(current_value)] + str(int(current_value) + 1)


def parse_txt_fw_bw(out_paper_root, txt_file_lines, title_paper, paragraph_titles, **kwargs):
    """
    parse_txt() reads the txt_file and builds the xml_analyzable for the output, using the information extracted from
    the temporary_xml (such as title_paper and paragraph_titles).
    :param out_paper_root: root of the xml_analyzable
    :param txt_file_lines: all the lines of input txt
    :param title_paper: the paper's title (passed as argument or extracted from the temporary_xml)
    :param paragraph_titles: the paper's paragraph titles (extracted from the temporary_xml), with the associated pages
    :param kwargs: logger' for logging
    :return: the built and analyzable xml Tree, otherwise None
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    page_for_title = kwargs['page_for_title'] if 'page_for_title' in kwargs else None
    # in txt_lines_informative, -1 means that it is an usual line
    txt_lines_informative = []
    txt_lines = []
    for line in txt_file_lines:
        line_tmp = re.sub("[^0-9a-zA-Z\\s]", " ", line).lower()
        line_tmp = re.sub("\\s+|\\n|\\v|\\f", " ", line_tmp).strip()
        txt_lines.append(line_tmp)
        txt_lines_informative.append([-1, line.replace('\n', '').replace('\v', ' ').replace('\f', ' ')])

    xml_titles = []
    l = [title_paper]
    l.extend(paragraph_titles)
    for title in l:
        title_tmp = re.sub("[^0-9a-zA-Z\\s]", " ", replace_special_chars_xml(title)).lower()
        title_tmp = re.sub("\\s+|\\n|\\v|\\f", " ", title_tmp).strip()
        xml_titles.append(title_tmp)

    txt_text_tmp = "|" + "|".join(txt_lines) + "|"
    txt_text = " " + " ".join(txt_lines) + " "
    start_index_informative = 0
    start_index_title = 0
    backward_i = []
    for i, title in enumerate(xml_titles):
        index_title = txt_text.find(title, start_index_title)
        if index_title == -1:
            if i == 0:  # paper title not found.. try to extract
                print_message(logger, logging.FATAL, 'Paper title "' + title + '" not found in txt.')
                if page_for_title is None:
                    return None
                else:
                    print_message(logger, logging.INFO, 'Trying to extract a new paper title.')
                    title, _ = get_title(page_for_title, logger=logger)
                    title = re.sub("[^0-9a-zA-Z\\s]", " ", replace_special_chars_xml(title)).lower()
                    title = re.sub("\\s+|\\n", " ", title).strip()
                    index_title = txt_text.find(title, start_index_title)
                    if index_title == -1:
                        print_message(logger, logging.FATAL, 'Extracted paper title "' + title + '" not found in txt.')
                        return None
            else:
                print_message(logger, logging.FATAL, 'Paragraph title "' + title + '" not found in txt.')
                return None

        ###########
        title_found = False
        find_last_index = False
        while title_found is False:
            first_index = txt_text_tmp[:index_title].rfind("|")
            if find_last_index:
                last_index = txt_text_tmp.find("|", index_title + len(title))
                title_lines = txt_text_tmp[first_index:last_index].split(sep="|")
            else:
                title_lines = txt_text_tmp[first_index:index_title + len(title)].split(sep="|")
            # ex: ['', '4 how fast is fast sgd analysis of step', 'mini batch sizes and computational', 'efficiency for quadratic loss']
            title_lines = title_lines[1:]
            full_search = False
            if len(title_lines) == 1:
                try:
                    index_informative = txt_lines.index(title, start_index_informative)
                    txt_lines_informative[index_informative][0] = i
                    start_index_informative = index_informative + 1
                    start_index_title = index_title + 1
                    title_found = True
                except ValueError as e:
                    print_message(logger, logging.DEBUG, '"' + title + '" not found. Proceeding with a full search..')
                    full_search = True
            if len(title_lines) > 1 or full_search is True:
                i_list = []
                for line in title_lines:
                    try:
                        index_informative = txt_lines.index(line, start_index_informative)
                        i_list.append(index_informative)
                        if find_last_index:
                            backward_i.append(index_informative)
                        print_message(logger, logging.DEBUG, 'Title line "' + line + '" found for the title "' + title +
                                      '", from the index ' + str(index_informative) + '.')
                        start_index_informative = index_informative + 1
                        start_index_title = index_title + 1
                        title_found = True
                        find_last_index = False
                    except ValueError as e:
                        print_message(logger, logging.DEBUG, 'Title line "' + line +
                                      '" not found in list for the title "' + title + '", but has matched with: [' +
                                      " ".join(title_lines) + "]")
                        index_title_tmp_forward = txt_text_tmp.find(title + "|", index_title + 1)
                        index_title_tmp_backward = txt_text_tmp.find("|" + title, index_title - 1)
                        if index_title_tmp_forward != -1 and index_title_tmp_backward == -1:
                            index_title_tmp = index_title_tmp_forward
                            find_last_index = False
                        elif index_title_tmp_forward == -1 and index_title_tmp_backward != -1:
                            index_title_tmp = index_title_tmp_backward + 1
                            find_last_index = True
                        elif index_title_tmp_forward != -1 and index_title_tmp_backward != -1:
                            if index_title_tmp_forward < index_title_tmp_backward + 1:
                                index_title_tmp = index_title_tmp_forward
                                find_last_index = False
                            else:
                                index_title_tmp = index_title_tmp_backward + 1
                                find_last_index = True
                        elif index_title_tmp_forward == -1 and index_title_tmp_backward == -1:
                            print_message(logger, logging.FATAL, 'Title line "' + title + '" not found in txt.')
                            return None
                        if index_title != index_title_tmp:
                            index_title = index_title_tmp
                            i_list = []
                            title_found = False
                            break
                for i_list_i in i_list:
                    txt_lines_informative[i_list_i][0] = i
        ###########

    backward_titles_dict = {}
    for s_i in backward_i:
        txt_line_informative = txt_lines_informative[s_i]
        backward_titles_dict[txt_line_informative[0]] = [s_i, txt_line_informative[1]]
    offset = 0
    for key, item in backward_titles_dict.items():
        point_index = item[1].rfind(".")
        if point_index != -1:
            number = re.match("^((\\d+|[MDCLXVI]+|[mdclxvi])\\.?)+$", item[1][:point_index])
            if number is None:
                txt_lines_informative.insert(item[0] + 1 + offset, [-1, item[1][point_index+1:].strip()])
                txt_lines_informative[item[0] + offset][1] = item[1][:point_index+1].strip()
                offset += 1

    # Check that all paragraph titles are found:
    print_message(logger, logging.INFO, "Titles matched:\n\t- " +
                  "\n\t- ".join([str(i[0]) + "# " + i[1].strip() for i in txt_lines_informative if i[0] >= 0]))

    # create paragraph and subsection
    id_paper = None if 'id' not in out_paper_root.attrib else out_paper_root.attrib['id']
    current_id_paragraph = None if id_paper is None else id_paper + ".-1"
    current_id_subsection = None if current_id_paragraph is None else current_id_paragraph + ".0"
    current_root = out_paper_root
    lines_accumulated = []
    id_lines_accumulated = -1
    for line in txt_lines_informative:
        if line[0] != id_lines_accumulated:  # create a child
            if id_lines_accumulated >= 0:  # create a paragraph
                if current_root.tag == 'paragraph' and len(
                        current_root.findall("./subsection")) == 0:  # merge the paragraphs
                    current_root.attrib['name'] = current_root.attrib['name'] + " " + " ".join(
                        lines_accumulated).strip()
                else:
                    child_title = ET.SubElement(out_paper_root, 'title' if id_lines_accumulated == 0 else 'paragraph')
                    current_id_paragraph = get_new_id_paragraph(current_id_paragraph)
                    if current_id_paragraph is not None:
                        child_title.attrib['id'] = current_id_paragraph
                        current_id_subsection = current_id_paragraph + ".0"
                    child_title.attrib['name'] = " ".join(lines_accumulated).strip()
                    current_root = out_paper_root if id_lines_accumulated == 0 else child_title
            elif id_lines_accumulated == -1 and len(lines_accumulated) > 0 and \
                    len("".join(lines_accumulated).replace(" ", "")):  # create a subsection
                child_sub = ET.SubElement(current_root, 'subsection')
                current_id_subsection = get_new_id_paragraph(current_id_subsection)
                if current_id_subsection is not None: child_sub.attrib['id'] = current_id_subsection
                child_sub.text = " ".join(lines_accumulated).replace("- ", "")
            lines_accumulated = [line[1]]
            id_lines_accumulated = line[0]
        else:  # accumulate line
            lines_accumulated.append(line[1])
            id_lines_accumulated = line[0]
            if lines_accumulated[-1].endswith('.'):  # create a subsection
                child_sub = ET.SubElement(current_root, 'subsection')
                current_id_subsection = get_new_id_paragraph(current_id_subsection)
                if current_id_subsection is not None: child_sub.attrib['id'] = current_id_subsection
                child_sub.text = " ".join(lines_accumulated).replace("- ", "")
                lines_accumulated = []

    return out_paper_root


def parse_txt(out_paper_root, txt_file_lines, title_paper, paragraph_titles, **kwargs):
    """
    parse_txt() reads the txt_file and builds the xml_analyzable for the output, using the information extracted from
    the temporary_xml (such as title_paper and paragraph_titles).
    :param out_paper_root: root of the xml_analyzable
    :param txt_file_lines: all the lines of input txt
    :param title_paper: the paper's title (passed as argument or extracted from the temporary_xml)
    :param paragraph_titles: the paper's paragraph titles (extracted from the temporary_xml), with the associated pages
    :param kwargs: logger' for logging
    :return: the built and analyzable xml Tree, otherwise None
    """
    logger = kwargs['logger'] if 'logger' in kwargs else None
    page_for_title = kwargs['page_for_title'] if 'page_for_title' in kwargs else None
    # in txt_lines_informative, -1 means that it is an usual line
    txt_lines_informative = []
    txt_lines = []
    for line in txt_file_lines:
        line_tmp = re.sub("[^0-9a-zA-Z\\s]", " ", line).lower()
        line_tmp = re.sub("\\s+|\\n|\\v|\\f", " ", line_tmp).strip()
        txt_lines.append(line_tmp)
        txt_lines_informative.append([-1, line.replace('\n', '').replace('\v', ' ').replace('\f', ' ')])

    xml_titles = []
    l = [title_paper]
    l.extend(paragraph_titles)
    for title in l:
        title_tmp = re.sub("[^0-9a-zA-Z\\s]", " ", replace_special_chars_xml(title)).lower()
        title_tmp = re.sub("\\s+|\\n|\\v|\\f", " ", title_tmp).strip()
        xml_titles.append(title_tmp)

    txt_text_tmp = "|" + "|".join(txt_lines) + "|"
    txt_text = " " + " ".join(txt_lines) + " "
    print(txt_text_tmp)
    print(txt_text)
    print(txt_lines)
    start_index_informative = 0
    for i, title in enumerate(xml_titles):
        index_title = txt_text.find(title)
        if index_title == -1:
            if i == 0:  # paper title not found.. try to extract
                print_message(logger, logging.FATAL, 'Paper title "' + title + '" not found in txt.')
                if page_for_title is None:
                    return None
                else:
                    print_message(logger, logging.INFO, 'Trying to extract a new paper title.')
                    title, _ = get_title(page_for_title, logger=logger)
                    title = re.sub("[^0-9a-zA-Z\\s]", " ", replace_special_chars_xml(title)).lower()
                    title = re.sub("\\s+|\\n", " ", title).strip()
                    index_title = txt_text.find(title)
                    if index_title == -1:
                        print_message(logger, logging.FATAL, 'Extracted paper title "' + title + '" not found in txt.')
                        return None
            else:
                print_message(logger, logging.FATAL, 'Paragraph title "' + title + '" not found in txt.')
                return None

        ###########
        title_found = False
        while title_found is False:
            first_index = txt_text_tmp[:index_title].rfind("|")
            title_lines = txt_text_tmp[first_index:index_title + len(title)].split(sep="|")
            # ex: ['', '4 how fast is fast sgd analysis of step', 'mini batch sizes and computational', 'efficiency for quadratic loss']
            title_lines = title_lines[1:]
            full_search = False
            if len(title_lines) == 1:
                try:
                    index_informative = txt_lines.index(title, start_index_informative)
                    txt_lines_informative[index_informative][0] = i
                    start_index_informative = index_informative + 1
                    title_found = True
                except ValueError as e:
                    print_message(logger, logging.DEBUG, '"' + title + '" not found. Proceeding with a full search..')
                    full_search = True
            if len(title_lines) > 1 or full_search is True:
                i_list = []
                for line in title_lines:
                    try:
                        index_informative = txt_lines.index(line, start_index_informative)
                        i_list.append(index_informative)  # txt_lines_informative[index_informative][0] = i
                        start_index_informative = index_informative + 1
                        print_message(logger, logging.DEBUG, 'Title line "' + line + '" found for the title "' + title +
                                      '", from the index ' + str(start_index_informative) + '.')
                        title_found = True
                    except ValueError as e:
                        print_message(logger, logging.DEBUG, 'Title line "' + line +
                                      '" not found in list for the title "' + title + '", but has matched with: [' +
                                      " ".join(title_lines) + "]")
                        index_title_tmp = txt_text_tmp.find(title + "|", index_title + 1)
                        if index_title_tmp == -1:
                            print_message(logger, logging.FATAL, 'Title line "' + title + '" not found in txt.')
                            return None
                        if index_title != index_title_tmp:
                            index_title = index_title_tmp
                            i_list = []
                            title_found = False
                            break
                for i_list_i in i_list:
                    txt_lines_informative[i_list_i][0] = i
        ###########

    # fix this paragraph title: ex. "Abstract. Labeled data for classification could often be obtained by sampling"
    found = list(filter(lambda x: (str(x[1]).strip().lower().startswith("abstract") and
                                   str(x[1]).strip()[len("abstract"):].strip().split(sep=" ")[0]
                                   in string.punctuation)
                        , [i for i in txt_lines_informative if i[0] >= 0]))
    if len(found) > 0:
        i_abstract = txt_lines_informative.index(found[0])
        txt_lines_informative.insert(i_abstract + 1,
                                     [-1, txt_lines_informative[i_abstract][1][len("abstract"):].strip()[1:].strip()])
        txt_lines_informative[i_abstract][1] = found[0][1][:len("abstract")]

    # Check that all paragraph titles are found:
    print_message(logger, logging.INFO, "Titles matched:\n\t- " +
                  "\n\t- ".join([str(i[0]) + "# " + i[1].strip() for i in txt_lines_informative if i[0] >= 0]))

    # create paragraph and subsection
    id_paper = None if 'id' not in out_paper_root.attrib else out_paper_root.attrib['id']
    current_id_paragraph = None if id_paper is None else id_paper + ".-1"
    current_id_subsection = None if current_id_paragraph is None else current_id_paragraph + ".0"
    current_root = out_paper_root
    lines_accumulated = []
    id_lines_accumulated = -1
    for line in txt_lines_informative:
        if line[0] != id_lines_accumulated:  # create a child
            if id_lines_accumulated >= 0:  # create a paragraph
                if current_root.tag == 'paragraph' and len(
                        current_root.findall("./subsection")) == 0:  # merge the paragraphs
                    current_root.attrib['name'] = current_root.attrib['name'] + " " + " ".join(
                        lines_accumulated).strip()
                else:
                    child_title = ET.SubElement(out_paper_root, 'title' if id_lines_accumulated == 0 else 'paragraph')
                    current_id_paragraph = get_new_id_paragraph(current_id_paragraph)
                    if current_id_paragraph is not None:
                        child_title.attrib['id'] = current_id_paragraph
                        current_id_subsection = current_id_paragraph + ".0"
                    child_title.attrib['name'] = " ".join(lines_accumulated).strip()
                    current_root = out_paper_root if id_lines_accumulated == 0 else child_title
            elif id_lines_accumulated == -1 and len(lines_accumulated) > 0 and \
                    len("".join(lines_accumulated).replace(" ", "")):  # create a subsection
                child_sub = ET.SubElement(current_root, 'subsection')
                current_id_subsection = get_new_id_paragraph(current_id_subsection)
                if current_id_subsection is not None: child_sub.attrib['id'] = current_id_subsection
                child_sub.text = " ".join(lines_accumulated).replace("- ", "")
            lines_accumulated = [line[1]]
            id_lines_accumulated = line[0]
        else:  # accumulate line
            lines_accumulated.append(line[1])
            id_lines_accumulated = line[0]
            if lines_accumulated[-1].endswith('.'):  # create a subsection
                child_sub = ET.SubElement(current_root, 'subsection')
                current_id_subsection = get_new_id_paragraph(current_id_subsection)
                if current_id_subsection is not None: child_sub.attrib['id'] = current_id_subsection
                child_sub.text = " ".join(lines_accumulated).replace("- ", "")
                lines_accumulated = []

    return out_paper_root
