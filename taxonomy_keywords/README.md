# Information

## Create Taxonomy

1. I created a [taxonomy](./resources/taxonomy.json) to group the arxiv papers. To this end, the [get_category_arxiv.py](./get_category_arxiv.py) file can be used to retrieve the information of the various categories.
2. Run [get_subjects_arxiv_papers_vpn.py](./get_subjects_arxiv_papers_vpn.py) to retrieve all the subjects of each arxiv paper. It generates [papers_subjects.json](./resources/papers_subjects.json). (note: each a subject has a correspondent in [taxonomy.json](./resources/taxonomy.json))
3. Similarly, run [get_info_arxiv_papers_vpn.py](./get_info_arxiv_papers_vpn.py) to retrieve information of each arxiv paper. It generates [papers_info.json](./resources/papers_info.json).

## Retrieve keywords from papers

1. Run [find_papers_with_keywords.py](./find_papers_with_keywords.py) to generate a [list](./resources/LIST_PAPERS_keywords.txt) of arxiv papers containing keywords and/or CCS CONCEPTS.
2. Run [extract_keywords.py](./extract_keywords.py) to extract keywords and/or CCS CONCEPTS from arxiv papers in pdf. It generates the file [papers_keywords.json](./resources/papers_keywords.json) containing information that for some papers is inaccurate. (note: some information is extracted incorrectly due to the diversity of the papers)
3. In order to extract all the keywords correctly, in the [fix_keywords.py](./fix_keywords.py) there are pieces of code that try to extract the keywords of a subset of papers. Each attempt must be checked for correctness. (note: I suggest using regular expression)

## Predict subjects for paper

In file [simplified_taxonomy](./predict_subjects/simplified_taxonomy.ipynb) a simplified taxonomy with 56 subjects is created.

1. In the file [datasetPaperSubject](./predict_subjects/datasetPaperSubject.ipynb) you see the relationship between all arxiv papers and the subjects of the taxonomy. You also prepare a text-clean dataset useful for prediction.
2. In the file [predictSubject](./predict_subjects/predictSubject.ipynb) the subjects are predicted for each arxiv paper. To this end, several attempts are made with different classifiers.

| METHOD | num_subjects | train_score | test_score |
|--------|:------------:|:-----------:|:----------:|
| **OneVsRest - Multinomial NB** | 133 | 0.506 | 0.489 |
| **OneVsRest - Multinomial NB** | 56 | 0.508 | 0.491 |
| **OneVsRest - Linear SVC** | 133 | 0.786 | 0.513 |
| **OneVsRest - Linear SVC** | 56 | 0.787 | 0.517 |
| **OneVsRest - Logistic Regression** | 133 | 0.572 | 0.518 |
| **OneVsRest - Logistic Regression** | 56 | 0.576 | 0.521 |

1. In the file [datasetPaperKeywordsSubject](./predict_subjects/datasetPaperKeywordsSubject.ipynb) you see the relationship between arxiv papers with keywords and the subjects of the taxonomy. You also prepare a text-clean dataset useful for prediction.
2. In the file [predictSubject_k](./predict_subjects/predictSubject_k.ipynb) the subjects are predicted for each arxiv paper with keywords. To this end, several attempts are made with different classifiers.

| METHOD | num_subjects | train_score | test_score |
|--------|:------------:|:-----------:|:----------:|
| **OneVsRest - Multinomial NB** | 114 | 0.545 | 0.529 |
| **OneVsRest - Multinomial NB** | 56 | 0.545 | 0.529 |
| **OneVsRest - Linear SVC** | 114 | 0.880 | 0.550 |
| **OneVsRest - Linear SVC** | 56 | 0.881 | 0.552 |
| **OneVsRest - Logistic Regression** | 114 | 0.602 | 0.554 |
| **OneVsRest - Logistic Regression** | 56 | 0.604 | 0.556 |

1. In files [create_intersting_arxiv_Dataset](./predict_subjects/create_intersting_arxiv_Dataset.ipynb) and [create_intersting_arxiv_textclean_Dataset](./predict_subjects/create_intersting_arxiv_textclean_Dataset.ipynb) two datasets are created, one of which is text-clean, and they contain all the interesting paragraphs of all analyzable arxiv papers.
A paragraph was considered "interesting" if:
	- it is a "problem description"
	- at least one subsection of it has been predicted as a "problem description"
	- its title belongs to a group of standard titles that are used to understand the context and information on the paper's problem.
2. In the file [predictSubject_interesting](./predict_subjects/predictSubject_interesting.ipynb) the subjects are predicted for each analyzable arxiv paper. To this end, several attempts are made with different classifiers.

| METHOD | num_subjects | train_score | test_score |
|--------|:------------:|:-----------:|:----------:|
| **OneVsRest - Multinomial NB** | 121 | 0.501 | 0.485 |
| **OneVsRest - Multinomial NB** | 56 | 0.502 | 0.486 |
| **OneVsRest - Linear SVC** | 121 | 0.861 | 0.507 |
| **OneVsRest - Linear SVC** | 56 | 0.858 | 0.509 |
| **OneVsRest - Logistic Regression** | 121 | 0.559 | 0.510 |
| **OneVsRest - Logistic Regression** | 56 | 0.562 | 0.511 |

## HLTA

1. Use [HLTA](https://github.com/kmpoon/hlta) to extract topics for paper with keywords. 


##### Important Resources:
- [taxonomy](./resources/taxonomy.json)
- [simplified taxonomy](./resources/taxonomy-56.json)
- [paper and subjects](./resources/papers_subjects.json) (for all arxiv papers: 37368)
- [paper and information](./resources/papers_info.json) (for all arxiv papers: 37368)
- [paper and keywords](./resources/papers_keywords.json) (for all arxiv papers that have explicit keywords: 15118)
- [topic_cv](./hlta_arxiv_auto_3000_cv/arxiv.html) (for all arxiv documents that have explicit keywords belonging to the subject 'cs.CV': 7872)
- [topic_others](./hlta_arxiv_auto_3000_others/arxiv.html) (for all arxiv documents that have explicit keywords belonging to the other subjects: 7246)
