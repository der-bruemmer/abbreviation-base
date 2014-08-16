# Abbreviation Base – A multilingual knowledge base for abbreviations

This software extracts abbreviations and their meanings from DBpedia data dump files. It also extracts categories, types, interlanguage links and (if existent) disambiguations
Extracted data is modelled using the Lemon Ontology, and queryable via SPARQL. Additionally, TSV files are generated for easier consumption.  
It works for all 119 DBpedia languages.

The software consists of three files : 
* a [downloader script](https://github.com/der-bruemmer/abbreviation-base/blob/master/Final%20Files/download_extract.py) to download the source dump files
* an [extractor script](https://github.com/der-bruemmer/abbreviation-base/blob/master/Final%20Files/extractor_lemonMaker.py) to generate the abbreviation data
* a [shell script](https://github.com/der-bruemmer/abbreviation-base/blob/master/Final%20Files/abbrev_script.sh) to automate the task for a list of languages


[Software Documentation](https://github.com/der-bruemmer/abbreviation-base/blob/master/Final%20Files/software%20documentation/SoftwareDocumentation.pdf)

[User Guide](https://github.com/der-bruemmer/abbreviation-base/blob/master/Final%20Files/software%20documentation/User%20Guide.pdf)

[Sparql Endpoint](http://abbrevbase.aksw.org/sparql)

[Website](http://abbrevbase.aksw.org)

[Data Extracted](http://abbrevbase.aksw.org/data/)
