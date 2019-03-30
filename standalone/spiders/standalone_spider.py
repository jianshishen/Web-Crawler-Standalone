# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy_splash import SplashRequest
from standalone.items import StandaloneItem
from scrapy.spiders import CrawlSpider
from urllib.parse import urlparse
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import re

hostip='127.0.0.1'
job_redis = redis.Redis(host=hostip)

class StandaloneSpiderSpider(CrawlSpider):
    name = 'standalone_spider'
    data = open('list.txt', 'r').readlines()
    allow_domains=['{uri.netloc}'.format(uri=urlparse(i)).strip() for i in data]
    start_urls = [domain.strip() for domain in data]

    maximumPagesPerSite=19
    http_user = 'user'
    http_pass='userpass'

    # Using Splash to handle requests
    def start_requests(self):
        for url in self.start_urls:
            splashrequest=SplashRequest(url, self.parse,endpoint='render.html',headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"},args={'wait':0.5,'allowed_domains':self.allow_domains},)
            splashrequest.errback=self.errback
            yield splashrequest

    def parse(self, response):
        parsed_uri = urlparse(response.url)
        domainurl = '{uri.netloc}'.format(uri=parsed_uri)

        # If the amount of downloaded pages of one site exceeds the limit, all following requests of the same domain will be removed from the queue
        if int(job_redis.hlen(domainurl)) > self.maximumPagesPerSite:
            regex = re.compile(r'\b'+domainurl+'\b')
            if len(filter(lambda i: regex.search(i), self.start_urls))>0:
                for item in filter(lambda i: regex.search(i), self.start_urls):
                    self.start_urls.remove(item)
            return

        # Remove urls containing anchor mark, phone numbers, emails and login pages
        for link in LxmlLinkExtractor(deny=[r'[\S\s]*#[\S\s]*',r'[\S\s]*\/tel:[\S\s]*',r'[\S\s]*\/fax:[\S\s]*',r'[\S\s]*\/mailto:[\S\s]*',r'[\S\s]*\/login[\S\s]*',r'[\S\s]*\/\+[0-9]*$'],allow_domains=self.allow_domains).extract_links(response):
            if int(job_redis.hlen(domainurl)) > self.maximumPagesPerSite:
                break
            else:
                self.start_urls.append(link.url)

        # Add sites having respond code from 400 to 600 to a list
        if response.status in range(400, 600):
            job_redis.sadd('error',response.url)
        else:
            item=StandaloneItem()
            tempinput=response.xpath("//body")
            
            #Extract the domain, title ,text and url of a website
            if tempinput:
                templist=[]
                templist.append(re.sub(r'\s+', ' ',tempinput.extract()[0].strip()))
                item['domain']=[domainurl]
                item['data'] = templist
                item['title']=response.xpath("normalize-space(//title)").extract()
                item['link']=[response.url]
                return item
            else:
                job_redis.sadd('error',response.url)

    # Error callback for Splash
    def errback(self,failure):
        if (hasattr(failure,'response')):
            responseurl=failure.value.response.url
            job_redis.sadd('error',responseurl)
