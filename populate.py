#!/usr/bin/python
#coding=utf-8
import re
import json
import MySQLdb
import xml.etree.ElementTree as ET
from w3lib.html import remove_tags, remove_tags_with_content
import sys

hometitle={}
db = MySQLdb.connect(host="192.168.247.129",user="root",passwd="1",db="data",charset="utf8")
cursor=db.cursor()
sql="INSERT INTO new_table (url,domain,title,text,code) VALUES (%s,%s,%s,%s,%s)"

with open("%s"%(sys.argv[1])) as f:
	jsonlist = json.load(f)
	dictlist=jsonlist[0]
	for domain in dictlist.keys():
		if (domain=='nocontent' or domain=='error'):
			continue
		for url in dictlist[domain].keys():
			if (re.search(r"//"+domain+"$|"+"//"+domain+"/$",url)):
				hometitle[domain]=""
				data=dictlist[domain][url]
				if ET.ElementTree(ET.fromstring(data)).getroot().find('title').text:
					hometitle[domain]=ET.ElementTree(ET.fromstring(data)).getroot().find('title').text
		for url in dictlist[domain].keys():
			root = ET.ElementTree(ET.fromstring(dictlist[domain][url])).getroot()
			try:
				title = root.find('title').text.strip()+' - '+str(hometitle[domain]).strip()
			except:
				print (title)
			text=re.sub(r'\s+', ' ',remove_tags(remove_tags_with_content(root.find('data').text, ('script','style','noscript'))).strip())
			if (not re.search(r"\S",text)):
				continue
			code = root.find('data').text
			if (root.find('header')):
				print ("header:{}".format(domain))
			if (root.find('footer')):
				print ("footer:{}".format(domain))
			param=(url,domain,title,text,code)
			try:
				cursor.execute(sql,param)
			except (MySQLdb.Error, e):
				print (e)
				pass
			db.commit()
