import scrapy
import json
from datetime import datetime
from scrapy.pipelines.images import ImagesPipeline


class ProductImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        urls = item['image_urls']
        colors = item['colors']
        idx = list(range(len(urls)))

        for url, clr, i in zip(urls, colors, idx):
            yield scrapy.Request(url, meta={'sku': item['sku'], 'color': clr, 'num': i})


    def file_path(self, request, response=None, info=None):
        i = request.meta['num']
        sku = request.meta['sku'].lower()
        ext = request.url.split('.')[-1]
        clr = request.meta['color'].lower()

        if (request.meta['num'] == 0):
            return f"{sku}-thumbnail.{ext}"
        else:
            color = ''.join(map(lambda l : '' if l in '/ ' else l, clr))
            return f"{sku}-{color}.{ext}"



class JsonWriterPipeline():

    def open_spider(self, spider):
        self.json = {'items': []}
        date = datetime.now().strftime("%d-%m-%Y_%I:%M%p")
        self.file = open(f'Products_{date}.json', 'w')


    def close_spider(self, spider):
        self.file.write(json.dumps(self.json))
        self.file.close()


    def process_item(self, item, spider):
        urls = map(lambda img : img['path'], item['images'])
        colors = zip(item['colors'], [url for url in urls])
        item['swatches'] = [{'color': clr, 'image': url} for clr, url in colors]

        del item['colors']
        del item['images']
        del item['image_urls']

        self.json['items'].append(dict(item))

        return item
