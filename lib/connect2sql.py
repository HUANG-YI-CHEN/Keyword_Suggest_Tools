#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymssql
import psycopg2

__all__ = ['MSSQL','PGSQL']

class MSSQL:
    ''' [class] '''

    def __init__( self, hostname, username, password, database ):
        ''' [construct] '''
        self.hostname = hostname
        self.username = username
        self.username = username
        self.password = password
        self.database = database
        self.cursor = self.__connect()

    def __connect( self ):
        ''' [private] Returns class pymssql.connect().coursor(), Get Connection '''
        if not self.database :
            raise NameError("Not Set Database Info .")

        self.connect = pymssql.connect( host = self.hostname, user = self.username, password = self.password, database = self.database, charset="utf8")
        cursor = self.connect.cursor()

        if not cursor:
            raise NameError("Connect Database Failed .")
        else:
            return cursor

    def execQuery( self, sql ):
        ''' [public] Returns list, Fetech all select guery  '''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def execNonQuery( self, sql ):
        ''' [public] No Returns, Excute ( insert, delete, update, stored procedure )  '''
        self.cursor.execute(sql)
        self.connect.commit()

    def execNonQueryMany( self, sql, args ):
        ''' [public] No Returns, Excute ( insert, delete, update, stored procedure )  '''
        self.cursor.executemany(sql,args)
        self.connect.commit()

    def close( self ):
        ''' [public] No Returns, Close database Connect   '''
        self.connect.close()

class PGSQL:
    ''' [class] '''

    def __init__( self, hostname, username, password, database ):
        ''' [construct] '''
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database
        self.cursor = self.__connect()

    def __connect( self ):
        ''' [private] Returns class psycopg2.connect.coursor(), Get Connection '''
        if not self.database :
            raise NameError("Not Set Database Info .")

        self.connect = psycopg2.connect("dbname="+ self.database +" user="+ self.username +" host="+ self.hostname +" password="+ self.password)
        cursor = self.connect.cursor()

        if not cursor:
            raise NameError("Connect Database Failed .")
        else:
            return cursor

    def execQuery( self, sql ):
        ''' [public] Returns list, Fetech all select guery  '''
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def execNonQuery( self, sql ):
        ''' [public] No Returns, Excute ( insert, delete, update, stored procedure )  '''
        self.cursor.execute(sql)
        self.connect.commit()

    def close( self ):
        ''' [public] No Returns, Close database Connect   '''
        self.connect.close()

# def test():
#     sqlserver = MSSQL( hostname='x.x.x.x',username='xxx', password='xxxxx',database='xxxx' )
#     sql = ' select top 1 * from object '
#     results = sqlserver.execQuery( sql )
#     print (results)
#     sqlserver.close()

# if __name__ == '__main__':
#     test()