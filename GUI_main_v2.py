# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\lanevsd1\PycharmProjects\BiRD_view\test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import sys
from math import *
from typing import Any

sys.path.append('../GUI/')
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox

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

class DataContainer(object):

    def __init__(self, fileName, filePath):
        self.fileName = fileName
        self.filePath = Path(filePath)
        self.readData()

    def readData(self):
        self.pols = []
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
            if header[0] == 'p':
                self.pols.append(1)
            elif header[0] == 's':
                self.pols.append(2)
            else:
                self.pols.append(0)
            hParts = header.split('/')
            self.IZA.append(float(hParts[0][1:]))
            self.VZA.append(float(hParts[1]))

        for i in range(2, len(lines)):
            line = lines[i].split(',')
            line = line[0:len(line) - 1]
            dataRow = []
            for j in range(6, len(line)):
                if j % 2 != 0:
                    dataRow.append(float(line[j]))
            self.data.append(dataRow)
            self.wavelengths.append(line[0])

        self.IZA = np.array(self.IZA)
        self.VZA = np.array(self.VZA)
        self.data = np.array(self.data)
        self.wavelengths = np.array(self.wavelengths)

class DataWizard(object):
    def __init__(self):
        self.dataDict = {}

        self.wavelengths = np.arange(400, 805, 5)
        self.vza = np.concatenate((np.arange(-80, 85, 5),np.arange(-80, 85, 5)))
        self.iza = np.zeros(len(self.vza))
        self.phi = np.zeros(len(self.vza))
        self.pols = np.array([1 for i in range(int(len(self.vza)/2))] + [2 for j in range(int(len(self.vza)/2))])
        self.data = np.empty((len(self.wavelengths),len(self.vza)))
        for i in range(len(self.wavelengths)):
            for j in range(len(self.vza)):
                self.data[i,j] = np.random.random()*cos(radians(self.vza[j]))

        self.pol = 1
        self.wavelength = 635
        self.siza = 0
        self.svza = 0
        self.sphi = 0

        self.maskVZA = (self.pols == self.pol) & (self.iza == self.siza) & (self.phi == self.sphi)
        self.maskWL = (self.pols == self.pol) & (self.iza == self.siza) & (self.phi == self.sphi) & (self.vza == self.svza)

        self.sdataVZA = self.data[(self.wavelengths == self.wavelength), self.maskVZA]
        self.sdataVZA = self.data[:, self.maskWL]

    def updateDataSelection(self):
        self.maskVZA = (self.pols == self.pol) & (self.iza == self.siza) & (self.phi == self.sphi)
        self.maskWL = (self.pols == self.pol) & (self.iza == self.siza) & (self.phi == self.sphi) & (self.vza == self.svza)

        self.sdataVZA = self.data[(self.wavelengths == self.wavelength), self.maskVZA]
        self.sdataVZA = self.data[:, self.maskWL]

    def updateData(self, fileName):
        dataContainer = self.dataDict[fileName]
        self.wavelengths = dataContainer.wavelengths
        self.vza = dataContainer.VZA
        self.iza = dataContainer.IZA
        self.phi = np.zeros(len(self.vza))
        self.pols = dataContainer.pols
        self.data = dataContainer.data

class openFileButton(QPushButton):
    def __init__(self, name, FileWalker, DataWizard, customTabWidget):
        super(openFileButton, self).__init__(name)
        self.clicked.connect(self.onButtonClicked)
        self.FileWalker = FileWalker
        self.DataWizard = DataWizard
        self.customTabWidget = customTabWidget

    def onButtonClicked(self):
        self.dataHolder = DataContainer(self.FileWalker.fileName, self.FileWalker.filePath)
        self.DataWizard.dataDict[self.dataHolder.fileName] = self.dataHolder
        self.DataWizard.updateData(self.dataHolder.fileName)

        self.singleTab = self.customTabWidget.currentWidget()
        self.singleTab.dataSelector.addAndConnectItems()
        self.singleTab.wavelengthSelector.addAndConnectItems()
        self.singleTab.izaSelector.addAndConnectItems()
        self.singleTab.vzaSelector.addAndConnectItems()
        self.singleTab.phiSelector.addAndConnectItems()
        self.singleTab.polSelector.addAndConnectItems()

class dataSelector(QComboBox):
    def __init__(self, DataWizard):
        super(QComboBox, self).__init__()
        self.DataWizard = DataWizard

    def addAndConnectItems(self):
        for name in self.DataWizard.dataDict:
            self.addItem(name)
        self.activated.connect(self.onActivated)
        self.update()

    def onActivated(self):
        self.DataWizard.updateData(self.currentText())

    def clearMenu(self):
        for index in range(self.count()):
            self.removeItem(index)
            self.clear()

class wavelengthSelector(QComboBox):
    def __init__(self, DataWizard):
        super(QComboBox, self).__init__()
        self.DataWizard = DataWizard

    def addAndConnectItems(self):
        self.clearMenu()
        for wavelength in self.DataWizard.wavelengths:
            self.addItem(wavelength)
        self.DataWizard.wavelength = self.DataWizard.wavelengths[0]
        self.activated.connect(self.onActivated)
        self.update()

    def onActivated(self):
        self.DataWizard.wavelength = self.currentData()
        self.DataWizard.updateDataSelection()

    def clearMenu(self):
        for index in range(self.count()):
            self.removeItem(index)
            self.clear()

class izaSelector(QComboBox):
    def __init__(self, DataWizard):
        super(QComboBox, self).__init__()
        self.DataWizard = DataWizard

    def addAndConnectItems(self):
        self.clearMenu()
        for iza in np.unique(self.DataWizard.iza):
            self.addItem(str(iza.item()))
        self.DataWizard.siza = np.unique(self.DataWizard.iza)[0]
        self.activated.connect(self.onActivated)
        self.update()

    def onActivated(self):
        self.DataWizard.siza = float(self.currentText())
        self.DataWizard.updateDataSelection()

    def clearMenu(self):
        for index in range(self.count()):
            self.removeItem(index)
            self.clear()

class vzaSelector(QComboBox):
    def __init__(self, DataWizard):
        super(QComboBox, self).__init__()
        self.DataWizard = DataWizard

    def addAndConnectItems(self):
        self.clearMenu()
        for vza in np.unique(self.DataWizard.vza):
            self.addItem(str(vza))
        self.DataWizard.svza = np.unique(self.DataWizard.vza)[0]
        self.activated.connect(self.onActivated)
        self.update()

    def onActivated(self):
        self.DataWizard.svza = float(self.currentText())
        self.DataWizard.updateDataSelection()

    def clearMenu(self):
        for index in range(self.count()):
            self.removeItem(index)
            self.clear()

class phiSelector(QComboBox):
    def __init__(self, DataWizard):
        super(QComboBox, self).__init__()
        self.DataWizard = DataWizard

    def addAndConnectItems(self):
        self.clearMenu()
        for phi in np.unique(self.DataWizard.phi):
            self.addItem(str(phi))
        self.DataWizard.sphi = np.unique(self.DataWizard.phi)[0]
        self.activated.connect(self.onActivated)
        self.update()

    def onActivated(self):
        self.DataWizard.sphi = float(self.currentText())
        self.DataWizard.updateDataSelection()

    def clearMenu(self):
        for index in range(self.count()):
            self.removeItem(index)
            self.clear()

class polSelector(QComboBox):
    def __init__(self, DataWizard):
        super(QComboBox, self).__init__()
        self.DataWizard = DataWizard

    def addAndConnectItems(self):
        self.clearMenu()
        upols = np.unique(self.DataWizard.pols)
        for pol in upols:
            if pol == 1:
                self.addItem('p')
            elif pol == 2:
                self.addItem('s')
            else:
                self.addItem('Non-polarized')
        self.DataWizard.pol = upols[0]
        self.activated.connect(self.onActivated)
        self.update()

    def onActivated(self):
        if self.currentText() == 'p':
            self.DataWizard.pol = 1
        elif self.currentText() == 's':
            self.DataWizard.pol = 2
        else:
            self.DataWizard.pol = 0
        self.DataWizard.updateDataSelection()

    def clearMenu(self):
        for index in range(self.count()):
            self.removeItem(index)
            self.clear()

class mainPlotWidget(object):
        def __init__(self, tab, DataWizard):
            self.tab = tab
            self.DataWizard = DataWizard

            self.figure = plt.figure()
            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self.tab)

class singleTab(QtWidgets.QWidget):
    def __init__(self, tabs, DataWizard):
        super(singleTab, self).__init__()
        self.tabs = tabs
        self.DataWizard = DataWizard
        self.mainPlot = mainPlotWidget(self, self.DataWizard)

        self.dataSelector = dataSelector(DataWizard)
        self.wavelengthSelector = wavelengthSelector(DataWizard)
        self.izaSelector = izaSelector(DataWizard)
        self.vzaSelector = vzaSelector(DataWizard)
        self.phiSelector = phiSelector(DataWizard)
        self.polSelector = polSelector(DataWizard)

        self.selectorLayout = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.selectorLayout.addWidget(QtWidgets.QLabel("Data file selector"))
        self.selectorLayout.addWidget(self.dataSelector)
        self.selectorLayout.addWidget(QtWidgets.QLabel("Wavelength selector"))
        self.selectorLayout.addWidget(self.wavelengthSelector)
        self.selectorLayout.addWidget(QtWidgets.QLabel("Incidence angle selector"))
        self.selectorLayout.addWidget(self.izaSelector)
        self.selectorLayout.addWidget(QtWidgets.QLabel("Viewing angle selector"))
        self.selectorLayout.addWidget(self.vzaSelector)
        self.selectorLayout.addWidget(QtWidgets.QLabel("Phi selector"))
        self.selectorLayout.addWidget(self.phiSelector)
        self.selectorLayout.addWidget(QtWidgets.QLabel("Polarization selector"))
        self.selectorLayout.addWidget(self.polSelector)

        self.splitterH = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitterH.addWidget(self.mainPlot.toolbar)
        # self.splitterH.addWidget(self.dataSelector)

        self.splitterH1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitterH1.addWidget(self.mainPlot.canvas)
        self.splitterH1.addWidget(self.selectorLayout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.splitterH)
        self.splitter.addWidget(self.splitterH1)


        self.layout = QtWidgets.QHBoxLayout(self)
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
        self.FileWalker = FileWalker()
        self.DataWizard = DataWizard()

        self.tabs.addTab(singleTab(self.tabs, self.DataWizard), 'Tab 1')

        self.openFileButton = openFileButton('Open File', self.FileWalker, self.DataWizard, self.tabs)

        self.splitterv = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitterv.addWidget(self.FileWalker)
        self.splitterv.addWidget(self.openFileButton)

        self.splitterh = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitterh.addWidget(self.splitterv)
        self.splitterh.addWidget(self.tabs)

        self.setCentralWidget(self.splitterh)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))

        self.setWindowTitle('BiRD view v1.0')
        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())


# comment
