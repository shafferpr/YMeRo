import numpy as np
import math
import sys
import os
import argparse



class PoreNetwork(object):
    def __init__(self,npores,boxsize,lowerc,upperc,poresizeceiling,poresizefloor,outputfile):
        self.npores=npores
        self.boxsize=boxsize
        self.lowerc=lowerc
        self.upperc=upperc
        self.poresizeceiling=poresizeceiling
        self.poresizefloor=poresizefloor
        self.q=self.createGrid()
        self.pores=self.createPores()
        self.gridpores=self.createGridPores()
        self.throats=self.createThroats()
        self.outputfile=outputfile

    def poresize(self,pore):
        psize=self.poresizefloor+(self.poresizeceiling-self.poresizefloor)*(pore[2]-float(self.lowerc))/float(self.upperc-self.lowerc)
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
        os.system("cat temp q.dat >%s"%self.outputfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create a membrane structure')
    parser.add_argument('--npores', type=int, dest='npores',default=20,help="number ofspherical pores in the membrane, in excess of the predefined grid pores on the bottom, default=20")
    parser.add_argument('--boxsize', type=int, dest='boxsize',default=80,help="total boxsize for cubic box, default=80")
    parser.add_argument('--lowerc', type=int, dest='lowerc',default=30,help="lower cutoff for the membrane structure in the box, default=30")
    parser.add_argument('--upperc', type=int, dest='upperc',default=60,help="upper cutoff for the membrane structure in the box, default=60")
    parser.add_argument('--poresizeceiling', type=float, dest='poresizeceiling',default=10,help="largest pore size, near the top of the membrane, default=10")
    parser.add_argument('--poresizefloor',type=float, dest='poresizefloor',default=3,help="smallest pore size, near at the bottom of the membrane, default=3")
    parser.add_argument('--outputfile',dest='outputfile',default='qq.dat',help="name of sdf outputfile, used as input to simulation, default=qq.dat")
    args = parser.parse_args()
    pn=PoreNetwork(npores=args.npores,boxsize=args.boxsize,lowerc=args.lowerc,upperc=args.upperc,poresizeceiling=args.poresizeceiling,poresizefloor=args.poresizefloor,outputfile=args.outputfile)
    pn.QQ()
    pn.output()
