import numpy as np
import math
import sys
import os


#npores=int(sys.argv[1])


class PoreNetwork(object):
    def __init__(self,npores,boxsize,lowerc,upperc):
        self.npores=npores
        self.boxsize=boxsize
        self.lowerc=lowerc
        self.upperc=upperc
        self.q=self.createGrid()
        self.pores=self.createPores()
        self.gridpores=self.createGridPores()
        self.throats=self.createThroats()

    def poresize(self,pore):
        psize=3+7*(pore[2]-float(self.lowerc))/float(self.upperc-self.lowerc)
        return psize

    def distance(self,p1,p2):
        return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)

    def norm(self,p1):
        return p1[0]**2+p1[1]**2+p1[2]**2
        
    def createGrid(self):
        x=np.arange(0,self.boxsize,2.0,dtype=np.float32)
        y=np.arange(0,self.boxsize,2.0,dtype=np.float32)
        z=np.arange(0,self.boxsize,2.0,dtype=np.float32)
        q=np.vstack(np.meshgrid(x,y,z,indexing='ij')).reshape(3,-1).T #array of 3d numbers
        return q

    def createPores(self):
        x=np.random.uniform(0,self.boxsize,self.npores)
        y=np.random.uniform(0,self.boxsize,self.npores)
        z=np.random.uniform(self.lowerc+5,self.upperc,self.npores)
        pores=np.vstack([x,y,z]).T
        return pores

    def createGridPores(self):
        xy=np.arange(5,self.boxsize-5,20)
        gridpores=[]
        for x in xy:
            for y in xy:
                gridpores.append([x,y,self.lowerc])
        return np.asarray(gridpores)
                
    
    def createThroats(self):
        throats=[]
        for idx, pore in enumerate(self.pores):
            distances=[self.distance(pore,x) for x in self.pores]
            neighbors=np.argsort(distances)
            throats.append([idx,neighbors[1]])
            throats.append([idx,neighbors[2]])
        for idx, pore in enumerate(self.gridpores):
            distances=[self.distance(pore,x) for x in self.pores]
            neighbors=np.argsort(distances)
            throats.append([idx+self.npores,neighbors[0]])
        self.pores=np.vstack([self.pores,self.gridpores])
        return throats

    def inthroat(self,node1,node2,x):
        throatlength=self.distance(node1,node2)
        distanceFromLine=math.sqrt((self.norm(x-node1)*self.norm(node1-node2)-np.dot(node1-x,node2-node1)**2)/(self.norm(node2-node1)))
        midpoint=0.5*(node1+node2)
        distanceFromMidpoint=self.distance(x,midpoint)
        parallelDistance=math.sqrt(distanceFromMidpoint**2-distanceFromLine**2)
        ps1=self.poresize(node1)
        ps2=self.poresize(node2)
        d1=self.distance(x,node1)
        d2=self.distance(x,node2)
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
        
    def inpores(self,x):
        for pore in self.pores:
            if self.distance(x,pore) < self.poresize(pore):
                return True
        return False
    
    def inthroats(self,x):
        for throat in self.throats:
            if self.inthroat(self.pores[throat[0]],self.pores[throat[1]],x):
                return True
        return False

    def sdf(self,x):
        if (x[2]>self.upperc or x[2]<self.lowerc):
            return -0.5
        elif self.inpores(x):
            return -0.5
        elif self.inthroats(x):
            return -0.5
        else:
            return 0.5

    def QQ(self):    
        self.qq=[self.sdf(x) for x in self.q] #sdf values
        return None

    def output(self):
        qnp=np.asarray(self.qq,dtype=np.float32)
        qnp.tofile("q.dat")
        with open("temp","w") as f:
            f.write("%d %d %d\n"%(self.boxsize,self.boxsize,self.boxsize))
            f.write("%d %d %d\n"%(self.boxsize/2,self.boxsize/2,self.boxsize/2))
        os.system("cat temp q.dat >qq.dat")


pn=PoreNetwork(npores=33,boxsize=80,lowerc=30,upperc=60)
pn.QQ()
pn.output()
'''x=np.arange(0,90,2.0,dtype=np.float32)
y=np.arange(0,90,2.0,dtype=np.float32)
z=np.arange(0,90,2.0,dtype=np.float32)
q=np.vstack(np.meshgrid(x,y,z,indexing='ij')).reshape(3,-1).T #array of 3d numbers

print('qstack generated')
x=np.random.uniform(0,90,npores)
y=np.random.uniform(0,90,npores)
z=np.random.uniform(20,70,npores)
pores=np.vstack([x,y,z]).T
throats=[]

def poresize(pore):
    psize=2+5*(pore[2]-20)/50
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

print('throats made')



def sdf(x):
    value=0.5
    if(x[2]>70 or x[2]<20):
        return -0.5
    else:
        for pore in pores:
            if distance(x,pore) < poresize(pore):
                return = -0.5
        for throat in throats:
            if inthroat(pores[throat[0]],pores[throat[1]],x):
                return=-0.5
    if x[2]>70 or x[2]<20:
        value=-0.5
    return value

#apply a function to each point in array, to create the sdf 
qq=[sdf(x) for x in q] #sdf values

#write to file
qnp=np.asarray(qq,dtype=np.float32)
qnp.tofile("q.dat")

#prepend the head to the file
with open("temp","w") as f:
    f.write("90 90 90\n")
    f.write("45 45 45\n")
os.system("cat temp q.dat >qq.dat")'''

