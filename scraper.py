import urllib.request as libreq
import xmltodict
import json
import os
import time
import requests


def paper_to_json_file(paper_dict, json_dir):
    json_dir = os.path.join(
        json_dir, paper_dict["published"][:4], paper_dict["published"][5:7])
    os.makedirs(json_dir, exist_ok=True)
    json_file_path = os.path.join(json_dir, paper_dict["id"][21:] + '.json')
    print(json_file_path)

    with open(json_file_path, 'w') as f:
        print(json.dumps(paper_dict, indent=4), file=f)


def download_pdf(paper_id, save_dir):
    full_url = "http://arxiv.org/pdf/{}".format(paper_id)
    r = requests.get(full_url, allow_redirects=True)

    save_path = os.path.join(save_dir, paper_id + '.pdf')
    open(save_path, 'wb').write(r.content)
    

def main():

    results_per_iter = 2
    current_index = 0
    year = 2021
    wait_time = 3
    json_dir = "data/paper_json"
    pdf_dir = "data/paper_pdf"

    while year != 2014:
        query_url = 'http://export.arxiv.org/api/query?search_query=cs.ai&start={}&max_results={}&sortBy=submittedDate&sortOrder=descending'.format(
            current_index, results_per_iter)
        with libreq.urlopen(query_url) as url:
            results = url.read()
        results_dict = xmltodict.parse(results)

        for paper in results_dict["feed"]["entry"]:
            paper_to_json_file(paper, json_dir)

            year = paper["published"][:4]
            paper_id = paper["id"][21:]
            download_pdf(paper_id, pdf_dir)
            current_index += 1
            
        print(current_index)
        time.sleep(wait_time)


if __name__ == "__main__":
    main()
