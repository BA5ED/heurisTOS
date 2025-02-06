

from heuristos.crawl import Crawler



if __name__ == '__main__':
    keywords = ['terms-of-service', 'privacy-policy', 'terms', 'privacy']
    c = Crawler("https://www.sonos.com/en-us/home")
    c.crawl(keywords, content_keywords=[])