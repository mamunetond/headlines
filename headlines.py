import feedparser
from flask import Flask


app = Flask(__name__)

# BBC_FEED = 'http://feeds.bbci.co.uk/news/rss.xml' #PArse BBC feed URL. Returns a dict.
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'
            }

# Static URL routing
# @app.route("/")
# @app.route("/bbc")
# def bbc():
#     return getNews('bbc')

# @app.route("/cnn")
# def cnn():
#     return getNews('cnn')

@app.route("/")
@app.route("/<publication>")
def getNews(publication="bbc"):
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article = feed['entries'][0]
    return """<html>
                <body>
                    <h1> Headlines </h1>
                    <b>{0}</br>
                    <i>{1}</br>
                    <p>{2}</br>
                </body>
            </html>""".format(first_article.get("title"), 
                              first_article.get("published"), 
                              first_article.get("summary"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
