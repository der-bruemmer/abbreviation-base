Abbreviation Base
=================

Goal of this project is to aggregate abbreviations from DBpedia into a multilingual linked open data dictionary.


# Initial files

Use DBpedia redirects as initial resources:

```
curl  http://downloads.dbpedia.org/3.9/en/redirects_en.ttl.bz2 | bzcat | grep "<http://dbpedia.org/resource/.*\.> <.*> <.*>" > abbrev_en.ttl
```

Loads all DBpedia redirect triples that end with a period, like this:

```
<http://dbpedia.org/resource/A.D.> <http://dbpedia.org/ontology/wikiPageRedirects> <http://dbpedia.org/resource/Anno_Domini> .
```

These come in two flavours. First one redirects the resource, i.e. "A.D.", to a page that contains the meaning of the resource, i.e. "Anno_Domini". The second one, for example in this triple:

```
<http://dbpedia.org/resource/A.I.> <http://dbpedia.org/ontology/wikiPageRedirects> <http://dbpedia.org/resource/Ai> .
```

links the abbreviation resource to a page that contains a number of disambiguation links, because the abbreviation has more than one meaning. This distinction is important when we want to build our knowledge base later.

# Processing via python

The python script is used to further process the abbreviation data we extracted via curl:

```
python3 extractAbbrevs_en.py -i abbrev_en.ttl -o abbrevs_en.tsv
```

It uses the SPARQLWrapper (http://www.ivan-herman.net/Misc/PythonStuff/SPARQL/Doc-SPARQL/) package to query DBpedia for further information on the resources.

# Output data format

The data output at the moment is a TSV with this format:

```
Entry example	Full entry name	Example tested	IsException	Usage Frequency	abbrevLink	Definition link-en	Abstract-en
```

With "Example tested", "IsException" and "Usage Frequency" being empty fields, because this is a legacy script. Final format will be in RDF modelled with Lemon (http://lemon-model.net).
