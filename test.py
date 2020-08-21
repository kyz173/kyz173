import numpy as np

y = np.array([[[10.0,11.1,12.2],
    [1,1,1],
    [1,1,1]]]
    ,dtype = np.float64)

a = np.array([1],dtype = np.int32)
print(a.shape)

y = np.array(y[0][0][0], dtype = np.int32)

#x = np.array([10.1,2.0,3,4,5], dtype = np.int32)

print (y)

data = ''

data += ' %d' %(y)

print (data)

print (y.shape)
