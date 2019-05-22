import re

file = open('test10mm.gcode', 'r')
lines = file.readlines()
file.close

h = re.compile(
    '(?i)^[gG0-3]{1,3}(?:\s+x-?(?P<x>[0-9.]{1,15})|\s+y-?(?P<y>[0-9.]{1,15})|\s+z-?(?P<z>[0-9.]{1,15}))*$')

for g in lines:
    i = h.match(g)
    if i:
        print(g, '->', i.groupdict())
    else:
        print(g, '->', None)
