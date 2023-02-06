import sys
import matplotlib
from dateutil.relativedelta import relativedelta
from dateutil.utils import today

matplotlib.use("Qt5Agg")


from qtpy import QtCore, QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from cursdb import CursDB
from curstypes import extract_dates_values

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, plot_data=([],[]), dpi=300):
        self.plot_data = plot_data
        super(MplCanvas, self).__init__(Figure((5,4), dpi=dpi))
        #self.figure.set_rasterized(True)

    def replot(self, oldsize, newsize):
        plot_data = getattr(self, "plot_data", None)
        if plot_data is None:
            return
        x, y, label = self.plot_data
        del self.plot_data

        if oldsize == newsize:
            return

        fig: Figure = self.figure

        fig.clear()

        fig.set_size_inches(newsize.width() / fig.get_dpi(), newsize.height() / fig.get_dpi(), forward=True)

        axes = fig.add_subplot(111)

        match len(x):
            case n if n <= 7:
                marker = "O"
            case n if n < 30:
                marker = "o"
            case n if n < 60:
                marker = "."
            case _:
                marker = None

        axes.plot(x, y, label=label, marker=marker, color="#000000")
        fig.autofmt_xdate(rotation=45)

        axes.grid(True, which="both", axis="y")
        # axes.axes.set_title(f"")
        axes.legend()

    def resizeEvent(self, event):
        self.replot(event.oldSize(), event.size())
        return super().resizeEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        plot_data = kwargs.pop("plot_data", None)

        super(MainWindow, self).__init__(*args, **kwargs)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        sc = MplCanvas(self, plot_data=plot_data, dpi=100)

        self.setCentralWidget(sc)

        self.show()


db = CursDB("bnr.db")
go_back = relativedelta(years=3, months=0, days=0)

x, y =  extract_dates_values(db.select_rows(
    date=(today() - go_back, None), currency="EUR"
), currency=None)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow(plot_data=(x,y,"EUR"))
app.exec_()
