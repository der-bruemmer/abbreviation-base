#1 run downloader_extractor code
#2 create graph
#3 import the files to virtuoso (upload all zipped files) i.e run isql-vt from command line
#4 run the lemon maker code
#5 delete graph
#6 delete folder named by language in /home/akswadmin/dbpedia_files/
#sparql select * where { <http://dbpedia.org/resource/BC> owl:sameAs ?s };
language = "en"
run downloader_extractor code
python /home/akswadmin/abbrev_repo/Downloader_Extractor\ code/download_extract.py $language
echo "Files for $language downoaded successfully"
echo "importing files\n"
isql-v 1111 dba dba << END
sparql create graph <http://dbpedia.org/> ;
ld_dir_all('/home/akswadmin/dbpedia_files/$language/data', '*.*', 'http://dbpedia.org');
select * from DB.DBA.LOAD_LIST;
rdf_loader_run(); 
END
echo "Files imported\nRunning lemon maker"
python3 /home/akswadmin/abbrev_repo/lemon\ file/extractor_lemonMaker.py $language
echo "removing graph"
isql-v 1111 dba dba << END
sparql CLEAR GRAPH <http://dbpedia.org/> ;
END
echo "removing folder"
rm -r /home/akswadmin/dbpedia_files/$language
