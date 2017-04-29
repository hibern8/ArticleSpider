# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrappy下载后并解析
        2. 获取下一页url并交给scrappy进行下载，下载后交给parse
        """

        posts_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in posts_nodes:
            img_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            # yield Request(url=post_url,meta={"front-image-url":img_url},callback=self.parse_detail)
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":img_url}, callback=self.parse_detail)
            print(post_url )

        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=post_url, callback=self.parse)

    def parse_detail(self,response):

        article_item = JobBoleArticleItem( )

        # # 通过xpath选择器提取
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()[1]').extract()[0].strip().replace("·","").strip()
        # praise_number = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # fav_num = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*",fav_num)
        # if match_re:
        #     fav_num = int(match_re.group(1))
        # else:
        #     fav_num = 0
        #
        # comment_num = response.xpath('//span[@class="btn-bluet-bigger href-style hide-on-480"]/text()').extract()[0]
        # match_re2 = re.match(".*?(\d+).*",comment_num)
        # if match_re2:
        #     comment_num = int(match_re2.group(1))
        # else:
        #     comment_num = 0
        #
        # content = response.xpath("//div[@class='entry']").extract()[0]
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = "，".join(tag_list )

        #通过css选择器提取
        front_image_url = response.meta.get("front_image_url","") #文章封面图
        title = response.css(".entry-header h1::text").extract()[0]
        create_time = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "")
        praise_number = response.css(".vote-post-up h10::text").extract()[0].strip()
        fav_num = response.css(".bookmark-btn::text").extract()[0].strip()
        match_re = re.match(".*?(\d+).*",fav_num)
        if match_re:
            fav_num = int(match_re.group(1))
        else:
            fav_num = 0
        comment_num =response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re2 = re.match(".*?(\d+).*",comment_num)
        if match_re2:
            comment_num = int(match_re2.group(1))
        else:
            comment_num = 0

        content = response.css("div.entry").extract()[0]

        tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = "，".join(tag_list )

        article_item["title"] = title
        article_item["url"] = response.url
        article_item["create_time"] = create_time
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_number"] = praise_number
        article_item["fav_num"] = fav_num
        article_item["comment_num"] = comment_num
        article_item["content"] = content
        article_item["tags"] = tags

        yield article_item



        pass
