from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SourceSerializer, HeadlineSerializer

from .models import Source, Headline

# import tweepy

requests.packages.urllib3.disable_warnings()


# Create your views here.

class GetDataAPI(APIView):
    def get(self, request, category='latest' , *args, **kwargs):
        sources = Source.objects.filter(source_category=category)
        if not sources:
                data = {
                    'success': False,
                    'msg': 'There\'s no sources matching your category',
                }
                return Response(data)
        else:
            serializer = SourceSerializer(sources, many=True)
            return Response(serializer.data)

class SearchAPI(APIView):
    def get(self, request, query, *args, **kwargs):
        headlines = Headline.objects.filter(title__contains=query)
        if not headlines:
                data = {
                    'success': False,
                    'msg': 'There\'s no headlines matching your keyword',
                }
                return Response(data)
        else:
            serializer = HeadlineSerializer(headlines, many=True)
            return Response(serializer.data)

def getAllByCategory(category):
    news_all = []
    for source in Source.objects.filter(source_category=category):
        source_name = source.source_name
        source_link = source.source_link
        update_datetime = source.updated_datetime
        news_list = Headline.objects.filter(source=source)

        news_count = len(news_list)
        if news_count > 5:
            dict = {'source': source_name,
                    'source_url': source_link,
                    'news_count': news_count,
                    'update_datetime': update_datetime,
                    'top_news': news_list[:5],
                    'news_list': news_list[5:]}
        else:
            dict = {'source': source_name,
                    'source_url': source_link,
                    'news_count': news_count,
                    'update_datetime': update_datetime,
                    'news_list': news_list}

        news_all.append(dict)
    return news_all

def get_all(request, category='latest'):
    return render(request, 'newsScrapper/news.html', {'news_all': getAllByCategory(category)})


def sync_now(request):
    Source.objects.all().delete()
    scrap_all_latest()
    scrap_all_politics()
    scrap_all_business()
    scrap_all_health()
    return render(request, 'newsScrapper/news.html', {'news_all': getAllByCategory('latest')})


def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        news_all = []
        for source in Source.objects.all():
            source_name = source.source_name
            source_link = source.source_link
            update_datetime = source.updated_datetime
            news_list = Headline.objects.filter(source=source, title__contains=query)

            news_count = len(news_list)
            if news_count > 5:
                dict = {'source': source_name,
                        'source_url': source_link,
                        'news_count': news_count,
                        'update_datetime': update_datetime,
                        'top_news': news_list[:5],
                        'news_list': news_list[5:]}
            else:
                dict = {'source': source_name,
                        'source_url': source_link,
                        'news_count': news_count,
                        'update_datetime': update_datetime,
                        'news_list': news_list}

            news_all.append(dict)
        return render(request, 'newsScrapper/news.html', {'news_all': news_all, 'query': query})
    else:
        get_all(request, 'latest')


def scrap_all_latest():
    news_all = [scrap_bbc(), scrap_new_york_times(), scrap_los_angles_times(), scrap_wired(), scrap_the_onion(),
                scrap_cnn(), scrap_quartz(), scrap_washington_post(), scrap_the_verge()]
    save_all(news_all, 'latest')
    # return render(request, 'newsScrapper/news.html', {'news_all': news_all})


def scrap_all_politics():
    news_all = [scrap_ny_times_politics(), scrap_washington_post_politics(), scrap_wsj_washington_wire_politics()]
    save_all(news_all, 'politics')
    # return render(request, 'newsScrapper/news.html', {'news_all': news_all})


def scrap_all_business():
    news_all = [scrap_wsj_washington_wire_business(), scrap_ny_times_business(), scrap_business_insider()]
    save_all(news_all, 'business')
    # return render(request, 'newsScrapper/news.html', {'news_all': news_all})


def scrap_all_health():
    news_all = [scrap_harvard_health(), scrap_webmd(), scrap_wellness_mama()]
    save_all(news_all, 'health')
    # return render(request, 'newsScrapper/news.html', {'news_all': news_all})


def save_all(news_all, category):
    for source in news_all:
        if source.get('success') and len(source.get('news_list')) > 0:
            print('Successfully Scrapped: ' + source.get('source'))
            source_obj, created = Source.objects.get_or_create(
                source_name=source.get('source'),
                source_link=source.get('source_url'),
                source_category=category
            )
            if created:
                for news in source.get('news_list'):
                    obj, created = Headline.objects.get_or_create(
                        source=source_obj,
                        title=news.title,
                        link=news.link
                    )
        else:
            print('Failed Scrapping: ' + source.get('source'))


def scrap_the_onion():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.theonion.com'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml', from_encoding="utf8")

        articles = soup.find_all('article')
        news_list = []
        for i in articles:
            if i.find('h4') and i.find('a'):
                title = i.find('h4').text.strip
                link = i.find_all('a')[-1]['href']
                news_list.append(Headline(title=title, link=link))

        # news_count = len(news_list)
        # if news_count > 5:
        #     top_news = []
        #     for i in range(5):
        #         top_news.append(news_list.pop(0))
        #     return {'source': 'The-Onion', 'source_url': url, 'news_count': news_count, 'top_news': top_news,
        #             'news_list': news_list}
        # else:
        #     return {'source': 'The-Onion', 'source_url': url, 'news_count': news_count, 'news_list': news_list}
        return {'success': True, 'source': 'The-Onion', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'The-Onion', 'source_url': url}


def scrap_new_york_times():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.nytimes.com/'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml', from_encoding="utf8")

        articles = soup.find_all('article')
        news_list = []
        for i in articles:
            if i.find('h2') and i.find('a'):
                title = i.find_all('h2')[-1].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))
        return {'success': True, 'source': 'NY-Times', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'NY-Times', 'source_url': url}


def scrap_wired():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.wired.com/'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml', from_encoding="utf8")

        rows = soup.select('.primary-grid-component .cards-component__row > div')
        news_list = []
        for i in rows:
            if i.find('h2') and i.find('a'):
                title = i.find('h2').text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'Wired', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'Wired', 'source_url': url}


def scrap_bbc():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.bbc.com/'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml', from_encoding="utf8")

        rows = soup.select('.module--promo h3')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.replace('"', '').strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'BBC', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'BBC', 'source_url': url}


def scrap_los_angles_times():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.latimes.com/'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml', from_encoding="utf8")

        rows = soup.select('.ListAA-items-item')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[1].text.replace('"', '').strip
                link = i.find_all('a')[1]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'LA-Times', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'LA-Times', 'source_url': url}


def scrap_cnn():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://edition.cnn.com'
    req_url = 'https://edition.cnn.com/data/ocs/section/index.html:intl_homepage1-zone-1/views/zones/common/zone-manager.izl'
    content = session.get(req_url, verify=False).text.replace('\\', '').replace('\"', '')
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('article h3')
        news_list = []
        for i in rows:
            if i.find('span', {'class': 'cd__headline-text'}) and i.find('a'):
                title = i.find_all('span', {'class': 'cd__headline-text'})[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'CNN', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'CNN', 'source_url': url}


def scrap_quartz():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://qz.com'
    req_url = 'https://qz.com/latest/'
    content = session.get(req_url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')

        rows = soup.select('article')
        news_list = []
        for i in rows:
            if i.find('h3') and i.find('a'):
                title = i.find_all('h3')[-1].text.strip
                link = i.find_all('a')[-1]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'QUARTZ', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'QUARTZ', 'source_url': url}


def scrap_washington_post():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.washingtonpost.com'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('#main-content .top-table-col > div')
        news_list = []
        for i in rows:
            if i.find('ul', {'class': 'related-links'}):
                for j in i.select('.related-links li'):
                    if j.find('a'):
                        title = j.find_all('a')[0].text.strip
                        link = j.find_all('a')[0]['href']
                        if not link.startswith(url):
                            link = url + link
                        news_list.append(Headline(title=title, link=link))
            if i.find('ul', {'class': 'timeline-stream'}):
                for j in i.select('.timeline-stream li'):
                    if j.find('a'):
                        title = j.find_all('a')[0].text.strip
                        link = j.find_all('a')[0]['href']
                        if not link.startswith(url):
                            link = url + link
                        news_list.append(Headline(title=title, link=link))
            if i.find('a') and i.find('a').has_attr('href'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'Washington-Post', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'Washington-Post', 'source_url': url}


def scrap_the_verge():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.theverge.com'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('.c-compact-river__entry .c-entry-box--compact__body')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'The-Verge', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'The-Verge', 'source_url': url}


def scrap_ny_times_politics():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.nytimes.com'
    req_url = 'https://www.nytimes.com/section/politics'
    content = session.get(req_url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('.css-f8yl15 article h2')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'NY-Times', 'source_url': req_url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'NY-Times', 'source_url': req_url}


def scrap_washington_post_politics():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.washingtonpost.com'
    req_url = 'https://www.washingtonpost.com/politics'
    content = session.get(req_url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('#main-content .story-list-story h2')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'Washington-Post', 'source_url': req_url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'Washington-Post', 'source_url': req_url}


def scrap_wsj_washington_wire_politics():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.wsj.com/news/types/washington-wire'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('article')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                # if not link.startswith(url):
                #     link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'WSJ-Washington-Wire', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'WSJ-Washington-Wire', 'source_url': url}


def scrap_wsj_washington_wire_business():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.wsj.com/news/business'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('article')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                # if not link.startswith(url):
                #     link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'WSJ-Business', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'WSJ-Business', 'source_url': url}


def scrap_ny_times_business():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.nytimes.com'
    req_url = 'https://www.nytimes.com/section/business'
    content = session.get(req_url, verify=False).content

    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('.ekkqrpp3 article h2')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'NY-Times', 'source_url': req_url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'NY-Times', 'source_url': req_url}


def scrap_business_insider():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.businessinsider.com'
    req_url = 'https://www.businessinsider.com/clusterstock'
    content = session.get(req_url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('section h2')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'Business-Insider', 'source_url': req_url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'Business-Insider', 'source_url': req_url}


def scrap_harvard_health():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.health.harvard.edu'
    # req_url = 'https://www.businessinsider.com/clusterstock'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.find_all('article',
                             {'class': ['article-listing-item', 'blog-listing-item', 'document-carousel-text-block']})
        a_all = []
        for i in rows:
            if i.find('h2'):
                a_all += i.select('h2 a')
            elif i.find('h3'):
                a_all += i.select('h3 a')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'Harvard-Health', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'Harvard-Health', 'source_url': url}


def scrap_webmd():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://www.webmd.com'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('.topStories a')
        news_list = []

        hero_story_title = soup.select('.hero-with-caption .caption h2')[0].text.strip
        hero_story_link = soup.select('.hero-with-caption > a')[0]['href']
        news_list.append(Headline(title=hero_story_title, link=hero_story_link))
        for i in rows:
            if i.find('h3'):
                title = i.find_all('h3')[0].text.strip
                link = i['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))
            elif i.find('h2'):
                title = i.find_all('h2')[0].text.strip
                link = i['href']
                if not link.startswith(url):
                    link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'WebMd', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'WebMd', 'source_url': url}


def scrap_wellness_mama():
    session = requests.session()
    session.headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    url = 'https://wellnessmama.com/blog/'
    content = session.get(url, verify=False).content
    try:
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('article h2')
        news_list = []
        for i in rows:
            if i.find('a'):
                title = i.find_all('a')[0].text.strip
                link = i.find_all('a')[0]['href']
                # if not link.startswith(url):
                #     link = url + link
                news_list.append(Headline(title=title, link=link))

        return {'success': True, 'source': 'Wellness-Mama', 'source_url': url, 'news_list': news_list}
    except:
        return {'success': False, 'source': 'Wellness-Mama', 'source_url': url}
# def get_twitter_trends():
#     consumer_key = 'secret'
#     consumer_secret = 'secret'
#     access_token = 'secret'
#     access_token_secret = 'secret'
#     # OAuth process, using the keys and tokens
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#     auth.set_access_token(access_token, access_token_secret)
#     api = tweepy.API(auth)
#
#     trends1 = api.trends_place(1)  # from the end of your code
#     # trends1 is a list with only one element in it, which is a
#     # dict which we'll put in data.
#     data = trends1[0]
#     # grab the trends
#     trends = data['trends']
#     # grab the name from each trend
#     names = [trend['name'] for trend in trends]
#     # put all the names together with a ' ' separating them
#     trendsName = ' '.join(names)
#     print(trendsName)
#
#
# get_twitter_trends()
