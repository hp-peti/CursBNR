import sys
from typing import List, Sequence

import matplotlib
from dateutil.relativedelta import relativedelta
from dateutil.utils import today

matplotlib.use("Qt5Agg")

import numpy as np
from cursdb import CursDB
from curstypes import Date, extract_dates_values, to_date_opt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.pyplot import cm
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import QDate
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, dpi=100):
        self._plot_data = {}

        super(MplCanvas, self).__init__(Figure((6.4, 4.8), dpi=dpi))
        # self.figure.set_rasterized(True)

    def set_plot_data(self, currency: str, x, y, *, color=None, remove_existing=True):
        if remove_existing:
            self._plot_data = {}

        self._plot_data[currency] = {"x": x, "y": y, "color": color}

        self._replot()

        self.draw()

    def _resize_figure(self, oldsize, newsize):
        if oldsize == newsize:
            return

        fig: Figure = self.figure

        fig.set_size_inches(
            newsize.width() / fig.get_dpi(),
            newsize.height() / fig.get_dpi(),
            forward=True,
        )

        self._replot()

    def _replot(self):
        fig: Figure = self.figure
        if len(self._plot_data) == 0:
            return

        fig.clear()
        axes = fig.add_subplot(111)

        def n_days(x: Sequence[Date]):
            if not len(x):
                return 0
            return (x[-1] - x[0]).days

        n_max_days = max(map(lambda data: n_days(data["x"]), self._plot_data.values()))

        match n_max_days:
            case n if n <= 7:
                marker = "8"
            case n if n < 30:
                marker = "o"
            case n if n < 60:
                marker = "."
            case _:
                marker = None

        for label, data in self._plot_data.items():
            x = data["x"]
            y = data["y"]

            axes.plot(x, y, label=label, marker=marker, color=data["color"])

        fig.autofmt_xdate(rotation=45)
        axes.grid(True, which="both", axis="y")
        axes.set_ylabel("RON")
        axes.legend()

    def resizeEvent(self, event):
        self._resize_figure(event.oldSize(), event.size())
        return super().resizeEvent(event)


class CursWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        self._db = kwargs.pop("db")
        date_from, date_to = map(to_date_opt, kwargs.pop("date_range", (None, None)))
        currencies = kwargs.pop("currencies")
        assert isinstance(currencies, list) and all(
            map(lambda s: isinstance(s, str), currencies)
        )

        super(CursWindow, self).__init__(*args, **kwargs)

        self._initUI(date_from, date_to, currencies)

        self._replot_xy()


    def _initUI(
        self, date_from: Date | None, date_to: Date | None, currencies: List[str]
    ):
        self._colors = cm.rainbow(np.linspace(0, 1, len(currencies))) * np.array(
            [0.75, 0.75, 0.75, 1]
        )

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        plot = MplCanvas(self, dpi=100)

        top_row = QHBoxLayout()


        self._currency_cb = QComboBox()
        self._currency_cb.addItems(currencies)
        self._currency_cb.setCurrentText("EUR")

        top_row.addWidget(self._currency_cb)


        label1 = QLabel("From:")
        top_row.addWidget(label1)
        self._date_from_edit = QDateEdit()
        self._date_from_edit.setDisplayFormat("yyyy-MM-dd")

        top_row.addWidget(self._date_from_edit)

        label2 = QLabel("To:")
        top_row.addWidget(label2)

        self._date_to_edit = QDateEdit()
        self._date_to_edit.setDisplayFormat("yyyy-MM-dd")

        top_row.addWidget(self._date_to_edit)

        # self._currency_cb.activated.connect(_uncheck_keep)
        button = QPushButton("&Plot!")
        button.pressed.connect(self._replot_xy)
        top_row.addWidget(button)

        top_row.addStretch()

        ck_label = QLabel("&Keep others:")
        top_row.addWidget(ck_label)
        self._keep_ckb = QCheckBox()
        ck_label.setBuddy(self._keep_ckb)
        top_row.addWidget(self._keep_ckb)
        self._keep_ckb.setCheckState(False)

        def _uncheck_keep(*args):
            self._keep_ckb.setCheckState(False)

        self._date_from_edit.dateChanged.connect(_uncheck_keep)
        self._date_to_edit.dateChanged.connect(_uncheck_keep)

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addWidget(plot)
        self._plot = plot

        center = QWidget()
        center.setLayout(layout)

        self.setCentralWidget(center)

        self._set_minmax_date(date_from, date_to)

        self.show()

    def _set_minmax_date(self, date_from, date_to) -> None:
        if date_from is not None:
            self._date_from_edit.setMinimumDate(date_from)
            self._date_to_edit.setMinimumDate(date_from)
            self._date_from_edit.setDate(date_from)
        if date_to is not None:
            self._date_from_edit.setMaximumDate(date_to)
            self._date_to_edit.setMaximumDate(date_to)
            self._date_to_edit.setDate(date_to)

    def _replot_xy(self):
        from_date = self._date_from_edit.date().toPyDate()
        to_date = self._date_to_edit.date().toPyDate()
        currency = self._currency_cb.currentText()
        n = self._currency_cb.currentIndex()
        keep = self._keep_ckb.checkState()
        rows = db.select_rows(date=(from_date, to_date), currency=currency)
        x, y = extract_dates_values(rows, currency=None)
        self._plot.set_plot_data(
            currency, x, y, color=self._colors[n], remove_existing=not keep
        )


db = CursDB("bnr.db", mode="ro")
go_back = relativedelta(years=3, months=0, days=0)

from_date, to_date = db.get_date_range()
currencies = db.get_currencies()

app = QtWidgets.QApplication(sys.argv)
w = CursWindow(db=db, date_range=(from_date, to_date), currencies=currencies)
app.exec_()
