# -*- coding: utf-8 -*-
import sys, getopt, os, collections 
from SPARQLWrapper import SPARQLWrapper, JSON

def getDisambiguations(abbrev, uri):
    query = "select distinct ?o, (str(?name) AS ?label), (str(?abstract) AS ?en_abstr) where {"+uri+" <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o. ?o <http://www.w3.org/2000/01/rdf-schema#label> ?name. FILTER(langMatches(lang(?name), \"EN\")) OPTIONAL {?o <http://dbpedia.org/ontology/abstract> ?abstract. FILTER(langMatches(lang(?abstract), \"EN\")) }}"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        abbrevs = collections.OrderedDict()
        count=1
        for result in results["results"]["bindings"]:
            abstract = ""
            if "en_abstr" in result:
                abstract = result["en_abstr"]["value"]
            abbrevs[abbrev+" "+str(count)] = [result["label"]["value"],result["o"]["value"],abstract]
            count+=1
        return abbrevs
    except ValueError:
        query = "select distinct ?o, (str(?name) AS ?label) where {"+uri+" <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o. ?o <http://www.w3.org/2000/01/rdf-schema#label> ?name. FILTER(langMatches(lang(?name), \"EN\"))}"
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        abbrevs = collections.OrderedDict()
        count=1
        for result in results["results"]["bindings"]:
            abbrevs[abbrev+" "+str(count)] = getOriginalLanguageData(abbrev, result["o"]["value"]) 
            count+=1
        return abbrevs

def getOriginalLanguageData(abbrev, uri):
    query = "select distinct (str(?name) AS ?label), (str(?abstract) AS ?en_abstr) where {<"+uri+"> <http://www.w3.org/2000/01/rdf-schema#label> ?name. FILTER(langMatches(lang(?name), \"EN\")) OPTIONAL {<"+uri+"> <http://dbpedia.org/ontology/abstract> ?abstract. FILTER(langMatches(lang(?abstract), \"EN\")) }}"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        data = []
        for result in results["results"]["bindings"]:
            abstract = ""
            if "en_abstr" in result:
                abstract = result["en_abstr"]["value"]
            data = [result["label"]["value"],uri,abstract]
        return data
    except ValueError:
        data = [uri[uri.rfind("/")+1:-1].replace("_"," "),uri,""]
        return data


def only_roman_chars(s):
    try:
        s.encode("iso-8859-1")
        return True
    except UnicodeEncodeError:
        return False

def main(argv):
    infile = ''
    outfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError as err:
        print('extractAbbrevs.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: extractAbbrevs.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i","--infile"):
            infile = arg
        elif opt in ("-o","--outfile"):
            outfile = arg
        else:
            print('Usage: extractAbbrevs -i <inputfile> -o <outputfile>')
            sys.exit()

    input = open(infile,'r')
    if os.path.exists(outfile):
        os.remove(outfile)
    output = open(outfile,'a')
    abbrevs = collections.OrderedDict()
    output.write("Entry example\tFull entry name\tExample tested\tIsException\tUsage Frequency\tabbrevLink\tDefinition link-en\tAbstract-en\n")
    count = 0
    for line in input:
        uris = line.split(" ")
        abbrev = uris[0][uris[0].rfind("resource/")+9:-1]
        if not only_roman_chars(abbrev):
            continue
        if abbrev.endswith("..."):
            continue
        meaning = uris[2][uris[2].rfind("/")+1:-1]
        meaningURI = uris[2]
        if "_" not in abbrev:
            count+=1
            value = [ meaning.replace("_"," "), uris[0][1:-1], meaningURI[1:-1]]
            #if "disambiguation" in meaning:
            values = getDisambiguations(abbrev, uris[2])
            if len(values) > 0:
                for k,v in values.items():
                    abbrevs[k] = v
                    abbrevs[k].insert(1,uris[0][1:-1])
                continue
            else:
                if abbrev not in abbrevs:
                    data = getOriginalLanguageData(abbrev, value[2])
                    if len(data) > 0:
                        abbrevs[abbrev] = data
                        abbrevs[abbrev].insert(1,uris[0][1:-1])
                else:
                    print("already in " + abbrev +" " + uris[0])
                    abbrevs[abbrev][0] = abbrevs[abbrev][0] + " | " + meaning
    print(str(count)+" abbreviations without whitespace")
    for k,v in sorted(abbrevs.items()):
        abbrevString = k.split(" ")[0]
        output.write(abbrevString+"\t"+v[0]+"\t\t\t\t"+v[1]+"\t"+v[2]+"\t"+v[3].replace("\t"," ").replace("\n"," ")+"\n")

 #       abbrev = abbrev.replace("_"," ")
#        abbrev = abbrev.split(" ")
  #      abbrev = abbrev[len(abbrev)-1]
        

if __name__ == "__main__":
    main(sys.argv[1:])
