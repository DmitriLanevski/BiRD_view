# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\lanevsd1\PycharmProjects\BiRD_view\test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import sys

sys.path.append('../GUI/')

from PyQt5 import QtCore, QtGui, QtWidgets

#from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import SymLogNorm
from matplotlib.ticker import LogFormatter

#import numpy as np

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


class singleTab(QtWidgets.QWidget):
    def __init__(self, tabs):
        super(singleTab, self).__init__()
        self.tabs = tabs

        self.layout = QtWidgets.QHBoxLayout(self)

        self.mainPlot = mainPlotWidget(self)
        # self.SpatialSpectralSelectror = spatialOrSpectralSelectror(self.mainPlot)
        # self.AverageMaximumSelector = maximumOrAverageSelector(self.mainPlot)
        # self.imagingModeSelector = imagingModeSelector(self.mainPlot)
        # self.dataSelector = dataSelectorFromList()

        self.splitterh1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitterh1.addWidget(self.mainPlot.toolbar)
        # self.splitterh1.addWidget(self.dataSelector)

        self.splitterh2 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        # self.splitterh2.addWidget(self.SpatialSpectralSelectror)
        # self.splitterh2.addWidget(self.AverageMaximumSelector)
        # self.splitterh2.addWidget(self.imagingModeSelector)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.splitterh1)
        self.splitter.addWidget(self.mainPlot.canvas)
        self.splitter.addWidget(self.splitterh2)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)


class mainPlotWidget(object):
    def __init__(self, tab):
        self.tab = tab

        self.figure = plt.figure()
        self.subplot = self.figure.add_subplot(111)

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self.tab)

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
        #self.tabs.addTab(singleTab(self.tabs), 'Test')
        self.splitterh.addWidget(self.tabs)

        self.setCentralWidget(self.splitterh)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))

        self.setWindowTitle('Tropomi Data viewer')
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())



