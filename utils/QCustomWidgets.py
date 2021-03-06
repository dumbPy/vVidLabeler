from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
from PyQt5.QtCore import Qt
import os
from PIL import Image, ImageQt
import numpy as np
import json

class QCanvas(QtWidgets.QLabel):
    def __init__(self, parent):
        QtWidgets.QLabel.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

    def imshow(self, image):
        if isinstance(image, np.ndarray):
            Qimage=ImageQt.ImageQt(Image.fromarray(image))
            self.setPixmap(QtGui.QPixmap.fromImage(Qimage))
        
class QTags(QtWidgets.QListWidget):
    def __init__(self, parent, labelFolderPath=None):
        QtWidgets.QListWidget.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        if labelFolderPath:
            tags_ref_path=os.path.join(labelFolderPath, 'config', 'tags_ref.json')
            if os.path.exists(tags_ref_path):
                with open(tags_ref_path) as f:
                    self.tags_ref=json.load(f)
            else: print(f"No Tags Reference File in {os.path.join(labelFolderPath, 'config')}"); self.tags_ref={}
        else: self.tags_ref={} #Empth Dictionary for tags if no labelFolderPath is provided
    
    def set(self, tags_list):
        if isinstance(tags_list, list):
            self.clear() #Clear all the tags
            tags_list.sort()
            for tag in tags_list:
                if tag in self.tags_ref.keys(): self.addItem(f'{tag}: {self.tags_ref[tag]}')
                else:                           self.addItem(tag)

            


class QVidLabeler(QtWidgets.QWidget):
    def __init__(self, parent, askForNextVideo, askForPreviousVideo=None, mainWindow=None, labelFolderPath=None, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        self.mainWindow=mainWindow                  #Pass Mainwindow to print stuff to status bar and set menu bars
        self.pressed=[]                             #Track the pressed keys at any instance
        self.args=args
        self.kwargs=kwargs
        self.labelFolderPath=labelFolderPath
        self.setupUi()
        self.attachKeys()
        self.setMenu()
        self.askForNextVideo=askForNextVideo         #askForNextVideo is a calllback function
        self.askForPreviousVideo=askForPreviousVideo #askForPreviousVideo is a callback function
        self.vid=self.askForNextVideo(next=False)    #Call for first video once everything is setup
        self.showNextFrame()

    def setupUi(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.tags = QTags(self.splitter, self.labelFolderPath)
        self.tags.setObjectName("listWidget")
        
        self.canvas=QCanvas(self.splitter)
        self.canvas.setObjectName("canvas")
        
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.new_class = QtWidgets.QLineEdit(self.widget)
        self.new_class.setText("")
        self.new_class.setAlignment(QtCore.Qt.AlignCenter)
        self.new_class.setClearButtonEnabled(False)
        self.new_class.setObjectName("new_class")
        self.verticalLayout.addWidget(self.new_class)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.button_previousVideo = QtWidgets.QPushButton(self.widget)
        self.button_previousVideo.setObjectName("button_previousVideo")
        self.verticalLayout.addWidget(self.button_previousVideo)
        self.button_next = QtWidgets.QPushButton(self.widget)
        self.button_next.setObjectName("button_next")
        self.verticalLayout.addWidget(self.button_next)
        self.horizontalLayout.addWidget(self.splitter)
        self.retranslateUi()
        

    def saveAndGetVideo(self, which="next"):
        self.vid.writeMeta()                #Write metadata like frameLabels, videoClass, key Mappings, to json file
        if which=="previous" and self.askForPreviousVideo!=None: vid=self.askForPreviousVideo()
        else: vid=self.askForNextVideo()    #Get next Video
        if (vid.vid[0]!=self.vid.vid[0]).any():self.vid=vid #Avoid Nonetype returned at the end of videoDataset 
        else: self.printStatus("No More Videos to Load...")
        self.showNextFrame()                #Get the first frame and show it
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.new_class.setPlaceholderText(_translate("MainWindow", "New Class"))
        self.button_previousVideo.setText(_translate("MainWindow", "Last Video"))
        self.button_next.setText(_translate("MainWindow", "Next Video"))
        self.setFocusPolicy(Qt.StrongFocus)                     #Set Strong Focus to register key press in this class

    def attachVid(self, iVideoObject):
        self.vid=iVideoObject
    
    def parseKey(self, event):
        """Handles the Key Press Event.
        English Alphanumeric characters have ASCII value upto 127
                as shown here--> http://ee.hawaii.edu/~tep/EE160/Book/chap4/subsection2.1.1.1.html
        Left Arrow = 16777234
        Up Arrow   = 16777235
        Right Arrow= 16777236
        Down Arrow = 16777237
        BackSpace  = 16777219
        """
        key=event.key()  #Get the corrosponding character of the pressed key
            # print(key)               #Used to print the ASCII code of pressed key
        if key==16777219:   key="backSpace"
        elif key<127:       
            if key==32:     key='space'#segrigate space key as navigation keys for frame labels
            else:           key=key #return numbers for image discription flags and strings frame labels(arrow keys) and backSpace
        elif key==16777234: key="Left"
        elif key==16777235: key="Up"
        elif key==16777236: key="Right"
        elif key==16777237: key="Down"
        else: key=None               #Don't Register any other keys by skipping next statements
        return key
        
    def updateTags(self): self.tags.set(self.pressed)

    def keyPressEvent(self, event):
        key=self.parseKey(event)
        # print(type(key))
        if type(key)==int: #If its an alpha numeric key, toggle it in self.pressed, and use self.pressed as tags for each frame labeled with arrow keys
            key=chr(key)
            if key in self.pressed: self.pressed.remove(key)
            else: self.pressed.append(key)
            self.updateTags()
        elif type(key)==str: #string keys are navigation keys or space parsed as strings above and shall be used as frame labels 
            if key=='backSpace': self.showPreviousFrame(); return None
            elif self.registerKeys :self.vid.setFrameLabel([key, self.pressed.copy()]) #Set Frame Label
            # print(key, self.pressed)
            self.showNextFrame()

    def showPreviousFrame(self):
        self.canvas.imshow(self.vid.previousFrame())
        self.show()
        self.setFocus()

    def showNextFrame(self):   
        self.canvas.imshow(self.vid.nextFrame())    #Show the next frame
        self.show()
        self.setFocus()
        self.updateTags()

    def addNewClass(self, className=None):
        if className==None:
            className=self.new_class.text()
            self.new_class.setText("")
        try: button=getattr(self, className)        #Check if self.<className> exists
        except:
            _translate = QtCore.QCoreApplication.translate
            setattr(self, className, QtWidgets.QPushButton(self.widget))
            button=getattr(self, className)
            button.setObjectName(className)
            lastIndex=self.verticalLayout.indexOf(self.button_next)
            self.verticalLayout.insertWidget(lastIndex-3, button)  #Added above QLineEdit
            button.setText(_translate("MainWindow", className))
            button.clicked.connect(lambda: [self.vid.setClassLabel(className), self.printStatus(f"videoLabel: {className}")])
            self.vid.setClassLabel(className)
            self.printStatus(f"videoLabel: {className}")
    
    def printStatus(self, message):
        if self.mainWindow:
            try: self.mainWindow.statusBar.showMessage(message, 2000)
            except: print("Problem Printing message to statusBar. Make sure it's called statusBar in mainWindow")
        else: print("No mainWindow passed to QVidLabeler")

    def attachKeys(self):
        self.button_next.clicked.connect(lambda: self.saveAndGetVideo("next"))
        self.button_previousVideo.clicked.connect(lambda: self.saveAndGetVideo("previous"))
        self.new_class.returnPressed.connect(self.addNewClass)

    def setMenu(self):
        if self.mainWindow:
            self.regKeysAction = QtWidgets.QAction('Register Key Strokes', self, checkable=True)
            self.regKeysAction.setStatusTip('If Unchecked, Key Strokes will not be Pushed to frameLabels')
            self.regKeysAction.setChecked(True)
            self.regKeysAction.triggered.connect(self.setKeyRegisterStatus)
            settings=self.mainWindow.menuBar.addMenu("Settings")
            settings.addAction(self.regKeysAction)
            self.registerKeys=True

    def setKeyRegisterStatus(self):
        self.registerKeys = self.regKeysAction.isChecked()

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
        self.videoFolderPath=None
        self.labelFolderPath=None
        self.attachKeys()

    def getVideoFolderPath(self): return self.getFolderPath()
    def getLabelFolderPath(self): return self.getFolderPath(forLabel=True)
    def getFolderPath(self, forLabel=False):
        if forLabel: self.labelFolderPath=QtWidgets.QFileDialog.getExistingDirectory( self, 
            "Select Label Directory", os.path.expanduser("~"), QtWidgets.QFileDialog.ShowDirsOnly)
        else: self.videoFolderPath=QtWidgets.QFileDialog.getExistingDirectory( self, 
            "Select Label Directory", os.path.expanduser("~"), QtWidgets.QFileDialog.ShowDirsOnly)
        print(self.labelFolderPath, self.videoFolderPath)
    def OK(self):
        self.callback(self.videoFolderPath, self.labelFolderPath) #Call the Callback function once the work of this page is done

    def attachKeys(self):
        self.button_videoFolder.clicked.connect(self.getVideoFolderPath)
        self.button_labelFolder.clicked.connect(self.getLabelFolderPath)
        self.button_OK.clicked.connect(self.OK)