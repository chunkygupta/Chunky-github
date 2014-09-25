'''
@author : Chunky Gupta  Date: 04/1/2014>
@updated : Ankit Singhal Date : 04/10/2014
'''

import sys
sys.path.append('.')

import stackexchange

so = stackexchange.Site(stackexchange.StackOverflow)
stats = so.tags()
f = open ('C:\\Users\\chunkygupta\\Dropbox\\Project_ir\\data\\Top_30000_Tags.txt', 'w')

count_item = 0
for item in stats:
    try:
        count_item += 1
        string_tag =  str(count_item) + ".\t"+ item.name + "\t" + str(item.count) + "\n"
        f.write(string_tag)
        if (count_item == 30000):
            break
    except:
        count_item += 1