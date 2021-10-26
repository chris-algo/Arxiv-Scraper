import urllib.request as libreq
import xmltodict
with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
    results = url.read()
results_dict = xmltodict.parse(results)