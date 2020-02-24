# -*- coding: utf-8 -*-
import chardet
import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup as bs
from fake_headers import Headers

class freeproxy:
    ''' [class] '''

    def __init__(self, code=None):
        self.code = code
        self.url = 'https://free-proxy-list.net/'
        self.headers = self.get_header(browser="chrome", os="win", headers=False)
        self.proxy_list = self.get()        
        self.cur_proxy = self.get_proxy()

    def get_header(self,browser=None, os=None, headers=None):
        if not browser:
            browser = "chrome"
        if not os:
            os = "win"
        if not headers:
            headers = False
        return Headers(browser=browser, os=os, headers=headers)

    def set_header(self,browser=None, os=None, headers=None):
        self.headers=self.get_header(browser, os, headers)

    def parse(self, content):
        result=[]
        try:
            soup = bs(content, 'html.parser')
            for items in soup.select("#proxylisttable tbody tr"):
                data = ([list(filter(None, item))[0] for item in items.select("td")[:]])
                length = len(data)
                dicts = [dict(zip(['ip','port','code','country','anonymity','google','https','last checked'], data[i:i+length])) for i in range(0, len(data), length)]
                result.append(dicts[0])
        except Exception as e:
            raise e
        return result

    async def get_encoding(self, response):
        encoding = ''
        if not response.charset:
            try:
                content = await response.read()
                encoding = chardet.detect(content)["encoding"]
            except Exception as e:
                raise e
        else:
            encoding = response.charset
        return encoding

    async def fetch(self, url):
        content = ''
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=self.headers.generate()) as response:
                if response.status == 200:
                    try:
                        encoding = await self.get_encoding(response)
                        content = await response.text(encoding)
                    except Exception as e:
                        raise e
        return content

    async def gather(self, loop):
        content = await self.fetch(self.url)
        return self.parse(content)

    def get(self):
        sets = []
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        sets = loop.run_until_complete(self.gather(loop))
        loop.close()
        return (sets)

    def get_proxy(self):
        proxy_list = []
        proxy = ''
        if self.code:
            for i in self.proxy_list:
                if i['code'] == self.code and i['https'] == 'no':
                    proxy_list.append(i)
        else:
            for i in self.proxy_list:
                if i['https'] == 'no':
                    proxy_list.append(i)
        
        if proxy_list:
            rnd = random.randint(0,len(proxy_list)-1)
            proxy = ( 'https' if proxy_list[rnd]['https'] == 'yes' else 'http') +'://'+proxy_list[rnd]['ip']+':'+proxy_list[rnd]['port']

        return (proxy)

# def test():
#     fp = freeproxy()
#     # for i in fp.proxy_list:
#     #     print(i)
#     print(fp.cur_proxy)

# if __name__ == '__main__':
#     test()