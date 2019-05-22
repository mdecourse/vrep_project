import re


DEFAULT_NC_SYNTAX = ("(?:G([0-9]?\d+\.?\d*))?(?:M([+-]?\d+\.?\d*))?(?:\sF([+-]?\d+\.?\d*))?(?:\sS([+-]?\d+\.?\d*))?(?:\sX([+-]?\d+\.?\d*))?(?:\sY([+-]?\d+\.?\d*))?(?:\sZ([+-]?\d+\.?\d*))?(?:\sE([+-]?\d+\.?\d*))?(?:\sX([+-]?\d+\.?\d*))?(?:\sY([+-]?\d+\.?\d*))?(?:\sF([+-]?\d+\.?\d*))?(?:\sZ([+-]?\d+\.?\d*))?(?:\ +|\w+|\,\w+)?(?:,?\ \w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?)?(?:;\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?)?(?:[(]\w+\ \w+\ \w+\ \w+\))?(?:;\w+\ ?\w+)?")

with open('test1.gcode', 'r', encoding='utf-8') as f:
    gcord = f.read()
    
f = open('gcode.txt', 'w')

def _match(patten, doc):
    yield from re.compile(patten, re.MULTILINE).finditer(doc)


for m in _match(DEFAULT_NC_SYNTAX, gcord):
    mx = m.group(5)
    my = m.group(6)
    mz = m.group(7)
    if mx is None and my is None and mz is None:
        None
    elif mx is None and my is None and mz is not None:
        mx = 0.0
        my = 0.0
        f.write(str(mx) + ' ' + str(my) + ' ' + str(mz) + '\n')
    elif mx is not None and my is not None and mz is None:
        mz = 0.0
        f.write(str(mx) + ' ' + str(my) + ' ' + str(mz) + '\n')
    elif mx is not None and my is None and mz is None:
        None
    else:
        f.write(str(mx) + ' ' + str(my) + ' ' + str(mz) + '\n')
f.close()
    
