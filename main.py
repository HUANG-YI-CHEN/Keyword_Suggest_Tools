# -*- coding: utf-8 -*-
import os, sys
import time
import random
import urllib
import datetime
from lib.config import Config
from lib.connect2sql import MSSQL
from lib.suggest_mult import suggest

clear = lambda: os.system( 'cls' )
unicode_cmd = lambda: os.system( 'chcp 65001 &' )

def get_cur_datetime():
    return datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

def timespent(calls):
    start = time.time()
    # time.sleep( random.uniform(1, 3) )
    calls
    end = time.time()
    print ('Cost : %.4f'%( abs(end-start) ))

def suggesttest():
    keyword = 'smartphone'
    response = suggest(keyword)
    print(response)

def processCrawler():
    # initalize variable
    # argvs = sys.argv[0:]
    cfg = Config()
    mode = int(cfg.get('mode')['run'])
    config = cfg.get('database')
    divisor = int(cfg.get('control')['divisor']) if len(sys.argv) == 1 else int(sys.argv[1:2][0])
    remainder = int(cfg.get('control')['remainder']) if len(sys.argv) == 1 else int(sys.argv[2:3][0])
    keyword = cfg.get('control')['domainkeyword']
    cycle = int(cfg.get('control')['counter']) if len(sys.argv) == 1 else int(sys.argv[3:4][0])
    runtimelimit = int(cfg.get('control')['runtimelimit'])
    conn = MSSQL( hostname=config['hostname'], username=config['username'], password=config['password'], database=config['database'] )

    # start
    defined_mode = {0:'all',1:'google',2:'bing',3:'youtube',4:'yahoo'}
    time_start = time.time()
    sql = """
        declare @type int = (select EID from Entity where CName=N'Suggest' and EName=N'Suggest')
        declare @divisor int = %s
        declare @remainder int = %s
        select * from dbo.fn_getObjectData(@type, @divisor, @remainder)
        """%(divisor,remainder)
    try:
        res = conn.execQuery(sql)
    except Exception as e:
        raise e

    if not res:
        tokens = []
        while not tokens:
            try:
                response = suggest(keyword)
                tokens = response.tokens
                json = response.content2sql(response.format_JSON(defined_mode[mode]))
                args2sql = response.tokens2args(tokens)
            except Exception as e:
                pass
        sql =   """
                declare @EID int = (select EID from Entity where CName=N'Suggest' and EName=N'Suggest')
                declare @Keyword nvarchar(800) = N'%s'
                declare @JSON nvarchar(max) = N'%s'
                declare @Tokens nvarchar(max) = N'%s'
                exec dbo.xp_insertObjectData @EID, @Keyword, @JSON, @Tokens
                """%(keyword, json, response.content2sql(args2sql))
        try:
            conn.execNonQuery(sql)
        except:
            print('error_1')
            with open(os.path.abspath(os.curdir)+'errorlog_'+get_cur_datetime()+'.txt','w+') as f:
                f.write('***   error_1   ***\n'+sql)
            # print (os.path.expanduser('~\Desktop'))
    counter = 0
    while True:
        if counter%20==0:
            clear()
        if counter == int(cycle) or (time.time()-time_start)>runtimelimit:
            break
        time.sleep( random.uniform(1, 3) )
        sql = """
            declare @type int = (select EID from Entity where CName=N'Suggest' and EName=N'Suggest')
            declare @divisor int = %s
            declare @remainder int = %s
            select * from dbo.fn_getObjectData(@type, @divisor, @remainder)
            """%(divisor,remainder)
        try:
            res = conn.execQuery(sql)
        except Exception as e:
            raise e
        if res:
            keyword = res[0][1]
            print(keyword)
            tokens = []
            while not tokens:
                try:
                    response = suggest(keyword)
                    tokens = response.tokens
                    json = response.content2sql(response.format_JSON(defined_mode[mode]))
                    args2sql = response.tokens2args(tokens)
                except Exception as e:
                    raise e
            sql =   """
                    declare @EID int = (select EID from Entity where CName=N'Suggest' and EName=N'Suggest')
                    declare @Keyword nvarchar(800) = N'%s'
                    declare @JSON nvarchar(max) = N'%s'
                    declare @Tokens nvarchar(max) = N'%s'
                    exec dbo.xp_insertObjectData @EID, @Keyword, @JSON, @Tokens
                    """%(keyword, json, response.content2sql(args2sql))
            try:
                conn.execNonQuery(sql)
            except:
                print('error_2')
                with open(os.path.abspath(os.curdir)+'errorlog_'+get_cur_datetime()+'.txt','w+') as f:
                    f.write('***   error_2   ***\n'+sql)
        else:
            print('sql query no data !!')
            with open(os.path.abspath(os.curdir)+'errorlog_'+get_cur_datetime()+'.txt','w+') as f:
                f.write('***   sql query no data !!   ***\n'+sql)
            conn.close()
            break
        counter+=1
    conn.close()

if __name__ == '__main__':
    processCrawler()