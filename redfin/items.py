# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RedfinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    price = scrapy.Field()
    beds = scrapy.Field()
    baths = scrapy.Field()
    sqft = scrapy.Field()
    sale_date = scrapy.Field()
    street = scrapy.Field()
    zipcode = scrapy.Field()
    remarks= scrapy.Field()
    key_details_dict = scrapy.Field()
    property_details_dict = scrapy.Field()
    school_details_dict = scrapy.Field()
    scores_dict = scrapy.Field()
