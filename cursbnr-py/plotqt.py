#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from pathlib import Path
from sys import argv
from typing import Any, Mapping, Sequence

import matplotlib
import numpy as np
from curs.db import CursDB
from curs.types import Date, extract_dates_values, to_date, to_date_opt
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.pyplot import cm
from qtpy import QtWidgets
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

matplotlib.use("Qt5Agg")


def main():
    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "--db", metavar="DB", type=str, help="target database", default=None
    )
    arg_parser.add_argument(
        "--start-date",
        metavar="YYYY-MM-DD",
        type=to_date,
        help="earliest date to show",
        default=None,
    )
    arg_parser.add_argument(
        "--end-date",
        metavar="YYYY-MM-DD",
        type=to_date,
        help="latest date to show",
        default=None,
    )

    arg_parser.add_argument(
        "--currency",
        metavar="CUR",
        type=str,
        default=None,
    )

    args = arg_parser.parse_args(argv[1:])

    if args.db is None:
        db_file = Path(__file__).parent / "bnr.db"
    else:
        db_file = Path(args.db)

    db = CursDB(db_file, mode="ro")

    go_back = relativedelta(years=0, months=0, days=15)

    if args.start_date is None and args.end_date is None:
        args.end_date = today()
        args.start_date = today() - go_back

    pp = {}
    if args.currency is not None:
        pp["currency"] = args.currency

    app = QtWidgets.QApplication(sys.argv)
    CursWindow(db=db, date_range=(args.start_date, args.end_date), **pp)
    app.exec_()


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, dpi=100):
        self._plot_data = {}

        super(MplCanvas, self).__init__(Figure((6.4, 4.8), dpi=dpi))
        # self.figure.set_rasterized(True)

    def set_plot_data(self, data: Mapping[str, Mapping[str, Any]]):
        new_plot_data = dict()
        for currency, data in data.items():
            self._add_plot_data(new_plot_data, currency, **data)
        self._plot_data = new_plot_data
        self._replot()
        self.draw()

    @staticmethod
    def _add_plot_data(_plot_data, /, currency: str, *, x, y, color=None):
        _plot_data[currency] = {"x": x, "y": y, "color": color}

    if False:  # due to navigation toolbar

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
        axes.locator_params(axis="x", tight=True, nbins=64)
        axes.locator_params(axis="y", tight=True, nbins=36)
        axes.tick_params(labelsize=6)

        def n_days(x: Sequence[Date]):
            if not len(x):
                return 0
            return (x[-1] - x[0]).days

        n_max_days = max(map(lambda data: n_days(data["x"]), self._plot_data.values()))

        match n_max_days:
            case n if n <= 30:
                marker = "o"
                markersize = 8
            case n if n < 90:
                marker = "o"
                markersize = 4
            case n if n <= 180:
                marker = "o"
                markersize = 2
            case _:
                marker = None
                markersize = None

        for label, data in self._plot_data.items():
            x = data["x"]
            y = data["y"]

            axes.plot(
                x,
                y,
                label=label,
                marker=marker,
                color=data["color"],
                markersize=markersize,
            )

        fig.autofmt_xdate(rotation=45)
        fig.set_tight_layout(True)
        axes.grid(True, which="both", axis="y")
        axes.set_ylabel("RON")
        axes.legend()

    if False:  # due to navigation toolbar

        def resizeEvent(self, event):
            self._resize_figure(event.oldSize(), event.size())
            return super().resizeEvent(event)


class CursWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        self._db = kwargs.pop("db")
        db = self._db
        date_from, date_to = map(to_date_opt, kwargs.pop("date_range", (None, None)))
        currency = kwargs.pop("currency", "EUR")

        self._past_currencies = set()

        super(CursWindow, self).__init__(*args, **kwargs)

        self._initUI(
            date_from=date_from,
            date_to=date_to,
            currency=currency,
            date_range=db.get_date_range(),
            currencies=db.get_currencies(),
        )

        self._replot_xy()

    @staticmethod
    def _generate_colors(length):
        return cm.rainbow(np.linspace(0, 1, length)) * np.array([0.75, 0.75, 0.75, 1])

    def _initUI(
        self,
        *,
        date_from: Date | None,
        date_to: Date | None,
        currency: str,
        date_range: tuple[Date, Date],
        currencies: list[str],
    ):
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        plot = MplCanvas(self, dpi=100)

        top_row = QHBoxLayout()

        self._currency_cb = QComboBox()
        self._currency_cb.addItems(currencies)

        if "," in currency:
            currency, *past_curr = (currency for currency in currency.split(","))
            self._past_currencies.update(past_curr)
            self._past_currencies.intersection_update(currencies)
            del past_curr
        else:
            past_curr = ()

        self._currency_cb.setCurrentText(currency if currency in currencies else "EUR")

        top_row.addWidget(self._currency_cb)

        label1 = QLabel("&From:")
        top_row.addWidget(label1)
        self._date_from_edit = QDateEdit()
        self._date_from_edit.setDisplayFormat("yyyy-MM-dd")
        label1.setBuddy(self._date_from_edit)

        top_row.addWidget(self._date_from_edit)

        label2 = QLabel("&To:")
        top_row.addWidget(label2)

        self._date_to_edit = QDateEdit()
        self._date_to_edit.setDisplayFormat("yyyy-MM-dd")
        label2.setBuddy(self._date_from_edit)

        top_row.addWidget(self._date_to_edit)

        # self._currency_cb.activated.connect(_uncheck_keep)
        button = QPushButton("&Plot!")
        button.pressed.connect(self._replot_xy)
        top_row.addWidget(button)

        # ck_label = QLabel("&Keep others:")
        # top_row.addWidget(ck_label)
        self._keep_ckb = QCheckBox("&Keep others")
        # ck_label.setBuddy(self._keep_ckb)
        top_row.addWidget(self._keep_ckb)
        self._keep_ckb.setChecked(bool(self._past_currencies))

        top_row.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addWidget(plot)

        self._plot = plot

        toolbar = NavigationToolbar(plot, self)

        layout.addWidget(toolbar)

        center = QWidget()
        center.setLayout(layout)

        self.setWindowTitle("CursDB plotter")
        self.setCentralWidget(center)

        self._set_minmax_date(date_range, init=(date_from, date_to))

        date_range[0]

        self.show()

    def _set_minmax_date(
        self,
        date_range: tuple[Date | None, Date | None],
        *,
        init: tuple[Date | None, Date | None] | None = None,
    ) -> None:
        date_from, date_to = date_range
        if date_range is not None:
            self._date_from_edit.setMinimumDate(date_from)
            self._date_to_edit.setMinimumDate(date_from)
        if date_to is not None:
            self._date_from_edit.setMaximumDate(date_to)
            self._date_to_edit.setMaximumDate(date_to)

        if init is not None:
            i_from, i_to = init
            self._date_from_edit.setDate(i_from if i_from is not None else date_from)
            self._date_to_edit.setDate(i_to if i_to is not None else date_to)

    def _replot_xy(self):
        db = self._db

        date_from = self._date_from_edit.date().toPyDate()
        date_to = self._date_to_edit.date().toPyDate()
        currency = self._currency_cb.currentText()
        self._currency_cb.currentIndex()
        self._keep_ckb.checkState()
        currencies = {currency}
        if self._keep_ckb.isChecked():
            currencies.update(self._past_currencies)

        rows = db.select_value_rows(
            date=(date_from, date_to), currency=list(currencies)
        )
        colors = self._generate_colors(len(currencies))

        data = {
            currency: (lambda x, y: {"x": x, "y": y, "color": colors[i]})(
                *extract_dates_values(rows, currency=currency)
            )
            for i, currency in enumerate(sorted(currencies))
        }

        self._plot.set_plot_data(data)
        self._past_currencies = currencies

        self._set_minmax_date(db.get_date_range())


if __name__ == "__main__":
    main()
