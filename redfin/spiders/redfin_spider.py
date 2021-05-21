from scrapy import Spider
from scrapy import Request 
from redfin.items import RedfinItem
import pandas as pd

class RedfinSpider(Spider):
    name = 'redfin_spider'
    allowed_urls = ['https://www.redfin.com/']

    def start_requests(self):
        redfin_url = 'https://www.redfin.com/zipcode/{}/filter/property-type=house,include=sold-1yr'
        csv = '/Users/Gary/Dropbox/Projects/redfin/redfin/spiders/irvine_zips.csv'
        df = pd.read_csv(csv, names=['zip'])
        zip_urls = [redfin_url.format(x) for x in df['zip']]

        # Feed in urls
        for zip_url in zip_urls:
            yield Request(url=zip_url, callback=self.parse)

    def parse(self, response):

        # URL
        url_list = response.xpath('//a[@class="clickable goToPage"]/@href').extract()
        results_urls = [response.url]
        if url_list:
            for url in url_list:
                results_urls.append('https://www.redfin.com' + url)

        # Result type
        for results_url in results_urls:
            yield Request(url=results_url, callback=self.parse_result_page)

    def parse_result_page(self, response):
        house_urls = response.xpath('//div[@class="scrollable"]/a/@href').extract()
        house_urls = ['https://www.redfin.com' + url for url in house_urls]

        for house_url in house_urls:
            yield Request(url=house_url, callback=self.parse_house_page)

    def parse_house_page(self, response):

        #  Stats
        price = response.xpath('//div[@class="stat-block price-section"]//text()').extract()
        beds = response.xpath('//div[@class="stat-block beds-section"]//text()').extract()
        baths = response.xpath('//div[@class="stat-block baths-section"]//text()').extract()
        sqft = response.xpath('//div[@class="stat-block sqft-section"]//text()').extract()

        # Last sold date
        sale_date = response.xpath('//div[@id="propertyHistory-0"]/div[@class="col-4"]//text()').extract()

        # Address
        address = response.xpath('//h1[@class="address"]//text()').extract()
        street, _ , zipcode = [i for i in address]

        # Remarks
        remarks = response.xpath('//div[@class="remarks"]//text()').extract()

        # Key details
        key_details = response.xpath('//div[@class="keyDetailsList"]//text()').extract()
        key_details_dict = {}
        for i in range(0, len(key_details), 2):
            key_details_dict[key_details[i]] = key_details[i + 1]

        # Property
        property_details_dict = {}
        property_details = response.xpath('//li[@class="entryItem "]').extract()
        property_details = [i.replace('<li class="entryItem "><span class="entryItemContent">', '') for i in property_details]
        property_details = [i.replace('<span>', '') for i in property_details]
        property_details = [i.replace('</span></span></li>', '') for i in property_details]
        property_details = [i for i in property_details if i.find('a href')==-1]

        for property_detail in property_details:
            if property_detail.find(':') >= 0:
                if len(property_detail.split(':')) == 2:
                    key, value = property_detail.split(':')
                    property_details_dict[key] = value
                else:
                    key = ''.join(i for i in property_detail.split(':')[:-1])
                    value = property_detail.split(':')[-1]
                    property_details_dict[key] = value
            else:
                property_details_dict[property_detail] = 1

        # School
        school_details_dict = {}
        school_name = response.xpath('//div[@class="school-title"]//text()').extract()
        school_ratings = response.xpath('//div[@class="gs-rating-col"]//text()').extract()
        school_ratings = [i for i in school_ratings if i != '/10']
        drop_list = [' • ', 'Students', 'Distance']
        school_info = response.xpath('//div[@class="sub-info font-color-gray-light font-size-small"]//text()').extract()
        school_info = [i for i in school_info if i not in drop_list]
        school_type = [school_info[i] for i in range(0, len(school_info)) if i%3==0]
        school_grade = [school_info[i+1] for i in range(0, len(school_info)) if i%3==0]
        school_serve = [school_info[i+2] for i in range(0, len(school_info)) if i%3==0]

        school_dist = response.xpath('//td[@class="distance-col"]/div[@class="value"]/text()').extract()
        for i in range(0, len(school_serve)):
            if school_serve[i] == 'Serves this home':
                school_details_dict[school_grade[i]] = [school_name[i], school_ratings[i], school_type[i], school_dist[i]]

        # Transportation
        scores_dict = {}
        transportation_details = response.xpath('//div[@class="score inline-block not-last"]//text()').extract()
        if len(transportation_details) == 4:
            key = transportation_details[3].replace('®','').replace(' ','_').lower()
            scores_dict[key] = transportation_details[0]
        elif len(transportation_details) == 8:
            key1 = transportation_details[3].replace('®', '').replace(' ', '_').lower()
            key2 = transportation_details[7].replace('®', '').replace(' ', '_').lower()
            scores_dict[key1] = transportation_details[0]
            scores_dict[key2] = transportation_details[4]
        else:
            scores_dict['walk_score'] = None
            scores_dict['transit_score'] = None

        bike_score = response.xpath('//div[@class="score inline-block"]//text()').extract()
        if bike_score:
            scores_dict['bike_score'] = bike_score[0]
        else:
            scores_dict['bike_score'] = None

        competitive_score = response.xpath('//div[@class="scoreTM"]//text()').extract()
        if competitive_score:
            scores_dict['competitive_score'] = competitive_score[0]
        else:
            scores_dict['competitive_score'] = None

        # Item
        item = RedfinItem()
        item['price'] = price
        item['beds'] = beds
        item['baths'] = baths
        item['sqft'] = sqft
        item['rermarks'] = remarks
        item['street'] = street
        item['zipcode'] = zipcode
        item['key_details_dict'] = key_details_dict
        item['property_details_dict'] = property_details_dict
        item['school_details_dict'] = school_details_dict
        item['scores_dict'] = scores_dict
        yield item