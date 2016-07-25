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
        self.secret_keyword = "climate change and "

    def return_all(self, query):
        """
            Keep query as is if climate change is in the query
            If not, add climate change
        """

        if 'climate change' in query:
            return self.api.search(q=query)
        return self.api.search(q=self.secret_keyword + query)

    def return_content(self, res):
        article = {}
        article['title'] = res['headline']['main']
        article['abstract'] = res['abstract']
        article['_id'] = res['_id']
        article['source'] = res['source']
        article['web_url'] = res['web_url']
        if len(res['multimedia']) > 0:
            article['image_url'] = 'http://nytimes.com/' + res['multimedia'][0]['url']
        article['date'] = res['pub_date']
        return article

    def return_article_list(self, query, num=1, randomize=False):
        articles = []
        results = self.return_all(query)
        idx = 0
        for doc in results['response']['docs']:
            if doc['abstract'] is None:
                doc['abstract'] = doc['lead_paragraph']
            else:
                continue
            articles.append(self.return_content(doc))
            idx += 1
            if idx == num:
                break
        if randomize:
            random.shuffle(articles)
        return articles
