import os
import sys
import subprocess
import logging

logging.basicConfig(filename='./log_process_papers.log', level=logging.DEBUG)

if __name__ == '__main__':

    if len(sys.argv) > 3:
        print("Error: too much arguments.\nUsage:\n"
              "\tpython process_all_papers.py [directory_papers] [papers_to_process_list.txt]\n")
        sys.exit(1)
    elif len(sys.argv) < 3:
        print("Error: missing arguments.\nUsage:\n"
              "\tpython process_all_papers.py [directory_papers] [papers_to_process_list.txt]\n")
        sys.exit(1)
    else:
        dir_papers_path = sys.argv[1]
        if not os.path.isdir(dir_papers_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython process_all_papers.py [directory_papers] [papers_to_process_list.txt]\n"
                  % dir_papers_path)
            sys.exit(2)
        papers_list_path = sys.argv[2]
        if not os.path.isfile(papers_list_path):
            print("Error: %s not exist.\n"
                  "Usage:\n\tpython process_all_papers.py [directory_papers] [papers_to_process_list.txt]\n"
                  % papers_list_path)
            sys.exit(2)

    # Processing:
    paper_line_list = []
    with open(papers_list_path, 'r') as in_file:
        paper_line_list = in_file.readlines()

    # output file:
    out_file_1 = "./papers_processed.txt"
    out_file_2 = "./papers_not_processed.txt"

    with open(out_file_1, "w") as out_1, open(out_file_2, "w") as out_2:
        for paper_line in paper_line_list:
            info_paper = paper_line.split("\t\t")
            path_dir = os.path.join(dir_papers_path, "paper_" + info_paper[0])
            if os.path.isdir(path_dir):
                paper_xml_path = os.path.join(path_dir, 'paper_' + info_paper[0] + '.xml')
                paper_txt_path = os.path.join(path_dir, 'paper_' + info_paper[0] + '.txt')
                args = ["python3", "process_paper.py", "-i", info_paper[0], "-u", info_paper[1],
                        "-t", info_paper[2].replace('\n', ''), paper_xml_path, paper_txt_path]
                process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                try:
                    exit_code = process.wait(timeout=30)
                    if exit_code == 0:
                        out_1.write(paper_line)
                    else:
                        out_2.write(paper_line)
                        logging.error(
                            'Processing paper "%s" terminated, with exit-code = %s.' % (info_paper[0], exit_code))
                except subprocess.TimeoutExpired:
                    process.terminate()
                    logging.error('Processing paper "%s" terminated, cause loop.' % info_paper[0])
                    out_2.write(paper_line)
            else:
                logging.error('Directory "%s" for paper %s not found.' % (path_dir, info_paper[0]))
