"""
3D visualization of reflectance measurements loaded from .csc file.

Based on https://github.com/eliben/code-for-blog/blob/master/2009/pyqt_dataplot_demo/qt_mpl_dataplot.py
"""

import sys, os, csv, re
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import matplotlib
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

class Form(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle('Tropomi Data viewer')

        self.data1 = DataHolder()
        self.data2 = DataHolder()
        self.series_list_model_1 = QStandardItemModel()
        self.series_list_model_2 = QStandardItemModel()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.index = 0
        self.update_ui(self.index)
        self.on_show(self.index)
        self.on_change(self.index)

    def load_file(self, index, filename=None):
        filename,  _filter = QtWidgets.QFileDialog.getOpenFileName(self,
            'Open a data file', '.', 'CSV files (*.csv);;All Files (*.*)')

        if filename:
            if index == 0:
                self.data1.load_from_file(filename)
                self.fill_series_list(self.data1.series_names(), index)
            else:
                self.data2.load_from_file(filename)
                self.fill_series_list(self.data2.series_names(), index)

            #self.status_text.setText("Loaded " + filename)
            self.update_ui(index)

    def update_ui(self, index):
        if index == 0:
            if self.data1.series_count() > 0 and self.data1.series_len() > 0:
                self.from_spin.setValue(0)
                self.to_spin.setValue(self.data1.series_len() - 1)

                for w in [self.from_spin, self.to_spin]:
                    w.setRange(0, self.data1.series_len() - 1)
                    w.setEnabled(True)
            else:
                for w in [self.from_spin, self.to_spin]:
                    w.setEnabled(False)
        else:
            if self.data2.series_count() > 0 and self.data2.series_len() > 0:
                self.from_spin.setValue(0)
                self.to_spin.setValue(self.data2.series_len() - 1)

                for w in [self.from_spin, self.to_spin]:
                    w.setRange(0, self.data2.series_len() - 1)
                    w.setEnabled(True)
            else:
                for w in [self.from_spin, self.to_spin]:
                    w.setEnabled(False)

    def on_show(self, index):
        self.axes.clear()
        self.axes.grid(True)

        has_series = False
        if index == 0:
            list_model = self.series_list_model_1
            data = self.data1
        else:
            list_model = self.series_list_model_2
            data = self.data2

        for row in range(list_model.rowCount()):
            model_index = list_model.index(row, 0)
            checked = list_model.data(model_index,
                Qt.CheckStateRole) == QVariant(Qt.Checked)
            name = str(list_model.data(model_index))

            if checked:
                has_series = True
                if self.legend_pp.isChecked():
                    x, y, z = data.get_series_data(name, 'p')
                elif self.legend_pp.isChecked() and self.legend_sp.isChecked():
                    x, y, z = data.get_series_data(name, 2)
                else:
                    x, y, z = data.get_series_data(name, 's')

                self.axes.scatter(x, y, z)

        if has_series and self.legend_cb.isChecked():
            self.axes.legend()
        self.canvas.draw()

    def on_about(self):
        msg = __doc__
        QtWidgets.QMessageBox.about(self, "About the demo", msg.strip())

    #@pyqtSlot()
    def on_change(self, i):
        self.index = i

    def fill_series_list(self, names, index):
        if index == 0:
            self.series_list_model_1.clear()
        else:
            self.series_list_model_2.clear()

        for name in names:
            new_name = str(name) +" nm"
            item = QStandardItem(new_name)
            item.setCheckState(Qt.Unchecked)
            item.setCheckable(True)
            if index == 0:
                self.series_list_model_1.appendRow(item)
            else:
                self.series_list_model_2.appendRow(item)

    def create_main_frame(self):
        self.main_frame = QtWidgets.QWidget()

        plot_frame = QtWidgets.QWidget()

        self.index = 1
        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        self.axes = self.fig.add_subplot(111, projection='3d')
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        log_label = QtWidgets.QLabel("Data series:")
        self.series_list_view =QtWidgets.QListView()
        self.series_list_view.setModel(self.series_list_model_1)

        spin_label1 = QtWidgets.QLabel('X from')
        self.from_spin = QtWidgets.QSpinBox()
        spin_label2 = QtWidgets.QLabel('to')
        self.to_spin = QtWidgets.QSpinBox()

        spins_hbox =QtWidgets.QHBoxLayout()
        spins_hbox.addWidget(spin_label1)
        spins_hbox.addWidget(self.from_spin)
        spins_hbox.addWidget(spin_label2)
        spins_hbox.addWidget(self.to_spin)
        spins_hbox.addStretch(1)

        self.legend_cb = QtWidgets.QCheckBox("Show Legend")
        self.legend_cb.setChecked(False)

        self.legend_pp = QtWidgets.QCheckBox("P-polarization")
        self.legend_pp.setChecked(False)

        self.legend_sp = QtWidgets.QCheckBox("S-polarization")
        self.legend_sp.setChecked(False)

        self.show_button = QtWidgets.QPushButton("&Show")
        self.show_button.clicked.connect(lambda: self.on_show(self.index))

        self.load_button = QtWidgets.QPushButton("&Load file")
        self.load_button.clicked.connect(lambda: self.load_file(self.index))

        self.series_list_view2 =QtWidgets.QListView()
        self.series_list_view2.setModel(self.series_list_model_2)

        log_label_2 = QtWidgets.QLabel("Data series:")

        spin_label1_2 = QtWidgets.QLabel('X from')
        self.from_spin_2 = QtWidgets.QSpinBox()
        spin_label2_2 = QtWidgets.QLabel('to')
        self.to_spin_2 = QtWidgets.QSpinBox()

        spins_hbox_2 = QtWidgets.QHBoxLayout()
        spins_hbox_2.addWidget(spin_label1_2)
        spins_hbox_2.addWidget(self.from_spin_2)
        spins_hbox_2.addWidget(spin_label2_2)
        spins_hbox_2.addWidget(self.to_spin_2)
        spins_hbox_2.addStretch(1)

        self.legend_cb_2 = QtWidgets.QCheckBox("Show Legend")
        self.legend_cb_2.setChecked(False)

        self.legend_pp_2 = QtWidgets.QCheckBox("P-polarization")
        self.legend_pp_2.setChecked(False)

        self.legend_sp_2 = QtWidgets.QCheckBox("S-polarization")
        self.legend_sp_2.setChecked(False)

        self.show_button_2 = QtWidgets.QPushButton("&Show")
        self.show_button_2.clicked.connect(lambda: self.on_show(self.index))

        self.load_button_2 = QtWidgets.QPushButton("&Load file")
        self.load_button_2.clicked.connect(lambda: self.load_file(self.index))

        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        left_vbox.addWidget(self.mpl_toolbar)

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()

        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

        self.tab1.layout = QtWidgets.QVBoxLayout(self)
        self.tab1.layout.addWidget(log_label)
        self.tab1.layout.addWidget(self.series_list_view)
        self.tab1.layout.addLayout(spins_hbox)
        self.tab1.layout.addWidget(self.legend_cb)
        self.tab1.layout.addWidget(self.legend_pp)
        self.tab1.layout.addWidget(self.legend_sp)
        self.tab1.layout.addWidget(self.show_button)
        self.tab1.layout.addWidget(self.load_button)
        self.tab1.layout.addStretch(1)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QtWidgets.QVBoxLayout(self)
        self.tab2.layout.addWidget(log_label_2)
        self.tab2.layout.addWidget(self.series_list_view2)
        self.tab2.layout.addLayout(spins_hbox_2)
        self.tab2.layout.addWidget(self.legend_cb_2)
        self.tab2.layout.addWidget(self.legend_pp_2)
        self.tab2.layout.addWidget(self.legend_sp_2)
        self.tab2.layout.addWidget(self.show_button_2)
        self.tab2.layout.addWidget(self.load_button_2)
        self.tab2.layout.addStretch(1)
        self.tab2.setLayout(self.tab2.layout)

        right_vbox = QtWidgets.QVBoxLayout()
        right_vbox.addWidget(self.tabs)

        self.tabs.currentChanged.connect(self.on_change)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(right_vbox)
        self.main_frame.setLayout(hbox)

        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QtWidgets.QLabel("Please load a data file")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")

        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

        self.add_actions(self.file_menu,
            (None, quit_action))

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action


class DataHolder(object):
    """ A wrapper over a .csv file. First column contains wavelenght, second contains
        angles of the detector, third angels of the sample, forth contains measured value and
        fifth column contains polarization.
    """
    def __init__(self, filename=None):
        self.load_from_file(filename)

    def load_from_file(self, filename=None):
        pol = []
        IZA = []
        VZA = []
        lines = []
        self.data = []
        self.wavelengths = []

        if filename:
            for line in csv.reader(open(filename)):
                lines.append(line)

            Headers_string = lines[0]
            Headers_string = [e for e in Headers_string if e not in ('')]
            Headers = Headers_string[3:(len(Headers_string))]

            for header in Headers:
                pol.append(header[0])
                hParts = header.split('/')
                IZA.append(float(hParts[0][1:]))
                VZA.append(float(hParts[1]))

            for i in range(2, len(lines) - 1):
                if len(lines[i]) < 1:
                    break
                self.wavelengths.append(float(lines[i][0]))
                k = 0
                for j in range(6, len(lines[i])):
                    if j % 2 == 1:
                        data_row = (self.wavelengths[i - 2], float(IZA[k]), float(VZA[k]), float(lines[i][j]), pol[k])
                        self.data.append(data_row)
                        k = k + 1

    def series_names(self):
        """ Names of the data series
        """
        return self.wavelengths

    def series_len(self):
        """ Length of a data series
        """
        return len(self.data)

    def series_count(self):
        return len(self.data)

    def get_series_data(self, name, pol):
        x = []
        y = []
        z = []
        name = re.sub(' nm', '', name)
        for i in range(len(self.data)):
            if pol == 2:
                if self.data[i][0] == float(name):
                    x.append(self.data[i][1])
                    y.append(self.data[i][2])
                    z.append(self.data[i][3])
            else:
                if self.data[i][0] == float(name) and self.data[i][4] == pol:
                    x.append(self.data[i][1])
                    y.append(self.data[i][2])
                    z.append(self.data[i][3])
        return x, y, z

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()