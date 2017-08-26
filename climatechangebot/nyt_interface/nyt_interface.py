"""

    Searches nyt API for articles related to climate change and returns them.
    API returns pages, each page has 10 articles. This currently only returns one page.
    Cannot specify how many articles per page in api.
    get_trending function returns articles for the past 3 days.

"""

from nytimesarticle import articleAPI
from datetime import datetime, timedelta
import random


class NytimesApi(object):
    def __init__(self, key):
        self.api = articleAPI(key)
        self.secret_keyword = "climate change and "
        self.num_days_trending = 3

    def return_all(self, query):
        """
            Keep query as is if climate change is in the query
            If not, add climate change
        """

        if 'climate change' in query:
            return self.api.search(q=query)
        return self.api.search(q=self.secret_keyword + query)

    def return_trending(self):
        """
            NYT API only accepts dates that are of format: YYYYMMDD
        """
        first_date = datetime.today() - timedelta(self.num_days_trending)
        first_date = first_date.strftime("%Y%m%d")
        return self.api.search(q=self.secret_keyword, begin_date=first_date)

    def return_content(self, res):
        article = {}
        # print res
        if res.get('headline'):
            article['title'] = res['headline'].get('main')
        else:
            #  Don't include article if there is no title
            return None
        if res.get('abstract'):
            article['abstract'] = res.get('abstract')
        else:
            if res.get('lead_paragraph'):
                article['abstract'] = res.get('lead_paragraph')
            elif res.get('snippet'):
                article['abstract'] = res.get('snippet')
            else:
                #  Don't include article if abstract, lead_paragraph or snippet don't exist
                return None
        article['_id'] = res.get('_id')
        article['source'] = res.get('source')
        article['web_url'] = res.get('web_url')
        if len(res.get('multimedia')) > 0:
            article['image_url'] = 'http://nytimes.com/' + res['multimedia'][0]['url']
        article['date'] = res.get('pub_date')
        return article

    def clean_response(self, results, num, randomize=False):
        articles = []
        count = 0
        if results.get('response'):
            for doc in results['response'].get('docs'):
                article_content = self.return_content(doc)
                if article_content is None:
                    continue
                articles.append(article_content)
                count += 1
                if count == num:
                    break
            if randomize:
                random.shuffle(articles)

        return articles

    def return_article_list(self, query, num=1, randomize=False):
        results = self.return_all(query)
        print results
        articles = self.clean_response(results, num, randomize)
        return articles

    def return_trending_list(self, num=6, randomize=False):
        results = self.return_trending()
        articles = self.clean_response(results, num, randomize)
        return articles
