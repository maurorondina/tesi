# Information

## Download papers

1. Run [download_papers.py](./download_papers.py) to download all the downloadable papers in pdf. It produces different out files containing lists of downloaded papers. (note: those of 'arxiv.org' are excluded)
2. Run [download_arxiv_papers.py](./download_arxiv_papers.py) to download all the downloadable arxiv papers in pdf. It produces an out file containing a list of downloaded papers. It uses a constantly updated list of free proxy servers. (note: the estimated time to download all the papers is one month)
3. Otherwise run [download_arxiv_papers_vpn.py](./download_arxiv_papers_vpn.py) to download all the downloadable arxiv papers in pdf with ExpressVPN. It also produces an out file. (note: the estimated time to download all the papers is a few days). Please download [ExpressVPN](https://www.expressvpn.com) and the python [wrapper](https://github.com/philipperemy/expressvpn-python). (note: I suggest few wrapper [modifications](./modfications_express-vpn.txt) to have more ip addresses)

## Convert papers
4. Prepare a single list of the pdf papers you want to transform starting from the previously generated out files. Run [transform_pdf.py](transform_pdf.py) to convert pdf papers to xml and txt format. It uses 'pdftohtml' and 'pdftotext' in [Poppler](http://poppler.freedesktop.org) library. It produces a 'LIST_PAPERS.txt' containing a list of converted papers such as [this](../data/LIST_PAPERS.txt) and it structures a folder, passed as an argument, as 'papers' in [data](../data).
5. 
