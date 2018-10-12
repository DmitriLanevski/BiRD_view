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
        self.setWindowTitle('PyQt & matplotlib demo: Data plotting')

        self.data = DataHolder()
        self.series_list_model = QStandardItemModel()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.update_ui()
        self.on_show()

    def load_file(self, filename=None):
        filename,  _filter = QtWidgets.QFileDialog.getOpenFileName(self,
            'Open a data file', '.', 'CSV files (*.csv);;All Files (*.*)')

        if filename:
            self.data.load_from_file(filename)
            self.fill_series_list(self.data.series_names())
            self.status_text.setText("Loaded " + filename)
            self.update_ui()

    def update_ui(self):
        if self.data.series_count() > 0 and self.data.series_len() > 0:
            self.from_spin.setValue(0)
            self.to_spin.setValue(self.data.series_len() - 1)

            for w in [self.from_spin, self.to_spin]:
                w.setRange(0, self.data.series_len() - 1)
                w.setEnabled(True)
        else:
            for w in [self.from_spin, self.to_spin]:
                w.setEnabled(False)

    def on_show(self):
        self.axes.clear()
        self.axes.grid(True)

        has_series = False

        for row in range(self.series_list_model.rowCount()):
            model_index = self.series_list_model.index(row, 0)
            checked = self.series_list_model.data(model_index,
                Qt.CheckStateRole) == QVariant(Qt.Checked)
            name = str(self.series_list_model.data(model_index))

            if checked:
                has_series = True
                if self.legend_pp.isChecked():
                    x, y, z = self.data.get_series_data(name,90)
                elif self.legend_pp.isChecked() and self.legend_sp.isChecked():
                    x, y, z = self.data.get_series_data(name, 2)
                else:
                    x, y, z = self.data.get_series_data(name, 0)

                self.axes.scatter(x, y, z)

        if has_series and self.legend_cb.isChecked():
            self.axes.legend()
        self.canvas.draw()

    def on_about(self):
        msg = __doc__
        QtWidgets.QMessageBox.about(self, "About the demo", msg.strip())

    def fill_series_list(self, names):
        self.series_list_model.clear()

        for name in names:
            new_name = str(name) +" nm"
            item = QStandardItem(new_name)
            item.setCheckState(Qt.Unchecked)
            item.setCheckable(True)
            self.series_list_model.appendRow(item)

    def create_main_frame(self):
        self.main_frame = QtWidgets.QWidget()

        plot_frame = QtWidgets.QWidget()

        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        self.axes = self.fig.add_subplot(111,projection='3d')
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        log_label = QtWidgets.QLabel("Data series:")
        self.series_list_view =QtWidgets.QListView()
        self.series_list_view.setModel(self.series_list_model)

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

        self.legend_cb = QtWidgets.QCheckBox("Show L&egend")
        self.legend_cb.setChecked(False)

        self.legend_pp = QtWidgets.QCheckBox("P-polarization")
        self.legend_pp.setChecked(False)

        self.legend_sp = QtWidgets.QCheckBox("S-polarization")
        self.legend_sp.setChecked(False)

        self.show_button = QtWidgets.QPushButton("&Show")
        #self.connect(self.show_button, SIGNAL('clicked()'), self.on_show)
        self.show_button.clicked.connect(self.on_show)

        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        left_vbox.addWidget(self.mpl_toolbar)

        right_vbox =QtWidgets.QVBoxLayout()
        right_vbox.addWidget(log_label)
        right_vbox.addWidget(self.series_list_view)
        right_vbox.addLayout(spins_hbox)
        right_vbox.addWidget(self.legend_cb)
        right_vbox.addWidget(self.legend_pp)
        right_vbox.addWidget(self.legend_sp)
        right_vbox.addWidget(self.show_button)
        right_vbox.addStretch(1)

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

        load_action = self.create_action("&Load file",
            shortcut="Ctrl+L", slot=self.load_file, tip="Load a file")
        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

        self.add_actions(self.file_menu,
            (load_action, None, quit_action))

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
            #self.connect(action, SIGNAL(signal), slot)
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
        self.data = []
        self.names = []

        if filename:
            for line in csv.reader(open(filename)):
                (w, a1, a2, r, p) = line[0].split(";")
                self.data.append([float(w), float(a1), float(a2), float(r), float(p)])

            self.names.append(self.data[0][0])
            self.datalen = len(self.data)

            for i in range(len(self.data)):
                if self.data[i][0] not in self.names:
                    self.names.append(self.data[i][0])

    def series_names(self):
        """ Names of the data series
        """
        return self.names

    def series_len(self):
        """ Length of a data series
        """
        return self.datalen

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
