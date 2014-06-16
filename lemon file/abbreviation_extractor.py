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
import re

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
    infile = './../DBpedia/'+language+'/data/redirects_en.ttl'  #location of input file
    outfile = 'abbreviation_extracted.txt'  #output file
    lemon_file = 'abbreviation_lemon_'+language+'.ttl'  #lemon file
    input_file = open(infile,'r')
    output = open(outfile,'w')
    lemon = open(lemon_file,'w')
    abbrevs = collections.OrderedDict()
    output.write("Abbreviation\tDefinition\tLabel\tReference Link\towl:sameAS\n")
    lemon.write("@prefix : <http://www.example.org/lexicon> .\n@prefix lemon: <http://www.monnetproject.eu/lemon#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf- syntax-ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n\n")
    lemon.write('\n:myLexicon a lemon:Lexicon ;\n\tlemon:language "'+language+'" ;\n')
    count = 0
    count_line=0
    for line in input_file:
        #if count_line == 2:
        	#break
        #count_line+=1
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
            #___print("values ",values)

            if len(values) > 0:
                for k,v in values.items():
                    abbrevs[k] = v
                    abbrevs[k].insert(0,uris[0][1:-1])
                    #print(k,"\t-----disamb-----",abbrevs[k])
                continue

            else:
                if abbrev not in abbrevs:
                    #print ("here")
                    #s1=input("enter")
                    data = getOriginalLanguageData(abbrev, uris[2][1:-1])
                    #print(data)
                    if len(data) > 0:
                        abbrevs[abbrev] = data
                        abbrevs[abbrev].insert(0,uris[0][1:-1])		#inserts the original link in the dictionary at pos 0
                        #print(abbrev,"\t----no disamb-----",abbrevs[abbrev])
                else:
                    print("already in " + abbrev +" " + uris[0])
                    abbrevs[abbrev][0] = abbrevs[abbrev][0] + " | " + meaning
    entry_var=""
    check_abbr = [] #list to check for occurrences of disambiguations when writing lemon:entry :*_Entry .
    #------this loop will make entry string of form lemon:entry :AA_Entry , BC_Entry .--------
    for k,v in abbrevs.items():
        temp=k.split(" ")[0] #fetches the abbreviation term
        if temp in check_abbr:
                continue
        check_abbr.append(temp)
        temp=":"+re.sub("\.|\?|!","",temp)+"_Entry" #replaces .,? or !
        entry_var += temp + ", "
    entry_var = "lemon:entry " + entry_var[:-2] + " .\n\n"
    lemon.write("\t"+entry_var)

    for k,v in abbrevs.items():
        abbrevString = k.split(" ")[0]  #stores abbreviation in abbrevString
        if k[-1]=='.' or k[-1]=='?' or k[-1]=='!' or k.split(" ")[1]=='1':
                string_to_write = "<"+abbrevString+"_Entry>\n\tlemon:form <"+abbrevString+"_Form> ;\n\tlemon:sense "
                for temp_abbr,v1 in abbrevs.items():
                	if temp_abbr.split(" ")[0]==abbrevString and (temp_abbr[-1]!='.' and temp_abbr[-1]!='?' and temp_abbr[-1]!='!'):
                                string_to_write += "<" + temp_abbr.split(" ")[0] + "_Sense" + temp_abbr.split(" ")[1] + ">, "
                	elif temp_abbr.split(" ")[0]==abbrevString and (temp_abbr[-1]=='.' or temp_abbr[-1]=='?' or temp_abbr[-1]=='!'):
                                string_to_write += "<" + temp_abbr.split(" ")[0] + "_Sense>, "
                string_to_write = string_to_write[:-2]+' ;\n\ta lemon:LexicalEntry .\n\n<'+abbrevString+'_Form>\n\tlemon:writtenRep \"'+abbrevString+'\"@'+language+' ;\n\ta lemon:LexicalForm .\n\n'
                lemon.write(string_to_write)
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
        if k[-1]!='.' and k[-1]!='?' and k[-1]!='!':
                k1 = k.split(" ")[1]
        elif k[-1]=='.' or k[-1]=='?' or k[-1]=='!':
                k1 = ""
        definition = "<"+abbrevString+"_Sense"+k1+">\n\tlemon:definition [\n\t\tlemon:value "+'"'+v[1]+'"@'+language+"\n\t] ;\n\t" #def
    	#rdf_type = "rdf:type " + v[3] + " ;\n\t"		#instance types
        label = 'rdfs:label "' + v[1] + '" ;\n\t'		#label					
    	#category = "dcterms:subject " + cat + " ;\n\t"		#Categories
        if len(sameAs_string) > 0:
                owl_sameAs = "owl:sameAs " + sameAs_string + " ;\n\t"	#interlanguage links containing "dbpedia"
        ref = "lemon:reference " + v[2] + " ;\n\ta lemon:LexicalSense .\n\n"	#reference
        sense = definition + label + owl_sameAs + ref	
        lemon.write(sense)
    output.close()
    lemon.close()

if __name__ == "__main__":
    main(sys.argv[1:])
