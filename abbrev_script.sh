#1 run downloader_extractor code
#2 create graph
#3 import the files to virtuoso (upload all zipped files) i.e run isql-vt from command line
#4 run the lemon maker code
#5 delete graph
#6 delete folder named by language in /home/akswadmin/dbpedia_files/

#makes a server report for download
echo "____Server Running Report_____">>server_report

#contains each step of process
echo "temp_file">>temp_file 

languages=("ba" "bat_smg" "be_x_old" "bg" "bn" "bpy" "br" "bs" "bug" "ca" "ceb" "ckb" "cv" "cy" "el" "eo" "eu" "fa" "fy" "ga" "gd" "gl" "gu" "he" "hi" "hif" "hr" "ht" "hu" "hy" "ia" "id" "io" "is" "ja" "jv" "ka" "kk" "kn" "ko" "ku" "ky" "la" "lb" "lmo" "lt" "lv" "map_bms" "mg" "mk" "ml" "mr" "ms" "my" "mzn" "nap" "nds" "ne" "new" "oc" "pms" "pnb" "qu" "ro" "scn" "sco" "sh" "simple" "sk" "sq" "sr" "su" "sw" "ta" "te" "tg" "th" "tl" "tr" "tt" "uk" "ur" "uz" "vec" "vi" "vo" "wa" "war" "yi" "yo" "zh" "zh_min_nan" "zh_yue")

for language in "${languages[@]}"
do
START=$(date +%s)
echo "***********$language**************">>temp_file
echo "***************Current Language: $language****************">>server_report

#downloader script
python /home/akswadmin/abbrev_repo/Downloader_Extractor\ code/download_extract.py $language

echo "---------------Files for $language downoaded successfully-------------------">>server_report
echo "---------------Importing files into virtuoso------------------">>server_report

#accessing virtuoso to import the necessary files from isql-v
isql-v 1111 dba dba << END
sparql create graph <http://dbpedia.org/> ;
ld_dir_all('/home/akswadmin/dbpedia_files/$language/data', '*.*', 'http://dbpedia.org');
select * from DB.DBA.LOAD_LIST;
rdf_loader_run(); 
END

echo "---------------Files imported--------------">>server_report
echo "-----------------Running lemon maker-----------------">>server_report

#extractor script
python3 /home/akswadmin/abbrev_repo/lemon\ file/extractor_lemonMaker.py $language

echo "---------------Removing graph---------------">>server_report

#remove graph
isql-v 1111 dba dba << END
sparql drop graph <http://dbpedia.org/> ;
END

echo "---------------Removing folder $language---------------">>server_report

#remove necessary files i.e. remove the complete folder
rm /home/akswadmin/dbpedia_files/$language

echo "---------------Done $language--------------">>server_report

echo "======================================================================================================">>server_report

END=$(date +%s)
DIFF=$(( $END - $START )) #time taken by the process for particular language

echo "$language took $DIFF seconds">>server_report
echo "======================================================================================================">>server_report
done
