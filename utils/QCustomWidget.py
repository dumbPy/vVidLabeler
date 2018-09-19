from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
from PyQt5.QtCore import Qt
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageQt

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig=Figure(figsize=(width,height), dpi=dpi, )
        fig.tight_layout()
        fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
        self.axis=fig.add_subplot(111)
        self.imshow(Image.open("no_image.png"))
        FigureCanvas.__init__(self,fig)
        self.setParent(parent)
        self.axis.axis('off')
        self.axis.get_xaxis().set_visible(False)
        self.axis.get_yaxis().set_visible(False)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def imshow(self, image): self.axis.imshow(image) #Standardize calling canvasObject.imshow() for MplCanvas and Qcanvas

def toQImage(frame): return QtGui.QImage(frame, frame.shape[0], frame.shape[1], QtGui.QImage.Format_RGB32) #Helper Function

class QCanvas(QtWidgets.QLabel):
    def __init__(self, parent, w=5, h=4):
        QtWidgets.QLabel.__init__(self, parent)
        # self.setScaledContents(False)
        Image.open("no_image.png")

    def draw(self): self.show() #Standardizing with MplCanvas

    def imshow(self, image):
        self.setPixmap(QtGui.QPixmap.fromImage(toQImage(image)))



class QVidLabeler(QtWidgets.QWidget):
    def __init__(self, parent, askForNextVideo, matplotlibBackend=False):
        QtWidgets.QWidget.__init__(self, parent)
        self.matplotlibBackend=matplotlibBackend
        self.setupUi()
        self.attachKeys()
        self.askForNextVideo=askForNextVideo #askForNextVideo is a calllback function
        self.vid=self.askForNextVideo()  #Call for first video once everything is setup
        self.showNextFrame()

    def setupUi(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        #Choose Between 2 Backends. Matplotlib is slow
        if self.matplotlibBackend: self.canvas = MplCanvas(self.splitter)
        else: self.canvas=QCanvas(self.splitter)
        self.canvas.setObjectName("canvas")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.clear_class = QtWidgets.QPushButton(self.widget)
        self.clear_class.setObjectName("clear_class")
        self.verticalLayout.addWidget(self.clear_class)
        self.left_class = QtWidgets.QPushButton(self.widget)
        self.left_class.setObjectName("left_class")
        self.verticalLayout.addWidget(self.left_class)
        self.right_class = QtWidgets.QPushButton(self.widget)
        self.right_class.setObjectName("right_class")
        self.verticalLayout.addWidget(self.right_class)
        self.new_class = QtWidgets.QLineEdit(self.widget)
        self.new_class.setText("")
        self.new_class.setAlignment(QtCore.Qt.AlignCenter)
        self.new_class.setClearButtonEnabled(False)
        self.new_class.setObjectName("new_class")
        self.verticalLayout.addWidget(self.new_class)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.replay = QtWidgets.QPushButton(self.widget)
        self.replay.setObjectName("replay")
        self.verticalLayout.addWidget(self.replay)
        self.button_next = QtWidgets.QPushButton(self.widget)
        self.button_next.setObjectName("button_next")
        self.verticalLayout.addWidget(self.button_next)
        self.horizontalLayout.addWidget(self.splitter)
        self.retranslateUi()
        

    def saveAndNextVideo(self):
        self.vid.writeLabels()
        self.vid=self.askForNextVideo() #Get next Video
        self.showNextFrame()            #Get the first frame and show it

    def attachKeys(self):
        self.button_next.clicked.connect(self.saveAndNextVideo)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.clear_class.setText(_translate("MainWindow", "clear_class"))
        self.left_class.setText(_translate("MainWindow", "left_class"))
        self.right_class.setText(_translate("MainWindow", "right_class"))
        self.new_class.setPlaceholderText(_translate("MainWindow", "New Class"))
        self.replay.setText(_translate("MainWindow", "replay"))
        self.button_next.setText(_translate("MainWindow", "Next Video"))
        self.setFocusPolicy(Qt.StrongFocus)                     #Set Strong Focus to register key press in this class

    def attachVid(self, iVideoObject):
        self.vid=iVideoObject
    
    def keyPressEvent(self, e):
        if self.vid==None: print("No Video Attached Yet!!")
        else:
            pressed=chr(Qt.Key(e.key()))  #Get the corrosponding character of the pressed key
            self.vid.setFrameLabel(pressed)                     #Set Frame Label
            self.showNextFrame()

    def showNextFrame(self):    
        self.canvas.imshow(self.vid.nextFrame()) #Show the next frame
        self.canvas.draw()                       #Render next frame
        self.show()
        self.setFocus()


class QFirstPage(QtWidgets.QWidget):
    def __init__(self, parent, callback):
        QtWidgets.QWidget.__init__(self, parent)
        self.callback=callback
        self.gridLayout_2 = QtWidgets.QGridLayout(self)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.button_videoFolder = QtWidgets.QPushButton(self)
        self.button_videoFolder.setObjectName("button_videoFolder")
        self.gridLayout_2.addWidget(self.button_videoFolder, 0, 0, 1, 1)
        self.button_labelFolder = QtWidgets.QPushButton(self)
        self.button_labelFolder.setObjectName("button_labelFolder")
        self.gridLayout_2.addWidget(self.button_labelFolder, 0, 1, 1, 1)
        self.button_OK = QtWidgets.QPushButton(self)
        self.button_OK.setObjectName("button_OK")
        self.gridLayout_2.addWidget(self.button_OK, 1, 1, 1, 1)
        _translate = QtCore.QCoreApplication.translate
        self.button_videoFolder.setText(_translate("MainWindow", "Video Folder Path"))
        self.button_labelFolder.setText(_translate("MainWindow", "Label Folder Path"))
        self.button_OK.setText(_translate("MainWindow", "OK"))
        
        #HardCoding Paths here for testing!!!
        self.videoFolderPath="/home/sufiyan/temp_data/Videos"
        self.labelFolderPath="/home/sufiyan/temp_data/Labels"
        self.attachKeys()

    def getVideoFolderPath(self): return self.getFolderPath()
    def getLabelFolderPath(self): return self.getFolderPath(forLabel=True)
    def getFolderPath(self, forLabel=False):
        if forLabel: self.labelFolderPath=QtWidgets.QFileDialog.getExistingDirectory( self, 
            "Select Label Directory", os.path.expanduser("~"), QtWidgets.QFileDialog.ShowDirsOnly)
        else: self.videoFolderPath=QtWidgets.QFileDialog.getExistingDirectory( self, 
            "Select Label Directory", os.path.expanduser("~"), QtWidgets.QFileDialog.ShowDirsOnly)

    def OK(self):
        self.callback(self.videoFolderPath, self.labelFolderPath) #Call the Callback function once the work of this page is done

    def attachKeys(self):
        self.button_videoFolder.clicked.connect(self.getVideoFolderPath)
        self.button_labelFolder.clicked.connect(self.getLabelFolderPath)
        self.button_OK.clicked.connect(self.OK)