import sys
from PyQt5 import QtWidgets, uic
import db_helper

class LaporanWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LaporanWindow, self).__init__()
        uic.loadUi('laporan.ui', self)
        
        self.btnRefresh.clicked.connect(self.load_report)
        self.btnKembali.clicked.connect(self.close)
        
        # Adjust table headers
        self.tablePopuler.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        self.load_report()

    def load_report(self):
        # Load general statistics
        stats = db_helper.get_general_statistics()
        self.lblTotalBuku.setText(f"Total Inventaris Buku:\n{stats['total_buku']} Eksemplar")
        self.lblActiveLoans.setText(f"Sedang Dipinjam:\n{stats['active_loans']} Buku")
        self.lblTotalDenda.setText(f"Total Denda Terkumpul:\nRp {stats['total_denda']:,.0f}")
        
        # Load most borrowed books
        self.tablePopuler.setRowCount(0)
        popular_books = db_helper.get_most_borrowed_books()
        for row_number, row_data in enumerate(popular_books):
            self.tablePopuler.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                self.tablePopuler.setItem(row_number, column_number, item)