# Readme

## Arxiv API Notes

```
http://export.arxiv.org/api/{method_name}?{parameters}
example: 
http://export.arxiv.org/api/query?search_query=cs.ai&start=0&max_results=100
```

### Query Interface

| parameters     | type                   | defaults | required |
| -------------- | ---------------------- | -------- | -------- |
| `search_query` | string                 | None     | No       |
| `id_list`      | comma-delimited string | None     | No       |
| `start`        | int                    | 0        | No       |
| `max_results`  | int                    | 10       | No       |

### Sort Order

There are two options for for the result set to the API search, sortBy and sortOrder.

`sortBy` can be "relevance", "lastUpdatedDate", "submittedDate"

`sortOrder` can be either "ascending" or "descending"

A sample query using these new parameters looks like:

```
http://export.arxiv.org/api/query?search_query=ti:"electron thermal conductivity"&sortBy=lastUpdatedDate&sortOrder=ascending
```

### The API Response

summary example

```
<summary xmlns="http://www.w3.org/2005/Atom">
    Multi-electron production is studied at high electron transverse momentum
    in positron- and electron-proton collisions using the H1 detector at HERA.
    The data correspond to an integrated luminosity of 115 pb-1. Di-electron
    and tri-electron event yields are measured. Cross sections are derived in
    a restricted phase space region dominated by photon-photon collisions. In
    general good agreement is found with the Standard Model predictions.
    However, for electron pair invariant masses above 100 GeV, three
    di-electron events and three tri-electron events are observed, compared to
    Standard Model expectations of 0.30 \pm 0.04 and 0.23 \pm 0.04,
    respectively.
</summary>
```

author example

```
<author xmlns="http://www.w3.org/2005/Atom">
      <name xmlns="http://www.w3.org/2005/Atom">H1 Collaboration</name>
</author>
```

category example

```
<category xmlns="http://www.w3.org/2005/Atom" term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
<category xmlns="http://www.w3.org/2005/Atom" term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
<category xmlns="http://www.w3.org/2005/Atom" term="I.2.6" scheme="http://arxiv.org/schemas/atom"/>
```

link elements

| rel       | title | refers to     | always present |
|-----------|-------|---------------|----------------|
| alternate | -     | abstract page | yes            |
| related   | pdf   | pdf           | yes            |
| related   | doi   | resolved doi  | no             |

### Python example

```python
import urllib.request as libreq
with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
    r = url.read()
print(r)
```
