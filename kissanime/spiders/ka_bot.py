# -*- coding: utf-8 -*-
import scrapy
from kissanime.items import KissanimeItem

class KaBotSpider(scrapy.Spider):
    name = "ka_bot"
    allowed_domains = ["kissanime.com"]
    start_urls = (
        'http://kissanime.com/AnimeList/LatestUpdate?page=1',
    )


    def parse(self, response):
        self.show_chain = []
        selector = scrapy.Selector(response)
        for row in selector.xpath("//table[@class='listing']/tr")[2:]:
            tds = row.xpath('.//td')
            td_href = row.xpath(".//td/a/@href").extract()
            link = "http://kissanime.com"+td_href[0]
            updated_tag = row.xpath(".//td/img[@title='Just updated']/@title").extract()
            updated = ''
            hot = ''
            hot_tag = row.xpath(".//td/img[@title='Popular anime']/@title").extract()
            if len(updated_tag) > 0:
                updated = 'UPDATED'
            if len(hot_tag) > 0:
                hot = 'HOT'
            if len(td_href) > 1:
                latest_episode = td_href[1]
            else :
                latest_episode = row.xpath(".//td[2]/text()").extract()
            # print img_url
            self.show_chain.append(scrapy.http.Request(
                link,callback=self.parse_episode,
                meta={'hot':hot,'updated':updated,'latest_episode':latest_episode},errback = lambda x: self.download_errback(x, link)))
        #Handle pagination
        pagination = selector.css('.pagination').xpath(".//ul/li/a[contains(text(),'Next')]/@href").extract()
        print '*******************'
        print 'Pagination %s'%pagination
        print '*******************'
        if len(pagination) > 0:
            link = pagination[0]
            link = 'http://kissanime.com'+link
            print 'Link --->'+link
            self.show_chain.append(scrapy.http.Request(link,callback=self.parse,
                                                       errback = lambda x: self.download_errback(x, link),
                                   meta={'dont_redirect': True,"handle_httpstatus_list": [301]},
                                   headers={'Referer':'http://kissanime.com/AnimeList/LatestUpdate?page=1'}
                                        )
                                   )

        if self.show_chain:
            yield self.show_chain.pop(0)


    def download_errback(self,response,link):
        print 'Error , but ignoring it.****************'
        if self.show_chain:
            yield self.show_chain.pop(0)
    def update_urls(self,urls):
        final_urls = []
        for url in urls :
            final_urls.append('http://www.kissanime.com'+url)
        return final_urls
    def parse_episode(self,response):
        if response.status == 200 :
            print 'Response Meta = %s'%response.meta
            selector = scrapy.Selector(response)
            item = KissanimeItem()
            item['url']  = response.url
            if len(selector.css('.bigChar')) > 0:
                item['title'] = selector.css('.bigChar').xpath(".//text()").extract()[0]
                item['hot'] = response.meta['hot']
                item['updated'] = response.meta['updated']
                item['latest_episode'] = response.meta['latest_episode']
                index = 1;
                item['other_name'] = selector.xpath("//div[@class='barContent']/div/p[%s]/a/text()"%index).extract()
                index+=1
                item['genres'] =  selector.xpath("//div[@class='barContent']/div/p[%s]/a/text()"%index).extract()
                index+=1
                aired_tag = selector.xpath("//div[@class='barContent']/div/p[%s]/text()"%index).extract()
                if len(aired_tag) > 0:
                    item['aired_date'] = selector.xpath("//div[@class='barContent']/div/p[%s]/text()"%index).extract()[1]
                    index+=1
                summary_tag = selector.xpath("//div[@class='barContent']/div/p[position() = (last()-1)]/text()").extract()
                is_Ok = False
                for x in summary_tag:
                    if len(x.strip()) > 0:
                        is_Ok = True
                        break
                if is_Ok:
                    item['summary'] = summary_tag[0]
                else :
                    summary_tag = selector.xpath("//div[@class='barContent']/div/p[position() = (last())]/text()").extract()
                    if len(summary_tag) > 0:
                        item['summary'] = summary_tag[0]

                p = selector.xpath("//div[@class='barContent']/div/p[3]/text()").extract()
                p1 = selector.xpath("//div[@class='barContent']/div/p[2]/text()").extract()
                p2 = selector.xpath("//div[@class='barContent']/div/p[4]/text()").extract()
                def isTagOk(items):
                    for x in items:
                        if len(x.strip()) > 1:
                            return True
                    return False
                if isTagOk(p) and len(p)>2:
                    item['views'] = p[2]
                    item['status'] = p[1]
                elif isTagOk(p1) and len(p1):
                    item['views'] = p1[2]
                    item['status'] = p1[1]
                elif isTagOk(p2) and len(p2) > 2:
                    item['views'] = p2[2]
                    item['status'] = p2[1]


                    # item['status'] = selector.xpath("//div[@class='barContent']/div/p[3]/text()").extract()[1]

                item['image_url'] = selector.css('.barContent').xpath("./div/img/@src").extract()[0]
                embeded_urls = selector.css('.listing').xpath(".//tr/td/a/@href").extract()
                item['embeded_urls'] = self.update_urls(embeded_urls)
                yield item
        if self.show_chain:
            yield self.show_chain.pop(0)