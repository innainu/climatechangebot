"""

    searches nyt for articles related to climate change and returns them
    returns pages, each page has 10 articles. currenly only returns one page.
    cannot specify how many articles per page in api.

    TODO: add date functionality after wit.ai

"""

from nytimesarticle import articleAPI
import random

class NytimesApi(object):
    def __init__(self, key):
        self.api = articleAPI(key)
        self.secret_keyword = 'climate change and '

    def return_all(self, query):
        return self.api.search(q=self.secret_keyword + query)

    def return_content(self, res):
        article = {}
        article['title'] = res['headline']['main']
        article['abstract'] = res['abstract']
        article['_id'] = res['_id']
        article['source'] = res['source']
        article['web_url'] = res['web_url']
        if len(res['multimedia']) > 0:
            print len(res['multimedia'])
            article['image_url'] = 'http://nytimes.com/' + res['multimedia'][0]['url']
        article['date'] = res['pub_date']
        return article

    def return_article_list(self, query, num=1):
        articles = []
        results = self.return_all(query)
        idx = 0
        for doc in results['response']['docs']:
            if doc['abstract'] is None:
                continue
            articles.append(self.return_content(doc))
            idx += 1
            if idx == num:
                break
        random.shuffle(articles)
        return articles
