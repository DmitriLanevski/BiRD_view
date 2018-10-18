# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\lanevsd1\PycharmProjects\BiRD_view\test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import sys

sys.path.append('../GUI/')
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import SymLogNorm
from matplotlib.ticker import LogFormatter

import numpy as np

class FileWalker(QtWidgets.QTreeView):
    """PyQt custom widget.
    It extends QtGui.QTreeView and specifies the actions of selecting a certain path/folder.
    Selection sets fileName and filePath variables that can be later obtained using getters
    or by calling private variable.
    Contains file path and file name getters.
    """
    def __init__(self):
        super(FileWalker, self).__init__()
        self.model = QtWidgets.QFileSystemModel() #gets the system paths model to build a file tree
        self.model.setRootPath(QtCore.QDir.currentPath()) #sets the root path for tree view widget
        self.setModel(self.model) #buils a file tree here
        self.clicked.connect(self.onFolderFileClicked) #common way to connect action with a specific function
        self.fileName = ''
        self.filePath = ''

    def onFolderFileClicked(self, index):
        """Function that specifies the action when a folder is selected.
        Automatically takes as argument the index of element selected by user in file tree
        and sets the class variables fileName and filePath. These can later be used to get
        the file path and name of the selected folder.

        Args:
            index (int) index of element in file tree model
        """

        indexItem = self.model.index(index.row(), 0, index.parent())
        self.fileName = self.model.fileName(indexItem)
        self.filePath = self.model.filePath(indexItem)

    def getFileName(self):
        """Returns fileName variable (str)"""
        return self.fileName

    def getFilePath(self):
        """Returns file path variable (str)"""
        return self.filePath

class mainPlotWidget(object):
        def __init__(self, tab):
            self.tab = tab
            self.figure = plt.figure()
            self.subplot = self.figure.add_subplot(111)

            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self.tab)

class singleTab(QtWidgets.QWidget):
    def __init__(self, tabs):
        super(singleTab, self).__init__()
        self.tabs = tabs

        self.layout = QtWidgets.QHBoxLayout(self)

        self.mainPlot = mainPlotWidget(self)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.mainPlot.toolbar)
        self.splitter.addWidget(self.mainPlot.canvas)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

class customTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(customTabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        self.dataAnalyzer = None

    def closeTab(self, currentIndex):
        self.currentQWidget = self.widget(currentIndex)
        self.currentQWidget.deleteLater()
        self.removeTab(currentIndex)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.tabs = customTabWidget()

        self.fileWalker = FileWalker()

        self.splitterv = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitterv.addWidget(self.fileWalker)

        self.splitterh = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitterh.addWidget(self.splitterv)
        self.tabs.addTab(singleTab(self.tabs), 'Test')
        self.splitterh.addWidget(self.tabs)

        self.setCentralWidget(self.splitterh)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))

        self.setWindowTitle('Tropomi Data viewer')
        self.show()

class DataContainer(object):

    def __init__(self, fileName, filePath):
        self.fileName = fileName
        self.filePath = filePath
        self.readData()

    def readData(self):
        self.pol = []
        self.IZA = []
        self.VZA = []
        self.data = []
        self.wavelengths = []

        # pathToFile = Path("C:/Users/lanevsd1/Dmitri/Work files/Reflectance measurements/300818_1500_14_0i.csv")
        f = open(self.filePath, 'r')

        lines = []
        for line in f:
            lines.append(line.strip())

        Headers_string = lines[0]
        Headers = Headers_string.split(',,')
        Headers = Headers[3:(len(Headers) - 1)]

        for header in Headers:
            self.pol.append(header[0])
            hParts = header.split('/')
            self.IZA.append(float(hParts[0][1:]))
            self.VZA.append(float(hParts[1]))

        for i in range(2, len(lines)):
            line = lines[i].split(',')
            line = line[0:len(line) - 1]
            dataRow = []
            for j in range(0, len(line)):
                if j % 2 != 0:
                    dataRow.append(float(line[j]))
            self.data.append(dataRow)
            self.wavelengths.append(line[0])

    # def getData(self):



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())



