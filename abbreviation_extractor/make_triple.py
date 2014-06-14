# This file downloads the file, extracts it and retreives the abreviations ending with a . or ? or !

import urllib2
import bz2
import sys
import re

def download_file(url):
	file_name = url.split('/')[-1]
	u = urllib2.urlopen(url)
	file_name = "abbrev_en.ttl.bz2"
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
	return file_name

def decompress(file_name):
	new_file = file_name.replace(".bz2",'')
	temp = open(new_file,"w")
	for line in bz2.BZ2File(file_name,'rb') :
		obj=re.match(r'<http://dbpedia.org/resource/.*[\?!\.]> <.*> <.*>',line)
		if obj:
			print line
			temp.write(line)
		"""s=raw_input("enter: ")
		if s=='0':
			break"""
	temp.close()

def main(argv):
	language=argv[0]
	root = "http://downloads.dbpedia.org/3.9/"
	redirect = root+language+"/redirects_"+language+".ttl.bz2"
	instance = root+language+"/instance_types_"+language+".ttl.bz2"
	InterLang_Links = root+language+"/interlanguage_links_"+language+".ttl.bz2"
	InterLang_Links_Chap = root+language+"/interlanguage_links_chapters_"+language+".ttl.bz2"
	label = root+language+"/labels_"+language+".ttl.bz2"
	category = root+language+"/category_labels_"+language+".ttl.bz2"

	file_name = download_file(redirect)
	
	#Commented to test the file	
	
	"""download_file(instance)
	download_file(InterLang_Links)
	download_file(InterLang_Links_Chap)
	download_file(label)
	download_file(category)"""

	decompress(file_name)


if __name__ == "__main__":
    main(sys.argv[1:])
