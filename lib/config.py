#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import os
'''
ConfigParser Support Unicode
https://my.oschina.net/cppblog/blog/384099
http://laochake.iteye.com/blog/443704
http://www.cnblogs.com/zhaoweiwei/p/ConfigParser.html
'''

__all__ = ['Config']

class Config:
    ''' [class] '''
    def __init__(self, path = None, file = None):
        ''' [construct] '''
        if path is None:
            if 'lib' in os.path.abspath(''):
                self.path = os.path.abspath('').replace('lib','')
            else:
                self.path = os.path.abspath('')+'\\'
        else:
            self.path = path
        if file is None:
            if os.path.exists(self.path+'config.ini'):
                self.file = 'config.ini'
            else:
                self.file = file
        else:
            self.file = file
        self.config = self.__read(self.path, self.file)

    def __str__(self):
        return "dir : '%s'\nfilename : '%s'\n"%(self.path,self.file)

    def __read(self, path = None, file = None):
        ''' [private] Returns class configparser.ConfigPaser()  .
            {path} : absolute path of the configuration file
            {file} : file name of the configuration file
        '''
        if path is None:
            self.path = self.path
        else:
            self.path = path
        if file is None:
            self.file = self.file
        else:
            self.file = file
        config = configparser.ConfigParser()
        config.read(self.path + self.file, encoding='utf-8-sig')
        return config

    def get(self, section = None):
        ''' [public] Returns dicts , a configuration file info.
            {section} : None -> all sections info, Not None -> one section info
        '''
        sections = self.config.sections()
        if section is not None :
            sections = [section]
        dicts = {}
        for i in sections:
            dicts.setdefault(i)
            for key, value in self.config.items(i):
                if not dicts.get(i) :
                    dicts[i]=dict({key:value})
                else:
                    dicts[i].setdefault(key,value)
        return (dicts[section] if (section is not None) else dicts)

    def sections(self, section = None):
        return (self.config.sections())

    def show(self, section = None):
        dicts = self.get(section)
        for i in sorted(dicts.keys()):
            print ('['+i+']')
            for key, value in sorted(dicts[i].items()):
                print(key,'=',value)
            print ('')
            if section is not None:
                break

    __repr__ = __str__

# def test():
#     cfg = Config()
#     cfg.show()

# if __name__ == '__main__':
#     test()