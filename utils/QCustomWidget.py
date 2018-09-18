from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig=Figure(figsize=(width,height), dpi=dpi, )
        fig.tight_layout()
        fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
        self.axis=fig.add_subplot(111)
        self.axis.imshow(Image.open("no_image.png"))
        FigureCanvas.__init__(self,fig)
        self.setParent(parent)
        self.axis.axis('off')
        self.axis.get_xaxis().set_visible(False)
        self.axis.get_yaxis().set_visible(False)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class QVidLabeler(QtWidgets.QWidget):
  def __init__(self, parent):
    QtWidgets.QWidget.__init__(self, parent)
    self.horizontalLayout = QtWidgets.QHBoxLayout(self)
    self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
    self.horizontalLayout.setSpacing(6)
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.splitter = QtWidgets.QSplitter(self)
    self.splitter.setOrientation(QtCore.Qt.Horizontal)
    self.splitter.setObjectName("splitter")
    self.display_widget = MplCanvas(self.splitter)
    self.display_widget.setObjectName("display_widget")
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
    self.horizontalLayout.addWidget(self.splitter)

    _translate = QtCore.QCoreApplication.translate
    self.clear_class.setText(_translate("MainWindow", "clear_class"))
    self.left_class.setText(_translate("MainWindow", "left_class"))
    self.right_class.setText(_translate("MainWindow", "right_class"))
    self.new_class.setPlaceholderText(_translate("MainWindow", "New Class"))
    self.replay.setText(_translate("MainWindow", "replay"))

  def attach(self):
    pass