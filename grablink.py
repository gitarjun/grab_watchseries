from urllib2 import Request
from urllib2 import urlopen
from lxml import etree
import requests
from unidecode import unidecode
import re
from collections import OrderedDict


class LinkGrab:
    def __init__(self):
        self.hdr = \
        {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        self.link = ''
        self.subseason_table_xpath = '//*[@class="listings show-listings"]'
        self.subseason_header_xpath = '//*[@id="left"]/div/h2/a/span'
        self.season_header = '//*[@itemprop="season"]'

    def _get_response(self, link):
        req = Request(link, headers=self.hdr)
        html = urlopen(req).read()
        x = etree.HTML(html)
        return html,x

    def getlinks(self,link):
        self.link = link
        if self.link.split('/')[-2]=='serie':
            return self.season_links(self.link)
        else:
            return self.get_sub_season_links(link)


    def get_sub_season_links(self,link):
        html, x = self._get_response(link)
        season = unidecode(x.xpath(self.subseason_header_xpath)[0].text)
        season_number = re.findall(r'\d+',season,re.DOTALL)[0]
        series_name = link.split('/')[-2]
        el = x.xpath(self.subseason_table_xpath)
        if len(el)!=1:
            print(el)
            return None
        li_list = el[0].getchildren()
        ret_dict = OrderedDict()
        for li in li_list[::-1]:
            a_tag = li.getchildren()[2]
            href = a_tag.attrib['href']
            full_name = unidecode(a_tag.getchildren()[0].text)
            episode_number = re.findall(r'\d+',full_name,re.DOTALL)[0]
            name = re.split(r'\d+',full_name,re.DOTALL)[1].rstrip().lstrip() # Remove trailing and leading spaces
            ret_dict['{}>{}>{}>{}'.format(series_name,season_number,episode_number.zfill(2),name)] = href
        return ret_dict

    def season_links(self,link):
        html, x = self._get_response(link)
        ret_dict = {}
        season_headers = x.xpath(self.season_header)[0].getchildren()
        for season_header in season_headers:
            print(season_header.getchildren()[0])
            a_tag = season_header.getchildren()[0].attrib['href']
            name = a_tag.split('/')[-1]
            subs = self.get_sub_season_links(a_tag)
            ret_dict[name]=subs
            print(subs)
        return ret_dict

    def get_gorilla_vid(self,link):
        html, x = self._get_response(link)
        target = '//*[@class="download_link_gorillavid.in "]'
        gorillas = x.xpath(target)
        if len(gorillas)==0:
            return None
        tds = gorillas[0].getchildren()
        gorilla_link = re.findall(r'link (.*?)\'\)\)',tds[-1].getchildren()[0].attrib['onclick'],re.DOTALL)[0]
        gorilla_link = gorilla_link.replace('http','https')
        html, x = self._get_response(gorilla_link)
        ##sending post request to get bypass form click ##
        form = re.findall(r'<form method="POST" action=\'\'>(.*?)<div id="pre-download-block">', html, re.DOTALL)[0]
        csrfmiddlewaretoken = re.findall(r"csrfmiddlewaretoken' value='(.*?)'\s/>",form,re.DOTALL)[0].rstrip()
        _id = re.findall(r'name="id" value="(.*?)">', form, re.DOTALL)[0].rstrip()
        fname = re.findall(r'name="fname" value="(.*?)">', form, re.DOTALL)[0].rstrip()
        data = {
        'csrfmiddlewaretoken': csrfmiddlewaretoken,
         'op': "download1",
         'usr_login': "",
         'id': _id,
         'fname': fname,
         'referer': "",
         'channel': "",
         'method_free': "Free Download"
        }
        r = requests.post(gorilla_link, data)
        html = r.text
        dllink = unidecode(re.findall(r"src:\s'(.*?)',", html, re.DOTALL)[0])
        return dllink

if __name__=="__main__":
    from pprint import pprint
    obj = LinkGrab()
    links = obj.getlinks(link = "https://www1.swatchseries.to/suits/season-2")
    pprint(links)
    for name,link in links.items():
        print(name)
        print("{} Season {} Episode {} - {}".format(*name.split('>')),obj.get_gorilla_vid(link))

