import requests
from lxml import html
import urllib
import re
import json

class Result:
    def __init__(self, title, seeders, leechers, size, author, url):
        self.title = str(title)
        self.seeders = int(seeders)
        self.leechers = int(leechers)
        self.size = str(size)
        self.author = str(author)
        self.url = str(url)

    def __str__(self):
        myjson = {}
        myjson['title'] = self.title
        myjson['seeders'] = self.seeders
        myjson['leechers'] = self.leechers
        myjson['size'] = self.size
        myjson['author'] = self.author
        myjson['url'] = self.url

        return json.dumps(myjson)

class Scraper:
    def __init__( self, config ):
        # the request client, belongs to session even if no "user session" is needed
        self.client = requests.Session()
        self.config = config

    def craft_url(self, protocol, proxy, search_terms):
        # https://pirate.blue/s/?q=Raising+Arizona&category=0&page=0&orderby=99
        f = { 'q': search_terms, 'category': 0, 'page': 0, 'orderby': 99 }
        url = str.format( "{0}://{1}/s/?{2}", protocol, proxy, urllib.parse.urlencode(f) )
        print(url)
        return url

    def get_results(self, search_terms):
        url = self.craft_url( "https", self.config.proxy, search_terms )

        fetch_results = self.client.get( url )
        results_list = self.Parser.scrape( "results_list", fetch_results.content )

        return results_list


    def get_magnet(self, url):
        url = "https://" + self.config.proxy + url
        fetch_results = self.client.get(url)

        magnet = self.Parser.scrape( "magnet_link", fetch_results.content )

        return magnet

    class Parser:
        @staticmethod
        def scrape( datapoint, text ):
            cases = {
                "results_list": Scraper.Parser.results_list,
                "magnet_link": Scraper.Parser.magnet_link
            }
            return cases[ datapoint ]( text )

        @staticmethod
        def results_list( text ):
            resultsTable = html.fromstring( text )
            resultsTable_xpath = resultsTable.xpath( '//table[@id="searchResult"]/tr' )

            results_buffer = list()

            for tr in resultsTable_xpath:
                title = tr.xpath('td[2]/div[1]/a[1]/text()')
                seeders = tr.xpath('td[3]/text()')[0]
                leechers = tr.xpath('td[4]/text()')[0]
                author = tr.xpath('td[2]/font/a/text()')
                size_unprocessed = tr.xpath('td[2]/font/text()')[0]
                url = tr.xpath('td/div[@class="detName"]/a[@class="detLink"]/@href')[0]


                m = re.search('Size (.+?),', size_unprocessed)

                if m:
                    size = m.group(1)


                results_buffer.append(
                    Result(title, seeders, leechers, size, author, url)
                )

            return results_buffer


        @staticmethod
        def magnet_link( text ):
            link_page = html.fromstring( text )
            magnet_link = link_page.xpath('//div[@class="download"]/a/@href')[0]
            return magnet_link



    class SessionError( Exception ):
        def __init__( self, value ):
            self.value = value

