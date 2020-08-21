f1 = open("TestDebug20.yuv", 'r')
f2 = open("TestDebug21.yuv", 'r')
f3 = open("Convolutuion.yuv", 'w')

for i in range(0,(1280*720/8)):
    data0 = f2.read(2)
    data1 = f1.read(8)
    data2 = f2.read(2)
    f3.write(data0)
    f3.write(data1)
    f3.write(data2)

f1.close()
f2.close()
f3.close()
