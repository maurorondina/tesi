# Information

## Create Taxonomy

1. I created a [taxonomy](./resources/taxonomy.json) to group the arxiv papers. To this end, the [get_category_arxiv.py](./get_category_arxiv.py) file can be used to retrieve the information of the various categories.
2. Run [get_subjects_arxiv_papers_vpn.py](./get_subjects_arxiv_papers_vpn.py) to retrieve all the subjects of each arxiv paper. It generates [papers_subjects.json](./resources/papers_subjects.json). (note: each a subject has a correspondent in [taxonomy.json](./resources/taxonomy.json))
3. Similarly, run [get_info_arxiv_papers_vpn.py](./get_info_arxiv_papers_vpn.py) to retrieve information of each arxiv paper. It generates [papers_info.json](./resources/papers_info.json).

## Retrieve keywords from papers

1. Run [find_papers_with_keywords.py](./find_papers_with_keywords.py) to generate a [list](./resources/LIST_PAPERS_keywords.txt) of arxiv papers containing keywords and/or CCS CONCEPTS.
2. Run [extract_keywords.py](./extract_keywords.py) to extract keywords and/or CCS CONCEPTS from arxiv papers in pdf. It generates the file [papers_keywords.json](./resources/papers_keywords.json) containing information that for some papers is inaccurate. (note: some information is extracted incorrectly due to the diversity of the papers)
3. In order to extract all the keywords correctly, in the [fix_keywords.py](./fix_keywords.py) there are pieces of code that try to extract the keywords of a subset of papers. Each attempt must be checked for correctness. (note: I suggest using regular expression)

## Visualize paper-subjects

1. In the file [datasetPaperSubject](./jup/datasetPaperSubject.ipynb) I see the relationship between all the papers and the subjects of the taxonomy.
2. In the file [datasetPaperKeywordsSubject](./jup/datasetPaperKeywordsSubject.ipynb) I see the relationship between papers with keywords and the subjects of the taxonomy.

## HLTA

1. Use [HLTA](https://github.com/kmpoon/hlta) to extract topics for paper with keywords. 


Recap:
	- [taxonomy](./resources/taxonomy.json)
	- [paper and subjects](./resources/papers_subjects.json) (for all arxiv papers: 37368)
	- [paper and information](./resources/papers_info.json) (for all arxiv papers: 37368)
	- [paper and keywords](./resources/papers_keywords.json) (for all arxiv papers that have explicit keywords: 15118)
	- [topic_cv](./hlta_arxiv_auto_3000_cv/arxiv.html) (for all arxiv documents that have explicit keywords belonging to the subject 'cs.CV': 7872)
	- [topic_others](./hlta_arxiv_auto_3000_others/arxiv.html) (for all arxiv documents that have explicit keywords belonging to the other subjects: 7246)
