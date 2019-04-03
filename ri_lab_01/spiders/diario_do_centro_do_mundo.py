# -*- coding: utf-8 -*-
import scrapy
import json
import pdb

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class DiarioDoCentroDoMundoSpider(scrapy.Spider):
    name = 'diario_do_centro_do_mundo'
    allowed_domains = ['diariodocentrodomundo.com.br']
    start_urls = []

    def __init__(self, *a, **kw):
        super(DiarioDoCentroDoMundoSpider, self).__init__(*a, **kw)
        with open('frontier/diariodocentrodomundo.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        self.logger.info("response_url " + response.url)
        news_url = response.css('h3.td-module-title a::attr(href)').get()
        yield response.follow(news_url, callback=self.news_parse,
                              meta={'news_number': 2})

    def news_parse(self, response):
        news_number = response.meta.get('news_number')

        if news_number != 0:
            self.logger.info("response_url " + response.url)
            self.logger.info("meta " + str(response.meta.get('news_number')))
            yield {"response": response.url}

            news_url = response.css('div.td-post-next-prev-content a::attr(href)').get()
            yield response.follow(news_url, callback=self.news_parse,
                                  meta={'news_number': news_number - 1})
