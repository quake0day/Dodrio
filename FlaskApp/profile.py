# -*- coding: utf-8 -*-

#####
# grab google scholar data of GSLIS faculty
# designed by Qiyuan Liu on 1/31/2013
# http://liuqiyuan.com
#####

import urllib2
import re
import os
import HTMLParser
import BeautifulSoup
import scholar as gs

GOOGLE_SCHOLAR_ID = "DDLTYpAAAAAJ"
class metadataExtraction:      
    # get source
    def getSource(self,urlList):
        """ grap the web page source """
        content=""
        for url in urlList:
            req=urllib2.urlopen(url)
            newcontent=req.read()
            content+=newcontent
        return content


    def mainProcess(self,url):
        raw_data = self.getSource(url)
        soup = BeautifulSoup.BeautifulSoup(''.join(raw_data))
        papers_title = soup.findAll("a", { "class" : "gsc_a_at" })
        with open('publication.json', 'w') as f:
            for title in papers_title:
                articles = gs.query(search=title.string,
                        author='Si Chen',
                        max_results=1)
                f.write(articles[0].dumps('json').encode('utf8'))
                print(articles[0].dumps('json'))


if __name__ == "__main__":
    #test url list
    url_vetle=["https://scholar.google.com/citations?user="+GOOGLE_SCHOLAR_ID+"&hl=en"]

    me=metadataExtraction()
    me.mainProcess(url_vetle)
    
    

    


    
    
    


