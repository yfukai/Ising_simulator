#!/usr/bin/env python3
# coding: utf-8

#### simulation code ####

import numpy as np
from numba import jit,njit

LATTICE_SIZE=32
DISPLAY_UPDATE_RATIO=0.1
#@njit(inline="always")
@njit
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

#### GUI code ####

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg

T_MAX=5.
T_MIN=0.
T_STEP=0.25
TEMP_INDICATOR_WIDTH=32
TEMP_INDICATOR_PADDING=10
TEMP_INDICATOR_CIRCLE_RADIUS=24
COLOR_0=(1,1,0)
COLOR_1=(0,0.3,0.3)

#ignore key press event for ImageView
class ImageViewCustom(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Preferred,
                           QSizePolicy.Expanding)
    def keyPressEvent(self, event):
        QWidget.keyPressEvent(self, event)
    def resizeEvent(self, event):
        #XXX dirty hack
        height=self.size().height()
        self.setFixedWidth(height)
#     def hasWidthForHeight(self):
#        return True
#    def widthForHeight(self,height):
#        return height

class _TempIndicator(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Minimum,
                           QSizePolicy.Expanding)
    def paintEvent(self, event):
#        print("paint",self.value)
        painter = QPainter(self)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
#        brush.setColor(QColor('black'))
#        rect = QRect(0, 0, painter.device().width(), painter.device().height())
#        painter.fillRect(rect, brush)
        d_width = painter.device().width()
        d_height = painter.device().height()
        brush.setColor(QColor('red'))
        rect_height=(d_height-TEMP_INDICATOR_PADDING-TEMP_INDICATOR_CIRCLE_RADIUS)*self.value
        self.rect = QRect((d_width-TEMP_INDICATOR_WIDTH)//2,
                          d_height-rect_height-TEMP_INDICATOR_CIRCLE_RADIUS,
                          TEMP_INDICATOR_WIDTH,
                          rect_height)
        painter.fillRect(self.rect, brush)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
                QPoint(d_width/2,d_height-TEMP_INDICATOR_CIRCLE_RADIUS), 
                TEMP_INDICATOR_CIRCLE_RADIUS, TEMP_INDICATOR_CIRCLE_RADIUS)
        painter.end()

    def setValue(self,value):
#        print("set",value)
        if value > 1.: value=1.
        if value < 0.: value=0.
        self.value=value
        self.update()

class _InstructionImage(QLabel):
    def __init__(self,image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.Expanding)
        self.pix=QPixmap(image)
    def resizeEvent(self, event):
        #XXX dirty hack
        height=self.size().height()
        pix2=self.pix.scaledToHeight(height,Qt.SmoothTransformation)
        self.setFixedWidth(pix2.width())
        self.setPixmap(pix2)
        self.show()
    
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.spins=np.random.randint(0,2,(LATTICE_SIZE,LATTICE_SIZE))*2-1
        self.T=5.
        titleBarHeight = self.style().pixelMetric(
            QStyle.PM_TitleBarHeight,QStyleOptionTitleBar(),self)
        geometry = app.desktop().availableGeometry()
        geometry.setHeight(geometry.height() - (titleBarHeight*2))

        self.setGeometry(geometry)
        self.initUI()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            if self.T < T_MAX: self.T+=T_STEP
        if key == Qt.Key_Down:
            if self.T > T_MIN: self.T-=T_STEP
#        if key == Qt.Key_Right:
#            LATTICE_SIZE=LATTICE_SIZE*2
#            self.spins=np.random.randint(0,2,(LATTICE_SIZE,LATTICE_SIZE))*2-1
        self.ind.setValue((self.T-T_MIN)/(T_MAX-T_MIN))
        self.statusBar().showMessage('Temperature: %.2f'%self.T)

    def initUI(self):               
        w = QWidget()
        hb = QHBoxLayout()
        self.setCentralWidget(w)

        #instruction image
        pic=_InstructionImage("instruction.png")
        hb.addWidget(pic)

        #imageview for Ising 
        self.imv=ImageViewCustom()
        #https://stackoverflow.com/questions/38065570/pyqtgraph-is-it-possible-to-have-a-imageview-without-histogram
        self.imv.ui.histogram.hide()
        self.imv.ui.roiBtn.hide()
        self.imv.ui.menuBtn.hide()
        self.imv.setFocusPolicy(Qt.NoFocus)
        self.imv.setColorMap(pg.ColorMap((0,1),(COLOR_0,COLOR_1)))
        hb.addWidget(self.imv)

        vb_temp = QVBoxLayout()
        label_high=QLabel()
        label_high.setPixmap(QPixmap("hot.png").scaledToHeight(32,Qt.SmoothTransformation))
        vb_temp.addWidget(label_high)
        label_high.show()
        self.ind=_TempIndicator()
        self.ind.setValue((self.T-T_MIN)/(T_MAX-T_MIN))
        vb_temp.addWidget(self.ind)
        label_low=QLabel()
        label_low.setPixmap(QPixmap("cold.png").scaledToHeight(32,Qt.SmoothTransformation))
        vb_temp.addWidget(label_low)
        label_low.show()
        hb.addLayout(vb_temp)
        hb.addStretch()
        w.setLayout(hb)

        #instruction image
        pic=_InstructionImage("instruction2.png")
        hb.addWidget(pic)

        self.statusBar().showMessage('Temperature: %.2f'%self.T)
        self.setWindowTitle('Ising simulation')    

        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(10) 
        
        self.showImage()
        self.show()

    def showImage(self):
        self.imv.setImage(self.spins.astype(np.float),levels=(0.,1.),autoHistogramRange=False)

    def update(self):
#        self.spins=np.random.randint(0,2,(LATTICE_SIZE,LATTICE_SIZE))*2-1
        updateIsing(self.spins,self.T)
        self.showImage()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


#class MainWindow(QMainWindow):
#    def __init__(self, *args, **kwargs):
##        w = QWidget()
##        vb = QVBoxLayout()
##        self.grid = QGridLayout()
##        self.grid.setSpacing(5)
##        vb.addLayout(self.grid)
##        w.setLayout(vb)
##        self.setCentralWidget(w)

#def main():
#    app = QApplication(sys.argv)
#    window = MainWindow()
#    sys.exit(app.exec_())
#
#if __name__ == '__main__':
#    main()
