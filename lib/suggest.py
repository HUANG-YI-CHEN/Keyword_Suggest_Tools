# -*- coding: utf-8 -*-
import re, sys
import time, random
import json
import copy
import chardet
import requests
import telnetlib
import multiprocessing as mp
from multiprocessing import Pool
from fake_useragent import UserAgent
from freeproxy import freeproxy

class suggest:
    ''' [class] '''

    def __init__(self, keyword):
        self.keyword = keyword
        self.options = {}
        self.selector = ''
        self.proxy_switch = False
        self.proxies = self.get_proxy()
        self.dicts = self.get()
        self.json = self.format_JSON()
        self.tokens = self.get_tokens(self.dicts['all'])

    ''' 取得 page 的 encoding '''
    def get_encoding(self, response):
        encoding = ''
        if re.findall(r'(?i)(?:charset=.*)', response.headers['content-type'], re.I&re.U):
            content_type = [ i.strip() for i in response.headers['content-type'].split('charset=') ]
            try:
                encoding = content_type[1]
            except Exception as e:
                raise e
        else:
            encoding = chardet.detect(response.content)["encoding"]
        return encoding

    def set_proxy_switch(self, proxy=None):
        if not proxy:
            self.proxy = False
        else:
            self.proxy = proxy

    def request_options(self, selector):
        # bing http://api.bing.com/osjson.aspx?query=apple&
        # google&youtube http://suggestqueries.google.com/complete/search?q=apple&client=toolbar&ds=!&hl=zh-tw
        # yahoo https://search.yahoo.com/sugg/ff?output=fxjson&appid=ffd&command=電腦軟體
        # yahoo https://sugg.search.yahoo.net/sg/?output=xml&nresults=20&appid=ffd&command=智慧型手機
        # google http://pagerank.tw/google-suggest/result.php
        # bing http://pagerank.tw/bing-suggest/result.php
        options = {
            'bing':{
                'url':'http://pagerank.tw/bing-suggest/result.php',
                'headers':{
                    'referer':'https://pagerank.tw/bing-suggest/',
                    'sec-fetch-mode':'cors',
                    'sec-fetch-site':'same-origin'
                },
                'params': {
                        'q' :'',
                        'lang': '1'
                }
            },
            'google':{
                'url': 'http://pagerank.tw/google-suggest/result.php',
                'headers':{
                    'accept':'*/*',
                    'accept-encoding':'gzip, deflate, br',
                    'accept-language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'referer':'https://pagerank.tw/google-suggest/',
                    'sec-fetch-mode':'cors',
                    'sec-fetch-site':'same-origin',
                },
                'params': {
                    'q' :'',
                    'dc': 'Google.com.tw'
                }
            },
            'yahoo':{
                'url': 'https://search.yahoo.com/sugg/ff',
                'headers':{
                    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-encoding':'gzip, deflate, br',
                    'accept-language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'sec-fetch-mode':'navigate',
                    'sec-fetch-site':'none',
                    'upgrade-insecure-requests':'1'
                },
                'params': {
                    'command' :'',
                    'output': 'firefox',
                    'appid':'ffd',
                    'nresults':'20'
                }
            },
            'youtube':{
                'url': 'http://suggestqueries.google.com/complete/search',
                'params': {
                    'q':'',
                    'client':'firefox',
                    'ds':'yt',
                    'hl':'zh-tw'
                }
            },
            'google_2':{
                'url': 'http://suggestqueries.google.com/complete/search',
                'params': {
                    'q':'',
                    'client':'firefox',
                    'ds':'!',
                    'hl':'zh-tw'
                }
            },
            'bing_2':{
                'url': 'https://api.bing.com/osjson.aspx',
                'headers':{},
                'params': {
                    'query':''
                }
            }
        }.get(selector,'error')
        options.update()
        try:
            options['headers'].update({'user-agent':UserAgent().random})
        except:
            options['headers'] = {'user-agent':UserAgent().random}
        return (options)

    def fetch(self, url=None, headers=None, params=None, proxy=False):
        content = ''
        encoding = ''
        if url and params:
            if proxy==False:
                with requests.session().get(url = url, headers = headers, params = params, stream=True) as req:
                    if req.status_code == 200:
                        try:
                            encoding = self.get_encoding(req)
                            content = req.content.decode(encoding, errors='ignore')
                        except:
                            try:
                                content = req.content.decode('gb2312', errors='ignore')
                            except Exception as e:
                                raise e
            else:
                try:
                    with requests.session().get(url = url, headers = headers, params = params, stream=True, proxies=self.proxies, timeout=3) as req:
                        if req.status_code == 200:
                            try:
                                encoding = self.get_encoding(req)
                                content = req.content.decode(encoding, errors='ignore')
                            except:
                                try:
                                    content = req.content.decode('gb2312', errors='ignore')
                                except Exception as e:
                                    raise e
                except:
                    with requests.session().get(url = url, headers = headers, params = params, stream=True) as req:
                        if req.status_code == 200:
                            try:
                                encoding = self.get_encoding(req)
                                content = req.content.decode(encoding, errors='ignore')
                            except:
                                try:
                                    content = req.content.decode('gb2312', errors='ignore')
                                except Exception as e:
                                    raise e
        else:
            raise NameError('url ,headers and params must fill in a value')
        return (content)

    def parse(self, content, selector):
        keyword = self.keyword
        lists = []
        if selector == 'bing':
            try:
                lists = content[0:content.index('<!--')].replace( keyword+' '+'<BR>','<BR>' ).split('<BR>')[0:]
            except Exception as e:
                raise e
        elif selector == 'bing_2':
            try:
                lists = json.loads(content)[1]
            except Exception as e:
                raise e
        elif selector == 'google':
            try:
                lists = content.split('<BR>')[0:-1]
            except Exception as e:
                raise e
        elif selector == 'google_2':
            try:
                lists = json.loads(content)[1]
            except Exception as e:
                raise e
        elif selector == 'yahoo':
            try:
                content = json.loads(content)['gossip']['results']
                [lists.append(i['key']) for i in content]
            except Exception as e:
                raise e
        elif selector == 'youtube':
            try:
                lists = json.loads(content)[1]
            except Exception as e:
                raise e
        lists = list( sorted( set( lists ), key = lists.index ) )
        if '' in lists :
            lists.remove( '' )
        return (lists)

    def gather(self, selector):
        keyword = self.keyword
        lists = []
        flags = False

        if selector == 'bing':
            try:
                self.options = self.request_options('bing')
                self.options['params']['q'] = keyword
                content = self.fetch(self.options['url'], self.options['headers'], self.options['params'], self.proxy_switch)
                lists = self.parse(content,selector)
            except:
                try:
                    flags = True
                    self.selector = 'bing_2'
                    self.options = self.request_options('bing_2')
                    self.options['params']['query'] = keyword
                    copyoptions = copy.deepcopy(self.options)
                    copyoptions['params']['query'] = keyword + ' '
                    content1 = self.fetch(self.options['url'], self.options['headers'], self.options['params'], self.proxy_switch)
                    content2 = self.fetch(self.options['url'], self.options['headers'], copyoptions['params'], self.proxy_switch)
                    lists = self.parse(content1,self.selector) + self.parse(content2,self.selector)
                except:
                    print("Unexpected error:",sys.exc_info())
        elif selector == 'google':
            try:
                self.options = self.request_options('google')
                self.options['params']['q'] = keyword
                content = self.fetch(self.options['url'], self.options['headers'], self.options['params'], self.proxy_switch)
                lists = self.parse(content,selector)
            except:
                try:
                    flags = True
                    self.selector = 'google_2'
                    self.options = self.request_options('google_2')
                    self.options['params']['q'] = keyword
                    copyoptions = copy.deepcopy(self.options)
                    copyoptions['params']['q'] = keyword + ' '
                    content1 = self.fetch(self.options['url'], None, self.options['params'], self.proxy_switch)
                    content2 = self.fetch(copyoptions['url'], None, copyoptions['params'], self.proxy_switch)
                    lists = self.parse(content1,self.selector) + self.parse(content2,self.selector)
                except Exception as e:
                    raise e
        elif selector == 'yahoo':
            try:
                flags = True
                self.options = self.request_options('yahoo')
                self.options['params']['command'] = keyword
                copyoptions = copy.deepcopy(self.options)
                copyoptions['params']['command'] = keyword + ' '
                content1 = self.fetch(self.options['url'], self.options['headers'], self.options['params'], self.proxy_switch)
                content2 = self.fetch(copyoptions['url'], self.options['headers'], copyoptions['params'], self.proxy_switch)
                lists = self.parse(content1,selector) + self.parse(content2,selector)
            except Exception as e:
                raise e
        elif selector == 'youtube':
            try:
                flags = True
                self.options = self.request_options('youtube')
                self.options['params']['q'] = keyword
                copyoptions = copy.deepcopy(self.options)
                copyoptions['params']['q'] = keyword + ' '
                content1 = self.fetch(self.options['url'], None, self.options['params'], self.proxy_switch)
                content2 = self.fetch(copyoptions['url'], None, copyoptions['params'], self.proxy_switch)
                lists = self.parse(content1,selector) + self.parse(content2,selector)
            except Exception as e:
                raise e

        if flags == True:
            lists = list( sorted( set( lists ), key = lists.index ) )
            if '' in lists :
                lists.remove( '' )
        return (lists)

    def get(self):
        fetch_source = ['google','bing','youtube','yahoo']
        dicts = {}

        pool = Pool(processes=mp.cpu_count())
        for proc_i in fetch_source:
            result = pool.apply_async(self.gather, args=(proc_i,))
            dicts.update({proc_i:result.get()})
        pool.close()
        pool.join()

        _emerge = []
        [_emerge.extend(dicts.get(i)) for i in dicts]
        _emerge = list( sorted( set( _emerge ), key = _emerge.index ) )
        dicts.update( {'all':_emerge} )
        return (dicts)

    def dict2json(self, dicts):
        return json.dumps(dicts, ensure_ascii=False)

    def format_JSON(self, mode=None):
        dicts = self.dicts
        if not mode:
            mode = 'all'
        if mode != 'all':
            for i in dicts:
                if i!=mode and i!='all':
                    dicts[i]=[]
                else:
                    dicts['all'] = dicts[i]
        return (self.dict2json(dicts))

    def generator(self):
        self.dicts = self.get()
        self.json = self.format_JSON()
        self.tokens = self.get_tokens(self.dicts['all'])

    def match(self, args):
        if re.compile(r'^(?:(?:\w|[\u4E00-\u9FA5])(?:[\(\)\-])*\s*)+$').match(args):
            return 1
        elif re.compile('^[\u4E00-\u9FA5]+$').match(args):
            return 2
        elif re.compile('^[a-zA-Z]+$').match(args):
            return 3
        return 0

    ### Suggest Data Handler Function ###
    def content2sql(self, words):
        return (words.replace('\'','\'\''))

    def get_tokens(self, lists):
        sets = []
        for i in range(len(lists)):
            sp = re.split(r'\s+',lists[i])
            for j in range(len(sp)):
                args = ''
                for k in range(j,len(sp)):
                    if k == j:
                        args += (str(sp[k])).strip()
                    else:
                        args += ' '+(str(sp[k])).strip()
                args = args.replace("\xFFFD", "").strip()
                if self.match(args) > 0 and args.strip() != '' :
                    sets.append(args)
        sets = list( sorted( set( sets ), key = sets.index ) )
        if '' in sets:
            sets.remove('')
        return (sets)

    def tokens2args(self, tokens):
        args2sql = ''
        if tokens:
            for i in range(len(tokens)):
                if i < (len(tokens)-1):
                    args2sql += '(N\''+self.content2sql(tokens[i])+'\')'+','
                else:
                    args2sql += '(N\''+self.content2sql(tokens[i])+'\')'
        else:
            args2sql = '(N\'\')'
        return (args2sql)

    def check_proxy(self, cur_proxy):
        c_proxy = (cur_proxy.replace('https://','')).replace('http://','')
        proxy = c_proxy.split(':')
        ip = proxy[0]
        port = proxy[1]
        try:
            telnetlib.Telnet(ip, port=port, timeout=3)
        except:
            return False
        return True

    def get_proxy(self):
        fp = freeproxy()
        proxy = fp.cur_proxy
        while self.check_proxy(proxy):
            proxy = fp.get_proxy()
        dicts = {}
        if 'https' in proxy:
            dicts = {'https':proxy.replace('https://','')}
        else:
            dicts = {'http':proxy.replace('http://','')}
        return (dicts)

def test():
    a = time.time()
    keyword = u'蔡英文'
    response = suggest(keyword)
    for i in response.dicts:
        print(i,response.dicts[i])
    print("spend time:",time.time()-a)

if __name__ == '__main__':
    test()