#!/usr/bin/env python3
# coding: utf-8

#### simulation code ####

import numpy as np
from numba import jit,njit

LATTICE_SIZE=128
DISPLAY_UPDATE_RATIO=0.1

@njit(inline="always")
def periodic_round(i): 
    return (i+LATTICE_SIZE)%LATTICE_SIZE
@njit
def updateIsing(spins,T):
    for i in range(int(LATTICE_SIZE**2*DISPLAY_UPDATE_RATIO)):
        #flipping position 
        x=np.random.randint(0,LATTICE_SIZE)
        y=np.random.randint(0,LATTICE_SIZE)

        #heat bath method
        p=spins[x,y]
        p2sum=0
        for (x2,y2) in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            p2sum+=spins[periodic_round(x2),periodic_round(y2)]
        dE=2*p*p2sum #energy after flipping - before flipping
        if T>0:
            if(np.random.rand() < 1./(1.+np.exp(dE/T))):
                spins[x,y]*=-1 
        else:
            if (dE<0) or (dE==0 and np.random.rand() < 0.5):
                spins[x,y]*=-1

...
  
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        #initialize values
        self.spins=np.random.randint(0,2,(LATTICE_SIZE,LATTICE_SIZE))*2-1
        self.T=5.
        ...

    ...

    def update(self): # called every 10 ms
        updateIsing(self.spins,self.T)
        self.showImage()
