from fake_useragent import UserAgent
from io import BytesIO
from PIL import Image
import urllib.parse
import requests
import time

class pinterest_image_scraping:

    def __init__(self, query: str, num_images: int, path: str):
        self.query = query
        self.encoded_query = urllib.parse.quote(self.query)
        self.num_images = num_images
        self.path = path
        
        self.image_urls = []
        self.bookmarks = [""]
        self.host = 'www.pinterest.jp'
        self.api_endpoint = f'https://{self.host}/resource/BaseSearchResource/get/'
        self.user_agent = UserAgent().chrome
        self.headers = {
                'authority': self.host,
                'accept': 'application/json, text/javascript, */*, q=0.01',
                'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
                'priority': 'u=1, i',
                'referer': f'https://{self.host}/',
                'user-agent': self.user_agent,
                'x-app-version': '4e166fb',
                'x-pinterest-appstate': 'active',
                'x-pinterest-pws-handler': 'www/search/[scope].js',
                'x-pinterest-source-url': f'/search/pins/?q={self.encoded_query}',
                'x-requested-with': 'XMLHttpRequest',
                }

        req = requests.get(f'https://{self.host}/search/pins/', params={'q': self.query})
        self.cookie_data = dict(req.cookies)

    def required_scraping_process(self):
        try:
            response = requests.get(
                    self.api_endpoint,
                    params={
                        'source_url': f'/search/pins/?q={self.encoded_query}',
                        'data': '{"options":{"article":"","appliedProductFilters":"---","price_max":null,"price_min":null,"query":"%s","scope":"pins","auto_correction_disabled":"","top_pin_id":"","filters":"","page_size":"14"},"context":{}}' % (self.query),
                        '_': str(time.time())
                        },
                    headers=self.headers,
                    cookies=self.cookie_data
                    )
            json_result = response.json()
            
            self.bookmarks[0] = json_result["resource_response"]["bookmark"]
            for obj in json_result["resource_response"]["data"]["results"]:
                images = obj["images"]["orig"]["url"]
                self.image_urls.append(images)
        except:
            print(
                    f'Error: {response.status_code}\n'
                    )
        else:
            print('\nWe have successfully acquired the first image data.')

    def main_scraping_process(self):
        if len(self.image_urls) <= self.num_images:
            self.headers['x-csrftoken']=self.cookie_data['csrftoken']
            while len(self.image_urls) <= self.num_images:
                response = requests.post(
                        self.api_endpoint,
                        data={
                            'source_url': f'/search/pins/?q={self.encoded_query}',
                            'data': '{"options":{"article":"","appliedProductFilters":"---","price_max":null,"price_min":null,"query":"%s","scope":"pins","auto_correction_disabled":"","top_pin_id":"","filters":"","page_size":"14","bookmarks":["%s"]},"context":{}}' % (self.query, self.bookmarks[0]),
                            },
                        headers=self.headers,
                        cookies=self.cookie_data
                        )
                
                json_result = response.json()

                for obj in json_result["resource_response"]["data"]["results"]:
                    images = obj["images"]["orig"]["url"]
                    self.image_urls.append(images)

                self.bookmarks[0] = json_result["resource"]["options"]["bookmarks"]

            print('Image is being saved...')
            for i in range(self.num_images):
                image_url = self.image_urls[i]
                r = requests.get(image_url)
                file_name = image_url.split("/")[7]
                image = Image.open(BytesIO(r.content))
                image.save(f'{self.path}/{file_name}')

            print('Image saved successfully!')
        else:
            print('Image is being saved...')
            for i in range(self.num_images):
                image_url = self.image_urls[i]
                r = requests.get(image_url)
                file_name = image_url.split("/")[7]
                image = Image.open(BytesIO(r.content))
                image.save(f'{self.path}/{file_name}')

            print('Image saved successfully!')

if __name__ == "__main__":
    query = input('Keywords of images you want to search：')
    num_images = input('Number of images you want to get：')
    path = input('PATH to save images：')

    instance = pinterest_image_scraping(query, int(num_images), path)
    instance.required_scraping_process()
    instance.main_scraping_process()
