# -*- coding: utf-8 -*-
import scrapy
import json
import datetime

from ri_lab_01.items import RiLab01Item


class DiarioDoCentroDoMundoSpider(scrapy.Spider):
    name = 'diario_do_centro_do_mundo'
    allowed_domains = ['diariodocentrodomundo.com.br']
    start_urls = []

    # the amount of news we should get per page.
    NEWS_NUMBER_PER_PAGE = 2

    def __init__(self, *a, **kw):
        super(DiarioDoCentroDoMundoSpider, self).__init__(*a, **kw)
        with open('seeds/diario_do_centro_do_mundo.json') as json_file:
            data = json.load(json_file)
        self.start_urls = list(data.values())

    """
    In this method, we get the first news of any of the pages in
    seeds/diario_do_centro_do_mundo.json file.
    
    With the first news in hand, we can scrape it to get other different news.
    We can accomplish this by using the parse_news callback. 
    """
    def parse(self, response):
        news_url = response.css('h3.td-module-title a::attr(href)').get()

        # We use the meta_data as follows:
        # - meta_data['news_number'] is mainly used to help our recursive
        #   parse_news callback to stop when reached the number of news needed.
        # - meta_data['category'] is used to set the section on the news item.
        #   This category is extracted from the page URL since we don't
        #   have this information within the news HTML.
        meta_data = {'news_number': self.NEWS_NUMBER_PER_PAGE,
                     'category': self.get_news_category(response.url)}

        yield response.follow(news_url, callback=self.parse_news, meta=meta_data)

    """
    This recursive method is responsible for scraping the last X news of 
    a page, where X is the NEWS_NUMBER_PER_PAGE.
    
    For example, if NEWS_NUMBER_PER_PAGE = 20 and the page we are scraping
    is /politica, it means we would get the last 20 news about politics.
    """
    def parse_news(self, response):
        news_number = response.meta.get('news_number')
        category = response.meta.get('category')

        # if news_number is 0, it means we have scraped the amount
        # of news defined at NEWS_NUMBER_PER_PAGE.
        if news_number != 0:
            yield self.create_news_item(response)

            news_url = response.css('div.td-post-next-prev-content a::attr(href)').get()
            meta_data = {'news_number': news_number - 1, 'category': category}

            yield response.follow(news_url, callback=self.parse_news, meta=meta_data)

    """
    This method is responsible for building the news item that will be 
    stored on the output/results.csv file.
    """
    def create_news_item(self, response):
        url = response.url
        title = response.css('header h1::text').get()
        author = response.css('div.td-post-author-name a::text').get()
        date = response.css('span.td-post-date time::attr(datetime)').get()
        date = self.format_date(date)
        category = response.meta.get('category')
        text = response.css('div.td-post-content span.s1::text').getall()

        # trying to get the news text from a different tag.
        if not text:
            text = response.css('div.td-post-content p::text').getall()

        # NOTE: we don't have the sub_title information in the news.
        return RiLab01Item(title=title, author=author, date=date,
                           text=text, url=url, section=category)

    """
    Get tne news category based on its URL.
    """
    def get_news_category(self, url):
        return url.split('/')[3].capitalize()

    """
    Format date to follow the Latin America date format.
    """
    def format_date(self, date):
        date = date.split("T")
        period = date[0]
        time = date[1].split("+")[0]

        date = period + " " + time
        obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return obj.strftime("%d/%b/%Y %H:%M:%S")
