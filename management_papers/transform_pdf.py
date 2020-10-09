import subprocess
import os
import shutil
import logging
import sys

# print(requests.__version__)

logging.basicConfig(filename='./log_transform_pdf.log', level=logging.DEBUG)


def transform_pdf_xml(paper_id, paper_pdf_path, dir_xml):
    """ Function to transform a paper in pdf to xml format.

        Parameters
        ----------
        paper_id : str
            The paper id.
        paper_pdf_path : str
            The path of the paper in pdf format.
        dir_xml : string
            Save folder for the paper in xml format.

        Returns
        -------
        True if paper is saved, False otherwise."""

    pdftohtml = subprocess.getoutput("which pdftohtml")
    paper_xml_path = os.path.join(dir_xml, 'paper_' + paper_id + '.xml')
    args = [pdftohtml, "-i", "-q", "-xml", paper_pdf_path, paper_xml_path]
    process = subprocess.Popen(args)
    process.wait()
    # check XML file:
    return True if os.path.isfile(paper_xml_path) else False


def transform_pdf_txt(paper_id, paper_pdf_path, dir_txt):
    """ Function to transform a paper in pdf to txt format.

        Parameters
        ----------
        paper_id : str
            The paper id.
        paper_pdf_path : str
            The path of the paper in pdf format.
        dir_txt : string
            Save folder for the paper in txt format.

        Returns
        -------
        True if paper is saved, False otherwise."""

    pdftotext = subprocess.getoutput("which pdftotext")
    paper_txt_path = os.path.join(dir_txt, 'paper_' + paper_id + '.txt')
    args = [pdftotext, "-raw", "-q", paper_pdf_path, paper_txt_path]
    process = subprocess.Popen(args)
    process.wait()
    # check TXT file:
    return True if os.path.isfile(paper_txt_path) else False


if __name__ == '__main__':

    if len(sys.argv) > 4:
        print("Error: too much arguments.\nUsage:\n"
              "\tpython transform_pdf.py [directory_path_pdf] [directory_papers] [papers_to_convert_list.txt]\n")
        sys.exit(1)
    elif len(sys.argv) < 4:
        print("Error: missing arguments.\nUsage:\n"
              "\tpython transform_pdf.py [directory_path_pdf] [directory_papers] [papers_to_convert_list.txt]\n")
        sys.exit(1)
    else:
        dir_pdf_path = sys.argv[1]
        if not os.path.isdir(dir_pdf_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython transform_pdf.py [directory_path_pdf] [directory_papers]"
                  " [papers_to_convert_list.txt]\n" % dir_pdf_path)
            sys.exit(2)
        dir_papers_path = sys.argv[2]
        if not os.path.isdir(dir_papers_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython transform_pdf.py [directory_path_pdf] [directory_papers]"
                  " [papers_to_convert_list.txt]\n" % dir_papers_path)
            sys.exit(2)
        papers_list_path = sys.argv[3]
        if not os.path.isfile(papers_list_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython transform_pdf.py [directory_path_pdf] [directory_papers]"
                  " [papers_to_convert_list.txt]\n" % papers_list_path)
            sys.exit(2)


    # output file:
    out_file = open("./LIST_PAPERS.txt", "w", buffering=1)

    # Conversion:
    with open(papers_list_path, 'r') as paper_list_file:

        while True:
            # Get next line from file
            line = paper_list_file.readline()
            # if line is empty, end of file is reached
            if line == "":
                logging.info("EOF reached. Bye...")
                break
            # Processing line: _id , url , title
            info_paper = line.split("\t\t")
            name_pdf = 'paper_' + info_paper[0] + '.pdf'

            # Check if paper pdf is downloaded
            paper_pdf_path = os.path.join(dir_pdf_path, name_pdf)
            if not os.path.isfile(paper_pdf_path):
                logging.error("Paper '%s': not found in directory %s." % (name_pdf, dir_pdf_path))

            # Create output directory for the paper
            dir_paper = os.path.join(dir_papers_path, 'paper_' + info_paper[0])
            try:
                os.mkdir(dir_paper)
            except OSError:
                logging.error("Paper %s: Creation of the directory %s failed." % (info_paper[0], dir_paper))
                continue

            # Invoke subprocess PDF->XML
            created_xml = transform_pdf_xml(info_paper[0], paper_pdf_path, dir_paper)
            if not created_xml:
                logging.error("Paper %s: Transformation in XML failed." % info_paper[0])

            # Invoke subprocess PDF->TXT
            created_txt = transform_pdf_txt(info_paper[0], paper_pdf_path, dir_paper)
            if not created_txt:
                logging.error("Paper %s: Transformation in TXT failed." % info_paper[0])

            # Save conversion
            if created_xml and created_txt:
                out_file.write(line)
            else:
                try:
                    shutil.rmtree(dir_paper)
                except Exception as e:
                    logging.error("%s not deleted." % dir_paper)
                else:
                    logging.info("%s deleted." % dir_paper)

        out_file.close()