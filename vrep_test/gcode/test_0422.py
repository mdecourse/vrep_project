file = open('test10mm.gcode','r')
lines = file.readlines()
file.close

for line in lines:
    line = line.strip()
    print(line)
    