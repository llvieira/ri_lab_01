# -*- coding: utf-8 -*-
import scrapy
import json
import re
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
        response = response.css('div.td_with_ajax_pagination')[0].css('script *::text').get()
        td_atts = json.loads(re.findall("{.*}", response)[0])
        td_atts["limit"] = 20

        body = {"td_atts": td_atts, "td_block_id": "td_uid_2_5ca3920f6fbd3", "td_column_number": "3",
                "td_current_page": "1", "block_type": "td_block_4", "td_filter_value": "",
                "td_user_action": "", "action": "td_ajax_block"}

        yield scrapy.FormRequest("https://www.diariodocentrodomundo.com.br/wp-admin/admin-ajax.php",
                                 callback=self.news_parse, formdata=body)

    def news_parse(self, response):
        print(response.url)
        pdb.set_trace()

