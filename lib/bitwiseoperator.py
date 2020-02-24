# -*- coding: utf-8 -*-
import re, sys

class bitwiseoperator:
    ''' [class] '''

    def __init__(self):
        self.value = 0

    def get_bits(self, value, posistion):
        if isinstance( posistion, int ) is True:
            value = 1 if value == ( value | ( 0x1<<( posistion-1 ) ) ) else 0
        else:
            lists = []
            for i in posistion:
                lists.append( 1 if value == ( value | ( 0x1<<( i-1 ) ) ) else 0 )
            value = lists
        return (value)

    def set_bits(self, value, posistion, bit):
        if isinstance( posistion, int ) is True:
            value = ( value | ( 0x1<<( posistion-1 ) ) ) if bit==1 else ( value & ( ~( 0x1<<( posistion-1 ) ) ) )
        else:
            tmp=0x0
            for i in range(len(posistion)):
                tmp = ( tmp | ( 0x1<<( posistion[i]-1 ) ) )
            if bit == 1:
                value = ( value | tmp )
            else:
                value = ( value & ( ~tmp ) )
        return (value)

    def byte2int(self, value):
        value = '0x'+ str(value)[ 2: len( str( value ) )-1 ].replace('\\n','').replace('\\x','')
        convert = int( value, 16 )
        return (convert)

# def test():
#     l = ['蔡英文fb','蔡英文x馬英九','麥當勞A餐','abc-z aaa','abc aa','蔡(Tsai)','iphone 8','a!','我要當A咖@@']
#     for i in l:
#         if re.compile(r'^(?:(?:\w|[\u4E00-\u9FA5\(\)\-])\s*)+$').match(i):
#             print(i)

# if __name__ == '__main__':
#     test()