#----input language in command line------


#----result["name"]["value"] ==> lemon:value "Michel van der Aa"@en
#----result["label"]["value"] ==> rdfs:label "Michel van der Aa"
#----result["o"]["value"] ==> lemon:reference <http://dbpedia.org/resource/Michel_van_der_Aa>
#----list_sameAs ==> owl:sameAs
#----list_type ==> rdf:type "but works only for abbreviations with disambiguations"
#----abbrev ==> writtenRep , stores abbrev
#----category  ==> yet to be fetched

#----------------Text file format----------------------
#abbreviation	definition	label	reference	sameAs(list format)
# P.S. type and category is not yet fetched completely so they have been omitted

import sys, getopt, os, collections 
from SPARQLWrapper import SPARQLWrapper, JSON

def getDisambiguations(abbrev, uri):
    query = "select distinct ?o, (str(?name) AS ?label), ?name, (str(?abstract) AS ?en_abstr) where {"+uri+" <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o. ?o <http://www.w3.org/2000/01/rdf-schema#label> ?name. FILTER(langMatches(lang(?name), \"EN\")) OPTIONAL {?o <http://dbpedia.org/ontology/abstract> ?abstract. FILTER(langMatches(lang(?abstract), \"EN\")) }}"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        abbrevs = collections.OrderedDict()
        count=1
        for result in results["results"]["bindings"]:

            #abstract = ""
            #if "en_abstr" in result:
                #abstract = result["en_abstr"]["value"]

            #fetch sameAs result for each disambiguation
            query_sameAs = 'select ?lang where {<'+result["o"]["value"]+'> owl:sameAs ?lang. filter(regex(?lang,"dbpedia"))}' 
            sparql.setQuery(query_sameAs)
            sparql.setReturnFormat(JSON)
            results_sameAs = sparql.query().convert()
  
            #fetch type for each disamb (but ignored for now)
            """query_type = 'select distinct ?type where {<'+result["o"]["value"]+'> rdf:type ?type. FILTER (REGEX(?type, "ontology") || REGEX(?type, "schema"))}' 
            sparql.setQuery(query_type)
            sparql.setReturnFormat(JSON)
            results_type = sparql.query().convert()
            list_type=[]"""

            list_sameAs=[]    #stores sameAs temporarily for each disambiguation
            for result_sameAs in results_sameAs["results"]["bindings"]:
                list_sameAs.append(result_sameAs["lang"]["value"])      #store the query result in a list

            """for result_type in results_type["results"]["bindings"]:
                list_type.append(result_type["type"]["value"])      #store the query result in a list"""

            #dictionary where key is abbreviation+count and value is label, reference link and sameAs fetched from query
            abbrevs[abbrev+" "+str(count)] = [result["label"]["value"],result["o"]["value"],list_sameAs]     #list_type]
            count+=1
        return abbrevs

    except ValueError:
        #control comes here if abbreviations does not has a disambiguation
        query = "select distinct ?o, (str(?name) AS ?label),?name where {"+uri+" <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o. ?o <http://www.w3.org/2000/01/rdf-schema#label> ?name. FILTER(langMatches(lang(?name), \"EN\"))}"
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        abbrevs = collections.OrderedDict()   #dictionary to store all the abbreviation as key and related information fetched as value
        count=1
        for result in results["results"]["bindings"]:
            abbrevs[abbrev+" "+str(count)] = getOriginalLanguageData(abbrev, result["o"]["value"])
            count+=1
        return abbrevs


def getOriginalLanguageData(abbrev, uri):
    query = "select distinct (str(?name) AS ?label), ?name, (str(?abstract) AS ?en_abstr) where {<"+uri+"> <http://www.w3.org/2000/01/rdf-schema#label> ?name. FILTER(langMatches(lang(?name), \"EN\")) OPTIONAL {<"+uri+"> <http://dbpedia.org/ontology/abstract> ?abstract. FILTER(langMatches(lang(?abstract), \"EN\")) }}"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        data = []
        for result in results["results"]["bindings"]:
            #abstract = ""
            #if "en_abstr" in result:
                #abstract = result["en_abstr"]["value"]
            query_sameAs = 'select ?lang where {<'+uri+'> owl:sameAs ?lang. filter(regex(?lang,"dbpedia"))}'   #fetch sameAs result for each abbreviation
            sparql.setQuery(query_sameAs)
            sparql.setReturnFormat(JSON)
            results_sameAs = sparql.query().convert()
            list_sameAs=[]
            for result_sameAs in results_sameAs["results"]["bindings"]:
                list_sameAs.append(result_sameAs["lang"]["value"])      #store the query result in a list
            #dictionary where key is abbreviation+count and value is label, reference link and sameAs fetched from query
            data = [result["label"]["value"],uri,list_sameAs]
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
    language=argv[0]
    infile = './DBpedia/'+language+'/data/redirects_en.ttl'  #location of input file
    outfile = 'abbreviation_extracted.txt'  #output file
    input_file = open(infile,'r')
    output = open(outfile,'w')
    abbrevs = collections.OrderedDict()
    output.write("Abbreviation\tDefinition\tLabel\tReference Link\towl:sameAS\n")
    count = 0
    count_line=0
    for line in input_file:
        #if count_line == 5:
        	#break
        count_line+=1
        uris = line.split(" ")		#splits the triple and stores is as list
        abbrev = uris[0][uris[0].rfind("resource/")+9:-1]    #stores abbreviation
        print(uris)
        if not only_roman_chars(abbrev):
            continue
        if abbrev.endswith("..."):
            continue
        #meaning = uris[2][uris[2].rfind("/")+1:-1]
        #meaningURI = uris[2][1:-1]
        if "_" not in abbrev:
            count+=1
            #value = [ meaning.replace("_"," "), uris[0][1:-1], meaningURI[1:-1]]
            #if "disambiguation" in meaning:
            values = getDisambiguations(abbrev, uris[2])

            if len(values) > 0:
                for k,v in values.items():
                    abbrevs[k] = v
                    abbrevs[k].insert(0,uris[0][1:-1])
                    #print(k,"\t-----disamb-----",abbrevs[k])
                continue

            else:
                if abbrev not in abbrevs:
                    data = getOriginalLanguageData(abbrev, uris[2][1:-1])
                    if len(data) > 0:
                        abbrevs[abbrev] = data
                        abbrevs[abbrev].insert(0,uris[0][1:-1])		#inserts the original link in the dictionary at pos 0
                        #print(abbrev,"\t----no disamb-----",abbrevs[abbrev])
                else:
                    print("already in " + abbrev +" " + uris[0])
                    abbrevs[abbrev][0] = abbrevs[abbrev][0] + " | " + meaning

    #print(str(count)+" abbreviations without whitespace")
    for k,v in sorted(abbrevs.items()):
        abbrevString = k.split(" ")[0]  #stores abbreviation in abbrevString
        #s1=input('Enter')
        sameAs_string = ','.join(v[3])  #converts sameAs from list to string format
        sameAs_string=sameAs_string.replace("http","<http")
        sameAs_string=sameAs_string.replace(",",">,")
        if len(sameAs_string)>0:
        	sameAs_string+='>'
        v[2]=v[2].replace("http","<http")
        v[2]+='>'
        print(abbrevString+"\t"+v[1]+"\t"+'"'+v[1]+'"@'+language+"\t"+v[2]+"\t"+sameAs_string+"\n")
        output.write(abbrevString+"\t"+v[1]+"\t"+'"'+v[1]+'"@'+language+"\t"+v[2]+"\t"+sameAs_string+"\n")
    output.close()

if __name__ == "__main__":
    main(sys.argv[1:])
