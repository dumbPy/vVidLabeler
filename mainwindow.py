# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from utils.QCustomWidget import QVidLabeler, QFirstPage
from utils.VideoHandler import iVideoDataset
import matplotlib.pyplot as plt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 299)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
	    # #Adding Custom Widget Here
        # self.widget1 = QVidLabeler(self.centralWidget)
        # self.widget1.setObjectName("widget1")
        # self.gridLayout.addWidget(self.widget1, 0, 0, 1, 1)

        # """Below 2 lines adds extra widget to handle 2 videos at a time.
        # Cool Feature if labeling only video level classes.
        # You can watch say 4 videos at a time and label them with corrosponding label buttons"""
        # # self.widget2 = QVidLabeler(self.centralWidget)
        # # self.gridLayout.addWidget(self.widget2, 0, 1, 1, 1)

        self.widget1 = QFirstPage(self.centralWidget, self.changeToVideoLabeler)
        self.widget1.setObjectName("widget1")
        self.gridLayout.addWidget(self.widget1, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 400, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuVideo_Labeling_Tool_by_Sufiyan = QtWidgets.QMenu(self.menuBar)
        self.menuVideo_Labeling_Tool_by_Sufiyan.setObjectName("menuVideo_Labeling_Tool_by_Sufiyan")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.menuBar.addAction(self.menuVideo_Labeling_Tool_by_Sufiyan.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuVideo_Labeling_Tool_by_Sufiyan.setTitle(_translate("MainWindow", "Video Labeling Tool by Sufiyan"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

    def changeToVideoLabeler(self, videoFolderPath, labelFolderPath):#Removes QFirstPage and Adds QVidLabeler
        self.attachVideoHandler(videoFolderPath, labelFolderPath)    #Attach VideoDataset before adding iVidLabeler as it asks for video upfront
        self.gridLayout.removeWidget(self.widget1)
        self.widget1.setParent(None)
        self.widget1 = QVidLabeler(self.centralWidget, self.pushVideoToDisplay)
        self.widget1.setObjectName("widget1")
        self.gridLayout.addWidget(self.widget1, 0, 0, 1, 1)
        

    def attachVideoHandler(self, videoFolderPath, labelFolderPath):
        self.vids= iVideoDataset(videoFolderPath, labelFolderPath)

    def pushVideoToDisplay(self):
        return self.vids.getNext()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

