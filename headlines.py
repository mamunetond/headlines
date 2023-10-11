import datetime
import feedparser
from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
import json
import urllib.parse
import urllib.request

app = Flask(__name__)

# BBC_FEED = 'http://feeds.bbci.co.uk/news/rss.xml' #PArse BBC feed URL. Returns a dict.
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'
            }
DEFAULTS = {'publication': 'bbc',
            'city': 'London',
            'currencyFrom': 'GBP',
            'currencyTo': 'USD'}

WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather?q={},&units=metric&APPID=cb64e63490fc49b2caa0a63127ffd04e'
CURRENCY_URL = 'https://openexchangerates.org/api/latest.json?app_id=6559ab0fdbf346ea8f631f990dce8ac1'
# Static URL routing
# @app.route("/")
# @app.route("/bbc")
# def bbc():
#     return getNews('bbc')

# @app.route("/cnn")
# def cnn():
#     return getNews('cnn')

@app.route("/")
def home():
    # Get customized headlines, based on user input or default

    publication = getValuewithFallback("publication")
    articles = getNews(publication)

    # Get customized weather based on user input or default
    city = getValuewithFallback('city')
    weather = getWeather(city)

    currencyFrom = getValuewithFallback('currencyFrom')
    currencyTo = getValuewithFallback('currencyTo')
    rate, currencies = getRate(currencyFrom, currencyTo)

    response = make_response(render_template("home.html", 
                           articles=articles, 
                           weather=weather,
                           currencyFrom =currencyFrom,
                           currencyTo=currencyTo,
                           rate=rate,
                           currencies=sorted(currencies)))
    
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currencyFrom", currencyFrom, expires=expires)
    response.set_cookie("currencyTo", currencyTo, expires=expires)

    return response


def getNews(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])

    return feed['entries']


def getWeather(query):
    # This is not how the book does it due to outdated version of urllib.
    apiUrl = WEATHER_URL
    query = urllib.parse.quote(query)
    url = apiUrl.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather= {"description": parsed['weather'][0]["description"],
                  "temperature": parsed['main']['temp'],
                  "city": parsed['name'],
                  "country": parsed['sys']['country']}
        
    return weather


def getRate(frm, to):

    allCurrency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(allCurrency).get('rates')
    frmRate = parsed.get(frm.upper())
    toRate = parsed.get(to.upper())

    return (toRate/frmRate, parsed.keys())


def getValuewithFallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    
# @app.route("/<publication>")
# def getNews(publication="bbc"):
#     feed = feedparser.parse(RSS_FEEDS[publication])
#     first_article = feed['entries'][0]
#     return render_template("home.html", articles=feed['entries'])
    # Cleaner way of populating dynamically
    # return render_template("home.html", article=first_article)
    # One way to dynamically populate your tmeplates
    # return render_template("home.html",
    #                        title=first_article.get("title"),
    #                        published=first_article.get("published"),
    #                        summary=first_article.get("summary")
    #                        )
    # You can return html in your return statements
    # return """<html>
    #             <body>
    #                 <h1> Headlines </h1>
    #                 <b>{0}</br>
    #                 <i>{1}</br>
    #                 <p>{2}</br>
    #             </body>
    #         </html>""".format(first_article.get("title"), 
    #                           first_article.get("published"), 
    #                           first_article.get("summary"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
