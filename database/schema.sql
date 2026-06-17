DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS barang;
DROP TABLE IF EXISTS peminjaman;
DROP TABLE IF EXISTS pengembalian;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE barang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    stok INTEGER NOT NULL
);

CREATE TABLE peminjaman (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    barang_id INTEGER,
    nama_peminjam TEXT NOT NULL,
    kelas TEXT NOT NULL,
    jumlah INTEGER NOT NULL,
    tanggal_pinjam DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'Ditinjau',

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(barang_id) REFERENCES barang(id)
);

CREATE TABLE pengembalian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peminjaman_id INTEGER,
    tanggal_kembali DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'Dikembalikan',

    FOREIGN KEY(peminjaman_id) REFERENCES peminjaman(id)
);

INSERT INTO users (username,password,role)
VALUES
('admin','admin123','admin'),
('siswa','siswa123','siswa');