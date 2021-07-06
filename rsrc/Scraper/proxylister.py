import requests
from lxml import html


class Scraper:
    def __init__( self, config ):
        # the request client, belongs to session even if no "user session" is needed
        self.client = requests.Session()
        self.config = config

    def get_proxies(self):
        print("Fetching raw HTML from '{0}'".format( self.config.proxylist_url))
        fetch_results = self.client.get( self.config.proxylist_url )
        proxy_list = self.Parser.scrape( "proxy_list", fetch_results.content )
        return proxy_list

    class Parser:
        @staticmethod
        def scrape( datapoint, text ):
            cases = {
                "proxy_list": Scraper.Parser.proxy_list
            }
            return cases[ datapoint ]( text )

        @staticmethod
        def proxy_list( text ):
            proxyTable = html.fromstring( text )
            proxyTable_xpath = proxyTable.xpath('//body[@id="mainPage"]/div[@class="container"]/div[@id="content"]/table[@id="searchResult"]/tr/td[@class="site"]/a/text()')
            for proxy in proxyTable_xpath:
                print("Available Proxy: {0}".format( proxy ) )
            return proxyTable_xpath

    class SessionError( Exception ):
        def __init__( self, value ):
            self.value = value

