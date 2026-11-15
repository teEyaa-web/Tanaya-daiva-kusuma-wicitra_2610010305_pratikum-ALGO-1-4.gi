import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate
import db_helper

class KembaliBukuWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(KembaliBukuWindow, self).__init__()
        uic.loadUi('kembali_buku.ui', self)
        
        self.dateKembali.setDate(QDate.currentDate())
        
        # Connect buttons & signals
        self.btnKembalikan.clicked.connect(self.process_return)
        self.btnBersihkan.clicked.connect(self.clear_fields)
        self.btnKembali.clicked.connect(self.close)
        
        # Menggunakan cellClicked agar lebih akurat saat baris tabel diklik
        self.tablePeminjaman.cellClicked.connect(self.on_table_click)
        self.dateKembali.dateChanged.connect(self.calculate_fine)
        
        # Adjust table headers
        self.tablePeminjaman.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        self.selected_tgl_pinjam = None
        self.selected_durasi = 0
        self.load_active_loans()

    def load_active_loans(self):
        self.tablePeminjaman.setRowCount(0)
        loans = db_helper.get_active_loans()
        for row_number, row_data in enumerate(loans):
            self.tablePeminjaman.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                self.tablePeminjaman.setItem(row_number, column_number, item)

    def on_table_click(self, row, column):
        # Mengambil data berdasarkan baris yang diklik di tabel
        # Kolom: 0=id_pinjam, 1=nama_peminjam, 2=id_buku, 3=judul, 4=tanggal_pinjam, 5=durasi, 6=status
        id_pinjam_item = self.tablePeminjaman.item(row, 0)
        nama_item = self.tablePeminjaman.item(row, 1)
        judul_item = self.tablePeminjaman.item(row, 3)
        tgl_pinjam_item = self.tablePeminjaman.item(row, 4)
        durasi_item = self.tablePeminjaman.item(row, 5)

        if id_pinjam_item and nama_item and judul_item:
            self.txtIdPinjam.setText(id_pinjam_item.text())
            self.txtNamaPeminjam.setText(nama_item.text())
            
            # Menyesuaikan nama komponen QLineEdit untuk Judul Buku
            judul_buku = judul_item.text()
            if hasattr(self, 'txtJudulBuku'):
                self.txtJudulBuku.setText(judul_buku)
            elif hasattr(self, 'txtJudul'):
                self.txtJudul.setText(judul_buku)
            
            self.selected_tgl_pinjam = tgl_pinjam_item.text()
            self.selected_durasi = int(durasi_item.text())
            self.txtIdPinjam.setReadOnly(True)
            
            self.calculate_fine()

    def calculate_fine(self):
        if not self.selected_tgl_pinjam:
            return
        tgl_pinjam = QDate.fromString(self.selected_tgl_pinjam, "yyyy-MM-dd")
        jatuh_tempo = tgl_pinjam.addDays(self.selected_durasi)
        tgl_kembali = self.dateKembali.date()
        
        hari_terlambat = jatuh_tempo.daysTo(tgl_kembali)
        if hari_terlambat > 0:
            denda = hari_terlambat * 1000
        else:
            denda = 0
        self.txtDenda.setText(str(denda))

    def process_return(self):
        id_pinjam = self.txtIdPinjam.text().strip()
        if not id_pinjam:
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal", "Pilih data peminjaman terlebih dahulu dari tabel!")
            return
            
        try:
            denda = float(self.txtDenda.text().strip())
            if denda < 0:
                raise ValueError()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal", "Nominal denda harus berupa angka positif!")
            return
            
        tanggal_kembali = self.dateKembali.date().toString("yyyy-MM-dd")
        
        reply = QtWidgets.QMessageBox.question(
            self, "Konfirmasi Pengembalian",
            f"Proses pengembalian untuk ID Pinjam {id_pinjam} dengan denda Rp {denda:,.0f}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return
            
        success, message = db_helper.return_book(id_pinjam, tanggal_kembali, denda)
        if success:
            QtWidgets.QMessageBox.information(self, "Berhasil", message)
            self.load_active_loans()
            self.clear_fields()
        else:
            QtWidgets.QMessageBox.critical(self, "Gagal", message)

    def clear_fields(self):
        self.txtIdPinjam.clear()
        self.txtIdPinjam.setReadOnly(False)
        self.txtNamaPeminjam.clear()
        if hasattr(self, 'txtJudulBuku'):
            self.txtJudulBuku.clear()
        if hasattr(self, 'txtJudul'):
            self.txtJudul.clear()
        self.dateKembali.setDate(QDate.currentDate())
        self.txtDenda.setText("0")
        self.selected_tgl_pinjam = None
        self.selected_durasi = 0
        self.tablePeminjaman.clearSelection()