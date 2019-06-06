import numpy as np
import math
import sys
import os


npores=int(sys.argv[1])
poresize=float(sys.argv[2])


x=np.arange(0,30,1.0,dtype=np.float32)
y=np.arange(0,30,1.0,dtype=np.float32)
z=np.arange(0,30,1.0,dtype=np.float32)
q=np.vstack(np.meshgrid(x,y,z,indexing='ij')).reshape(3,-1).T #array of 3d numbers


x=np.random.uniform(0,30,npores)
y=np.random.uniform(0,30,npores)
z=np.random.uniform(10,20,npores)
pores=np.vstack([x,y,z]).T
throats=[]

def poresize(pore):
    psize=1.5+2.5*(pore[2]-10)/10
    return psize

def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)

def norm(p1):
    return p1[0]**2+p1[1]**2+p1[2]**2


def inthroat(node1,node2,x):
    throatlength=distance(node1,node2)
    distanceFromLine=math.sqrt((norm(x-node1)*norm(node1-node2)-np.dot(node1-x,node2-node1)**2)/(norm(node2-node1)))
    midpoint=0.5*(node1+node2)
    distanceFromMidpoint=distance(x,midpoint)
    parallelDistance=math.sqrt(distanceFromMidpoint**2-distanceFromLine**2)
    ps1=poresize(node1)
    ps2=poresize(node2)
    d1=distance(x,node1)
    d2=distance(x,node2)
    dp=0
    if d1 >d2:
        dp=distanceFromMidpoint+throatlength/2
    else:
        dp=throatlength/2-distanceFromMidpoint
    adjustedporesize=ps1+dp*(ps2-ps1)/throatlength
    if distanceFromLine<adjustedporesize and parallelDistance < (throatlength/2):
        return True
    else:
        return False

for idx, pore in enumerate(pores):
    distances=[distance(pore,x) for x in pores]
    neighbors=np.argsort(distances)
    throats.append([idx,neighbors[1]])
    throats.append([idx,neighbors[2]])


def sdf(x):
    value=0.5
    for pore in pores:
        if distance(x,pore) < poresize(pore):
            value = -0.5
    for throat in throats:
        if inthroat(pores[throat[0]],pores[throat[1]],x):
            value=-0.5
    if x[2]>20 or x[2]<10:
        value=-0.5
    return value

#apply a function to each point in array, to create the sdf 
qq=[sdf(x) for x in q] #sdf values

#write to file
qnp=np.asarray(qq,dtype=np.float32)
qnp.tofile("q.dat")

#prepend the head to the file
with open("temp","w") as f:
    f.write("30 30 30\n")
    f.write("30 30 30\n")
os.system("cat temp q.dat >qq.dat") 

