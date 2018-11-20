#coding:utf-8
rows = int(20)
print ("空心正方形")
for i in range(0, rows):
    for k in range(0, rows):
        if i != 0 and i != rows - 1:
            if k == 0 or k == rows - 1:
                #由于视觉效果看起来更像正方形，所以这里*两侧加了空格，增大距离
                print (" * ",) #注意这里的","，一定不能省略，可以起到不换行的作用
            else:
                 print ("   ",) #该处有三个空格
        else:
            print (" * ",) #这里*两侧加了空格
        k += 1
    i += 1
    print ("\n")