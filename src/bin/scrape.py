from heuristos.crawl import Crawler

if __name__ == "__main__":
    keywords = ["terms-of-service", "privacy-policy", "terms", "privacy"]
    c = Crawler("https://www.nestle.com/")
    c.crawl(keywords, content_keywords=[])
