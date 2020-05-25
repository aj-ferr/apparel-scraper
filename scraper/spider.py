import scrapy
from scraper.items import ProductItem

# php -S localhost:8080
# scrapy crawl products
# scrapy shell -s USER_AGENT='custom user agent' "http://localhost:8080/index.html"

sanmar_login = {
    'w3exec': 'login', 
    'customerNo': '',
    'email': '',
    'password': '', 
    'send': ''
}


class ProductSpider(scrapy.Spider):

    name = "products"

    custom_settings = {
        "IMAGES_STORE": 'images',
        "DOWNLOAD_DELAY": 1,
        "ITEM_PIPELINES": {
            'scraper.pipelines.ProductImagePipeline': 100,
            'scraper.pipelines.JsonWriterPipeline': 200
        }
    }

    def start_requests(self):
        return [scrapy.FormRequest(
            url = "https://www.sanmarcanada.com/flashconnect/index/index/",
            formdata = sanmar_login,
            callback = self.after_login
        )]

    def after_login(self, response):
        if 'login' in response.url:
            self.logger.error("[!] LOGIN FAILED")
            return
        
        return [scrapy.Request(url=url, meta={'product': False}) for url in self.start_urls]


    def parse(self, response):
        if (response.meta.get('product', False)):
            yield self.parse_product(response)

        else:
            for product in response.css('.products-grid .item'):
                name = product.css('h2 a::text').get()
                url = product.css('h2 a::attr(href)').get()

                if 'DISCONTINUED' not in name:
                    yield scrapy.Request(url=url, meta={'product': True}, callback=self.parse)


    def parse_product(self, response):
        name = response.css('.product-name h1::text').get()
        desc = response.css('.short-description .std ul').get().replace("\n", "")
        imgs = response.css('#itemslider-zoom')[0]
        urls = imgs.css(".item a::attr(href)").getall()
        clrs = imgs.css('.item a::attr(title)').getall()
        sku = name.split('.')[1].replace(' ', '').lower()
        
        sizes = response.css('.productgrid .header')[0].css('td::text').getall()[2:]
        prices = response.css('.productgrid .body')[0].css('.price::text').getall()

        return ProductItem(
            name=name, 
            sku=sku, 
            description=desc, 
            colors=clrs, 
            image_urls=urls, 
            sizes=dict(zip(sizes, prices))
        )