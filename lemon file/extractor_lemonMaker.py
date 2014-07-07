#----input language in command line------

#----result["name"]["value"] ==> lemon:value "Michel van der Aa"@en
#----result["label"]["value"] ==> rdfs:label "Michel van der Aa"
#----result["o"]["value"] ==> lemon:reference <http://dbpedia.org/resource/Michel_van_der_Aa>
#----list_sameAs ==> owl:sameAs
#----list_type ==> rdf:type "but works only for abbreviations with disambiguations"
#----abbrev ==> writtenRep , stores abbrev
#----category  ==> <http://purl.org/dc/terms/subject> 

#----------------Text file format----------------------
#abbreviation	definition	label	reference	sameAs(list format)	type	category

import sys, getopt, os, collections 
from SPARQLWrapper import SPARQLWrapper, JSON
import re
global language
def getDisambiguations(abbrev, uri):
    global language
    query = "select distinct ?o, (str(?name) AS ?label), ?name where {"+uri+" <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o. ?o <http://www.w3.org/2000/01/rdf-schema#label> ?name.FILTER(langMatches(lang(?name), \""+language.upper()+"\")) }"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        abbrevs = collections.OrderedDict()
        count=1
        for result in results["results"]["bindings"]:

            #fetch sameAs result for each disambiguation
            query_sameAs = 'select ?lang where {<'+result["o"]["value"]+'> owl:sameAs ?lang. filter(contains(STR(?lang),"dbpedia"))}' 
            sparql.setQuery(query_sameAs)
            sparql.setReturnFormat(JSON)
            results_sameAs = sparql.query().convert()
  
            #fetch type for each disamb (but ignored for now)
            query_type = 'select distinct ?type where {<'+result["o"]["value"]+'> rdf:type ?type. FILTER (contains(STR(?type), "ontology") || contains(STR(?type), "schema"))}' 
            sparql.setQuery(query_type)
            sparql.setReturnFormat(JSON)
            results_type = sparql.query().convert()
            list_type=[]

            list_sameAs=[]    #stores sameAs temporarily for each disambiguation
            for result_sameAs in results_sameAs["results"]["bindings"]:
                list_sameAs.append(result_sameAs["lang"]["value"])      #store the query result in a list

            for result_type in results_type["results"]["bindings"]:
                list_type.append(result_type["type"]["value"])      #store the query result in a list

            query_cat = 'select distinct ?cat where {<'+result["o"]["value"]+'>  <http://purl.org/dc/terms/subject> ?cat }'
            sparql.setQuery(query_cat)
            sparql.setReturnFormat(JSON)
            results_cat = sparql.query().convert()
            
            list_cat=[]
            for result_cat in results_cat["results"]["bindings"]:
                list_cat.append(result_cat["cat"]["value"])

            #dictionary where key is abbreviation+count and value is label, reference link and sameAs fetched from query
            abbrevs[abbrev+" "+str(count)] = [result["label"]["value"],result["o"]["value"],list_sameAs,list_type,list_cat]
            count+=1
        return abbrevs

    except ValueError:
        #control comes here if abbreviations does not has a disambiguation
        query = "select distinct ?o, (str(?name) AS ?label),?name where {"+uri+" <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o. ?o <http://www.w3.org/2000/01/rdf-schema#label> ?name.FILTER(langMatches(lang(?name), \""+language.upper()+"\")) }"
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
    global language
    query = "select distinct (str(?name) AS ?label), ?name, (str(?abstract) AS ?en_abstr) where {<"+uri+"> <http://www.w3.org/2000/01/rdf-schema#label> ?name.FILTER(langMatches(lang(?name), \""+language.upper()+"\")) }"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        data = []
        for result in results["results"]["bindings"]:
            
            query_sameAs = 'select ?lang where {<'+uri+'> owl:sameAs ?lang. filter(regex(?lang,"dbpedia"))}'   #fetch sameAs result for each abbreviation
            sparql.setQuery(query_sameAs)
            sparql.setReturnFormat(JSON)
            results_sameAs = sparql.query().convert()
            list_sameAs=[]
            for result_sameAs in results_sameAs["results"]["bindings"]:
                list_sameAs.append(result_sameAs["lang"]["value"])      #store the query result in a list
            
            query_type = 'select distinct ?type where {<'+uri+'> rdf:type ?type. FILTER (REGEX(?type, "ontology") || REGEX(?type, "schema"))}' 
            sparql.setQuery(query_type)
            sparql.setReturnFormat(JSON)
            results_type = sparql.query().convert()
            list_type=[]

            for result_type in results_type["results"]["bindings"]:
                list_type.append(result_type["type"]["value"])      #store the query result in a list
           
            query_cat = 'select distinct ?cat where {<'+uri+'>  <http://purl.org/dc/terms/subject> ?cat }'
            sparql.setQuery(query_cat)
            sparql.setReturnFormat(JSON)
            results_cat = sparql.query().convert()

            list_cat=[]
            for result_cat in results_cat["results"]["bindings"]:
                list_cat.append(result_cat["cat"]["value"])
            
            #dictionary where key is abbreviation+count and value is label, reference link and sameAs fetched from query
            data = [result["label"]["value"],uri,list_sameAs,list_type,list_cat]
        return data
    except ValueError:
        data = [uri[uri.rfind("/")+1:-1].replace("_"," "),uri,""]
        return data

def main(argv):
    global language
    language = argv[0]
    in_directory = '/home/akswadmin/dbpedia_files/'
    out_directory = '/home/akswadmin/abbrev_extracted/'+language
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    
    infile = in_directory+language+'/data/redirects_en.ttl'  #location of input file
    outfile = out_directory+'/abbreviation_tsv_'+language+'.txt'  #output file
    lemon_file = out_directory+'/abbreviation_lemon_'+language+'.ttl'  #lemon file
    input_file = open(infile,'r')
    output = open(outfile,'w')
    lemon = open(lemon_file,'w')
    abbrevs = collections.OrderedDict()
    output.write("Abbreviation\tDefinition\tLabel\tReference Link\towl:sameAS\trdf:type\n")
    lemon.write("@prefix :  <http://nlp.dbpedia.org/abbrevbase> .\n@prefix lemon: <http://lemon-model.net/lemon#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix dcterms: <http://purl.org/dc/terms/> .\n\n")
    lemon.write('\n<http://nlp.dbpedia.org/abbrevbase/lexicon/'+language+'>\n a lemon:Lexicon ;\n\tlemon:language "'+language+'" ;\n')
    count = 0
    count_line=0
    for line in input_file:
        """if count_line == 2:
            break
        count_line+=1"""
        uris = line.split(" ")		#splits the triple and stores is as list
        abbrev = uris[0][uris[0].rfind("resource/")+9:-1]    #stores abbreviation
        #print(uris)
        if abbrev.endswith("..."):
            continue
        #meaning = uris[2][uris[2].rfind("/")+1:-1]
        #meaningURI = uris[2][1:-1]
        if "_" not in abbrev:
            if abbrev.find('&nbsp')>0:
                abbrev=abbrev.replace('&nbsp',"_")
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
        temp=":"+temp+"_Entry" #replaces .,? or !
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

        rdfType_string = ','.join(v[4])  #converts rdfType from list to string format
        rdfType_string=rdfType_string.replace("http","<http")
        rdfType_string=rdfType_string.replace(",",">,")
        if len(rdfType_string)>0:
                rdfType_string+='>'
        
        cat_string = ','.join(v[5])  #converts category from list to string format
        cat_string=cat_string.replace("http","<http")
        cat_string=cat_string.replace(",",">,")
        if len(cat_string)>0:
                cat_string+='>'

        #print(abbrevString+"\t"+v[1]+"\t"+'"'+v[1]+'"@'+language+"\t"+v[2]+"\t"+sameAs_string+"\t"+rdfType_string+"\t"+cat_string+"\n")
        output.write(abbrevString+"\t"+v[1]+"\t"+'"'+v[1]+'"@'+language+"\t"+v[2]+"\t"+sameAs_string+"\t"+rdfType_string+"\t"+cat_string+"\n")
        if k[-1]!='.' and k[-1]!='?' and k[-1]!='!':
                k1 = k.split(" ")[1]
        elif k[-1]=='.' or k[-1]=='?' or k[-1]=='!':
                k1 = ""
        definition = "<"+abbrevString+"_Sense"+k1+">\n\tlemon:definition [\n\t\tlemon:value "+'"'+v[1]+'"@'+language+"\n\t] ;\n\t" #def
        if len(rdfType_string) > 0:
                rdf_type = "rdf:type " + rdfType_string + " ;\n\t"		#instance types
        
        label = 'rdfs:label "' + v[1] + '" ;\n\t'				#label					

        if len(cat_string) > 0:
                category = "dcterms:subject " + cat_string + " ;\n\t"		#Categories
        
        if len(sameAs_string) > 0:
                owl_sameAs = "owl:sameAs " + sameAs_string + " ;\n\t"		#interlanguage links containing "dbpedia"

        ref = "lemon:reference " + v[2] + " ;\n\ta lemon:LexicalSense .\n\n"	#reference
        sense = definition + rdf_type + label + category + owl_sameAs + ref	
        lemon.write(sense)
    output.close()
    lemon.close()

if __name__ == "__main__":
    main(sys.argv[1:])
