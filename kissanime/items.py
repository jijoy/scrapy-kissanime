# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KissanimeItem(scrapy.Item):
      title = scrapy.Field()
      updated = scrapy.Field()
      hot = scrapy.Field()
      latest_episode = scrapy.Field()
      other_name = scrapy.Field()
      genres = scrapy.Field()
      aired_date = scrapy.Field()
      status = scrapy.Field()
      views = scrapy.Field()
      summary = scrapy.Field()
      url = scrapy.Field()
      image_url = scrapy.Field()
      image_path = scrapy.Field()
      embeded_urls = scrapy.Field()