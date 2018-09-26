#! /usr/bin/env python

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from utils.QCustomWidgets import QVidLabeler, QFirstPage
from utils.VideoHandler import iVideoDataset

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
        """Adding Custom Widget Here. Can Add multiple widgets to display 
        and classify multiple Videos at a time"""

        self.widget1 = QFirstPage(self.centralWidget, self.changeToVideoLabeler)
        self.widget1.setObjectName("widget1")
        self.gridLayout.addWidget(self.widget1, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 400, 22))
        self.menuBar.setObjectName("menuBar")


        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        # self.toolBar = QtWidgets.QToolBar(MainWindow)
        # self.toolBar.setObjectName("toolBar")
        # MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "vVidLabeler"))
        # self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

    def changeToVideoLabeler(self, videoFolderPath, labelFolderPath):#Removes QFirstPage and Adds QVidLabeler
        self.attachVideoHandler(videoFolderPath, labelFolderPath)    #Attach VideoDataset before adding iVidLabeler as it asks for video upfront
        self.gridLayout.removeWidget(self.widget1)
        self.widget1.setParent(None)
        self.widget1 = QVidLabeler(self.centralWidget, self.vids.getNextVideo, self.vids.getPreviousVideo, mainWindow=self, labelFolderPath=self.labelFolderPath)
        self.widget1.setObjectName("widget1")
        self.gridLayout.addWidget(self.widget1, 0, 0, 1, 1)
        for className in self.vids.allVideoClasses:
            self.widget1.addNewClass(className)

    def attachVideoHandler(self, videoFolderPath, labelFolderPath):
        self.labelFolderPath=labelFolderPath
        self.vids= iVideoDataset(videoFolderPath, labelFolderPath)




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

