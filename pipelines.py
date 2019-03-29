# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import os
import redis
import xml.etree.ElementTree as ET

hostip='127.0.0.1'
job_redis = redis.Redis(host=hostip)

class StandalonePipeline(object):
	def process_item(self, item, spider):
		domain=item['domain']
		link=item['link']
		data=item['data']
		title=item['title']
		zipitem=list(zip(domain,link,title,data))
		for i in range(len(zipitem)):
			item=zipitem[i]
			a=item[0]
			b=item[1]
			c=item[2]
			d=item[3]
			if (re.search(r"\S",d)):
				doc = ET.Element("doc")
				ET.SubElement(doc, "link").text = b
				ET.SubElement(doc, "title").text = c
				ET.SubElement(doc, "data").text = d
				xmlstr=ET.tostring(doc, encoding='utf8', method='xml')
				job_redis.hset(a,b,xmlstr)
			else:
				job_redis.sadd('nocontent',b)
		return item
