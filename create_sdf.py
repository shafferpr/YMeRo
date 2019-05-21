import numpy as np
import math
import sdf as sdf
import struct as struct
import sys
import os

#creat array of 3 numbers
x=np.arange(0,30,0.5,dtype=np.float32)
y=np.arange(0,30,0.5,dtype=np.float32)
z=np.arange(0,15,0.5,dtype=np.float32)
q=np.vstack(np.meshgrid(x,y,z,indexing='ij')).reshape(3,-1).T #array of 3d numbers

def sdf(x):
    gp=[5,10,15,20,25]
    gridpoints=np.vstack(np.meshgrid(gp,gp,indexing='ij')).reshape(2,-1).T
    value=0.5
    for gridpoint in gridpoints:
        if math.sqrt((x[0]-gridpoint[0])**2+(x[1]-gridpoint[1])**2) < 2:
            value = -0.5
    if x[2]>9.5 or x[2]<5.5:
        value=-0.5
    return value

#apply a function to each point in array, to create the sdf 
qq=[sdf(x) for x in q] #sdf values

#write to file
qnp=np.asarray(qq,dtype=np.float32)
qnp.tofile("q.dat")

#prepend the head to the file
with open("temp","w") as f:
    f.write("15 30 30\n")
    f.write("30 60 60\n")
os.system("cat temp q.dat >qq.dat") 

