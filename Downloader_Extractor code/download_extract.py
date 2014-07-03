import urllib2
import bz2
import sys
import re
import os.path
import time

global language

#this function downloads the files and shows the progress bar as per the file being downloaded
def download_file(url,abbrevFile=0):
	file_name = url.split('/')[-1]
	u = urllib2.urlopen(url)
	if os.path.isfile(file_name):
		print file_name," already exists"
		return file_name
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)
	    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
	    status = status + chr(8)*(len(status)+1)
	    print status,
	f.close()
	print file_name, "downloaded successfully..."
	decompress(file_name,abbrevFile)
	return file_name

def decompress(file_name,abbrevFile=0):
	global language
	location = '/usr/local/share/virtuoso/vad/'
	new_file = file_name.replace(".bz2",'')	
	directory= location+language+"/data"  #makes a new dirctory like for french fr/data, this will store extracted data
	
	#if dirctory doesnot exists then make it
	if not os.path.exists(directory):
    		os.makedirs(directory)	
	
	temp = open(directory+"/"+new_file,"w")
	bz_file = os.popen('bzip2 -cd ' + file_name) #to read compressed file
	line_list = bz_file.readlines()
	
	#here we download abbreviations ending with .,! or ? but this is only in redirects, which contains all the abbreviations 
	#rest of the files contain meanings so no regular expression required

	if abbrevFile:
		for line in line_list :
			obj=re.match(r'<http://dbpedia.org/resource/.*[\?!\.]> <.*> <.*>',line)
			if obj:
				#print line
				temp.write(line)
	else:
		for line in line_list :
			#print line
			temp.write(line)
	temp.close()

	print file_name," decompressed successfully...saved as",new_file


def main(argv):
	global language	
	language=argv[0] #language received at command line
	root = "http://downloads.dbpedia.org/3.9/"

	#below will make URL for different files to be downloaded
	redirect = root+language+"/redirects_"+language+".ttl.bz2"
	instance = root+language+"/instance_types_heuristic_"+language+".ttl.
	InterLang_Links = root+language+"/interlanguage_links_"+language+".ttl.bz2"
	InterLang_Links_Chap = root+language+"/interlanguage_links_chapters_"+language+".ttl.bz2"
	label = root+language+"/labels_"+language+".ttl.bz2"
	category = root+language+"/article_categories_"+language+".ttl.bz2"
	disambiguation = root+language+"/disambiguations_"+language+".ttl.bz2"
	
	#dwn=open("download_time.txt","w") #file to store time take by each file to download and decomress

	#downloaded 7 files namely:
	#1. redirects- contains abbreviations
	#2. instance_types_heuristic
	#3. interlanguage_links
	#4. interlanguage_links_chapters
	#5. labels
	#6. article_categories
	#7. disambiguations

	f=download_file(redirect,1)
		
	f=download_file(instance)
		
	f=download_file(InterLang_Links)
		
	f=download_file(InterLang_Links_Chap)	
		
	f=download_file(label)
		
	f=download_file(category)	
		
	f=download_file(disambiguation)
	
if __name__ == "__main__":
    main(sys.argv[1:])
