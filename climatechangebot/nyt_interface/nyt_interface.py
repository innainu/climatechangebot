"""

    searches nyt for articles related to climate change and returns them

    TODO: add date functionality after wit.ai

"""

from nytimesarticle import articleAPI

class NytimesApi(object):
    def __init__(self, key):
        self.api = articleAPI(key)
        #nyt api gives 10 articles per page
        self.DEFAULT_NUM_ARTICLES = 10
        self.secret_keyword = 'climate change and '

    def return_all(self, query):
        return self.api.search(q = self.secret_keyword + query)

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

    def return_one_article(self, query):
        results = self.return_all(query)
        idx = 0
        articles = results['response']['docs']
        #make sure to get an article with abstract
        while articles[idx]['abstract'] is None:
            idx += 1
        article = self.return_content(articles[idx])
        return article

    def return_article_list(self, query):
        articles = []
        results = self.return_all(query)
        for idx in xrange(self.DEFAULT_NUM_ARTICLES):
            if results['response']['docs'][idx]['abstract'] is None:
                continue
            articles.append(self.return_content(results['response']['docs'][idx]))
        return articles
