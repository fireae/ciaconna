#!/usr/bin/python
# coding: utf-8
import lxml
from lxml import etree
import sys
import re
import codecs
import os
import unicodedata
import HTMLParser

def dehyphenate(treeIn):
        pair_count = 0
	last_words = treeIn.xpath("//html:span[@class='ocr_word'][last()] | //span[@class='ocr_word'][last()]",namespaces={'html':"http://www.w3.org/1999/xhtml"})
	first_words = treeIn.xpath("//html:span[@class='ocr_word'][1] | //span[@class='ocr_word'][1]",namespaces={'html':"http://www.w3.org/1999/xhtml"})
        if len(last_words) > 0 and len(first_words) > 0:
                last_first_pairs = zip(last_words,first_words[1:]+[None])
                last_first_pairs = [(None,first_words[0])] + last_first_pairs
                for pair in last_first_pairs:
                    if pair[1] == None:
                        print pair[0].text, "DONE"
                    elif pair[0] == None:
                        print "START", pair[1].text
                    else:
                        if pair[0].text[-1] == u'-':
                            pair_count = pair_count + 1
                            dehyphenated_form = u'' + pair[0].text[:-1] + pair[1].text
                            hyphen_position = str(len(pair[0].text))
                            pair[0].set('dehyphenatedForm', dehyphenated_form)
                            pair[0].set('hyphenPosition', hyphen_position)
                            pair[0].set('hyphenEndPair',str(pair_count))
                            pair[1].set('dehyphenatedForm', '')
                            pair[1].set('hyphenStartPair',str(pair_count))
                        print(etree.tostring(pair[0], method='xml', encoding="utf-8", pretty_print=True))
                        print(etree.tostring(pair[1], encoding="utf-8", pretty_print=True))
	return treeIn

def identify(treeIn):
        words = treeIn.xpath("//html:span[@class='ocr_word'] | //span[@class='ocr_word']",namespaces={'html':"http://www.w3.org/1999/xhtml"})
        for word in words:
            if word.get('id') == None:
                word.set('id',str(id(word)))
        return treeIn

html_parser = HTMLParser.HTMLParser()
spellcheck_dict = {}
euro_sign = unicode(u"\N{EURO SIGN}") 
print sys.argv[1]
try:
    dir_in = sys.argv[1]
    print dir_in
    dir_in_list = os.listdir(dir_in)
    dir_out = sys.argv[2]
except (IndexError, ValueError) as e:
    print e
    print "usage: dehyphenate.py dir_in dir_out"
    exit()
        
for file_name in dir_in_list:
        if file_name.endswith('.html'):
                simplified_name = file_name
                if file_name.startswith('output-'):
                        simplified_name = file_name[7:]
                print simplified_name
                name_parts = simplified_name.split('_')
                print name_parts
                simplified_name = name_parts[0] + '_' + name_parts[1] #+ '.html'
                fileIn_name = os.path.join(dir_in,file_name)
                fileOut_name = os.path.join(dir_out,simplified_name)
                fileIn= codecs.open(fileIn_name,'r','utf-8')
                fileOut = open(fileOut_name,'w')
		print "checking", fileIn_name, "sending to ", fileOut_name
                try:
                    treeIn = etree.parse(fileIn)
                    treeIn = identify(treeIn)
		    treeIn = dehyphenate(treeIn)
		    fileOut.write(etree.tostring(treeIn.getroot(),
                        encoding="UTF-8",xml_declaration=True))
                    fileOut.close()
                except(lxml.etree.XMLSyntaxError):
                    pass



