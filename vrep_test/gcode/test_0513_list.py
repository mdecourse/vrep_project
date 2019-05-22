'''
list = [1.1, -23, 5530, 41, 0.0]
a = list[2] * list[4]
print(a)
'''

f = open('gcode.txt', 'r')

for line in f.readlines(): 
    line = line.split(',') 
    print(float(line[0]),line[2],line[2])

 
f.close()