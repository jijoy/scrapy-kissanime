# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.contrib.exporter import XmlItemExporter as BaseXmlItemExporter
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import log,Request
from kissanime import settings
class XmlItemExporter(BaseXmlItemExporter):

    def export_item(self, item):
        self.xg.startElement(self.item_element, {})
        for name, value in self._get_serialized_fields(item, default_value=''):
            self._export_xml_field(name, value)
        self.xg.endElement(self.item_element)

    def _export_embed(self, name, serialized_value):
        log.msg('Inside _export_embed ********************URL-->%s'%serialized_value,log.DEBUG)
        self.xg.startElement(name, serialized_value)
        self.xg.endElement(name)

    def _export_xml_field(self, name, serialized_value):
        if name == 'embed':
            self._export_embed(name, serialized_value)
            return

        self.xg.startElement(name, {})
        if hasattr(serialized_value, 'items'):
            for subname, value in serialized_value.items():
                self._export_xml_field(subname, value)
        elif hasattr(serialized_value, '__iter__'):
            for value in serialized_value:
                self._export_xml_field('value', value)
        else:
            self._xg_characters(serialized_value)
        self.xg.endElement(name)


class XmlExportPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        outfile = open('{}.xml'.format(spider.name), 'w+b')
        self.files[spider] = outfile
        self.exporter = XmlItemExporter(outfile)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        outfile = self.files.pop(spider)
        outfile.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class MyImagesPipeline(ImagesPipeline):


    def get_media_requests(self, item, info):
        if item.has_key('image_url'):
            image_url = item['image_url']
            log.msg('***********',log.DEBUG)
            log.msg(image_url, level=log.DEBUG)
            # for image_url in image_urls:
            #     log.msg('URL = %s'%image_url, level=log.DEBUG)
                # log.msg('***Title = %s'%title, level=log.DEBUG)
            yield Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        print 'I got some request =%s'%image_paths[0]
        item['image_path'] = settings.IMAGES_STORE+'/'+image_paths[0]
        return item

