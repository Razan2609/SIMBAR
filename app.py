from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3


app = Flask(__name__)
app.secret_key = "simbar"

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================
# LOGIN
# =====================

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def proses_login():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE username = ? AND password = ?
        """,
        (username, password)
    ).fetchone()

    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        return redirect("/dashboard")

    return "Username atau Password Salah"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =====================
# DASHBOARD
# =====================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()

    # =====================
    # DASHBOARD ADMIN
    # =====================
    if session["role"] == "admin":

        total_barang = conn.execute(
            "SELECT COUNT(*) FROM barang"
        ).fetchone()[0]

        total_pinjam = conn.execute(
            """
            SELECT COUNT(*)
            FROM peminjaman
            WHERE status='Disetujui'
            """
        ).fetchone()[0]

        menunggu = conn.execute(
            """
            SELECT *
            FROM peminjaman
            WHERE status='Menunggu'
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()

        barang_tersedia = max(0, total_barang - total_pinjam)

        conn.close()

        return render_template(
            "admin/admin.html",
            total_barang=total_barang,
            total_pinjam=total_pinjam,
            barang_tersedia=barang_tersedia,
            menunggu=menunggu
        )

    # =====================
    # DASHBOARD SISWA
    # =====================

    total_barang = conn.execute(
        "SELECT COUNT(*) FROM barang"
    ).fetchone()[0]

    total_pinjam = conn.execute(
        """
        SELECT COUNT(*)
        FROM peminjaman
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    aktif = conn.execute(
        """
        SELECT COUNT(*)
        FROM peminjaman
        WHERE user_id = ?
        AND status = 'Disetujui'
        """,
        (session["user_id"],)
    ).fetchone()[0]

    aktivitas = conn.execute(
        """
        SELECT *
        FROM peminjaman
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 3
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "siswa/dashboard.html",
        total_barang=total_barang,
        total_pinjam=total_pinjam,
        tersedia=total_barang - total_pinjam,
        aktif=aktif,
        aktivitas=aktivitas
    )
    # =====================
# BARANG
# =====================

@app.route("/barang")
def barang():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()

    data_barang = conn.execute("""
        SELECT * FROM barang
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "siswa/barang.html",
        role=session.get("role"),
        data_barang=data_barang,
        is_admin=session.get("role") in ["admin", "superadmin"],
        is_superadmin=session.get("role") == "superadmin"
    )
    
@app.route("/peminjaman")
def peminjaman():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()

    data = conn.execute("""
        SELECT *
        FROM peminjaman
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    barang = conn.execute("""
        SELECT *
        FROM barang
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "siswa/peminjaman.html",
        data=data,
        barang=barang
    )

@app.route("/ajukan-peminjaman", methods=["POST"])
def ajukan_peminjaman():

    if "user_id" not in session:
        return redirect("/")

    barang = request.form["barang"]
    jumlah = request.form["jumlah"]
    tanggal = request.form["tanggal"]
    keperluan = request.form["keperluan"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO peminjaman
        (user_id, barang, jumlah, tanggal_pinjam, keperluan, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            barang,
            jumlah,
            tanggal,
            keperluan,
            "Menunggu"
        )
    )

    conn.commit()
    conn.close()

    return redirect("/peminjaman")

@app.route("/riwayat")
def riwayat():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()

    data = conn.execute(
        """
        SELECT *
        FROM peminjaman
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "siswa/riwayat.html",
        data=data
    )


@app.route("/profil")
def profil():

    if "user_id" not in session:
        return redirect("/")

    return render_template("siswa/profil.html")


@app.route("/admin/peminjaman")
def admin_peminjaman():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()

    data = conn.execute("""
        SELECT
            p.*,
            u.username
        FROM peminjaman p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin/admin_peminjaman.html",
        data=data
    )
    
@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return redirect("/dashboard")

    conn = get_db()

    total_barang = conn.execute(
        "SELECT COUNT(*) FROM barang"
    ).fetchone()[0]

    total_pinjam = conn.execute(
        """
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Disetujui'
        """
    ).fetchone()[0]

    barang_tersedia = max(0, total_barang - total_pinjam)

    menunggu = conn.execute(
        """
        SELECT *
        FROM peminjaman
        WHERE status='Menunggu'
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_barang=total_barang,
        total_pinjam=total_pinjam,
        barang_tersedia=barang_tersedia,
        menunggu=menunggu
    )
    
@app.route("/setujui/<int:id>")
def setujui(id):

    conn = get_db()

    conn.execute(
        "UPDATE peminjaman SET status='Disetujui' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin/peminjaman")


@app.route("/tolak/<int:id>")
def tolak(id):

    conn = get_db()

    conn.execute(
        "UPDATE peminjaman SET status='Ditolak' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin/peminjaman")

@app.route("/laporan")
def laporan():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()

    menunggu = conn.execute("""
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Menunggu'
    """).fetchone()[0]

    disetujui = conn.execute("""
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Disetujui'
    """).fetchone()[0]

    ditolak = conn.execute("""
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Ditolak'
    """).fetchone()[0]

    dikembalikan = conn.execute("""
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Dikembalikan'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "admin/laporan.html",
        menunggu=menunggu,
        disetujui=disetujui,
        ditolak=ditolak,
        dikembalikan=dikembalikan
    )
    
@app.route("/isi-barang")
def isi_barang():
    conn = get_db()

    conn.execute("INSERT INTO barang (nama, stok) VALUES ('Laptop ASUS', 10)")
    conn.execute("INSERT INTO barang (nama, stok) VALUES ('Proyektor Epson', 5)")
    conn.execute("INSERT INTO barang (nama, stok) VALUES ('Kamera Canon', 3)")

    conn.commit()
    conn.close()

    return "Data berhasil ditambahkan"

@app.route("/kembalikan/<int:id>")
def kembalikan(id):

    conn = get_db()

    conn.execute(
        "UPDATE peminjaman SET status='Dikembalikan' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/riwayat")


@app.route("/superadmin")
def superadmin():

    if session.get("role") != "superadmin":
        return redirect("/dashboard")

    conn = get_db()

    total_user = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_admin = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role='admin'"
    ).fetchone()[0]

    total_siswa = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role='siswa'"
    ).fetchone()[0]

    total_barang = conn.execute(
        "SELECT COUNT(*) FROM barang"
    ).fetchone()[0]

    total_peminjaman = conn.execute(
        """
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Disetujui'
        """
    ).fetchone()[0]

    users = conn.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    conn.close()

    return render_template(
        "superadmin/superadmin.html",
        total_user=total_user,
        total_admin=total_admin,
        total_siswa=total_siswa,
        total_barang=total_barang,
        total_peminjaman=total_peminjaman,
        users=users
    )
    
@app.route("/statistik")
def statistik():

    if session.get("role") != "superadmin":
        return redirect("/dashboard")

    conn = get_db()

    total_barang = conn.execute(
        "SELECT COUNT(*) FROM barang"
    ).fetchone()[0]

    total_user = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_peminjaman = conn.execute(
        "SELECT COUNT(*) FROM peminjaman"
    ).fetchone()[0]

    total_disetujui = conn.execute(
        """
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Disetujui'
        """
    ).fetchone()[0]

    total_dikembalikan = conn.execute(
        """
        SELECT COUNT(*)
        FROM peminjaman
        WHERE status='Dikembalikan'
        """
    ).fetchone()[0]

    barang_populer = conn.execute(
        """
        SELECT barang,
        COUNT(*) as jumlah
        FROM peminjaman
        GROUP BY barang
        ORDER BY jumlah DESC
        LIMIT 5
        """
    ).fetchall()

    conn.close()

    return render_template(
        "superadmin/statistik.html",
        total_barang=total_barang,
        total_user=total_user,
        total_peminjaman=total_peminjaman,
        total_disetujui=total_disetujui,
        total_dikembalikan=total_dikembalikan,
        barang_populer=barang_populer
    )

@app.route("/users")
def users():

    if session.get("role") != "superadmin":
        return redirect("/dashboard")

    conn = get_db()

    data = conn.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "superadmin/users.html",
        data=data
    )
    
@app.route("/tambah-user", methods=["POST"])
def tambah_user():

    if session.get("role") != "superadmin":
        return redirect("/dashboard")

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO users
        (username, password, role)
        VALUES (?, ?, ?)
        """,
        (username, password, role)
    )

    conn.commit()
    conn.close()

    return redirect("/users")

@app.route("/hapus-user/<int:id>")
def hapus_user(id):

    if session.get("role") != "superadmin":
        return redirect("/dashboard")

    conn = get_db()

    conn.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/users")

@app.route("/aktivitas")
def aktivitas():

    if session.get("role") != "superadmin":
        return redirect("/dashboard")

    conn = get_db()

    data = conn.execute("""
        SELECT *
        FROM peminjaman
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()

    conn.close()

    return render_template(
        "superadmin/aktivitas.html",
        data=data
    )

@app.route("/tambah-barang", methods=["GET", "POST"])
def tambah_barang():

    if session.get("role") not in ["admin", "superadmin"]:
        return redirect("/dashboard")

    if request.method == "POST":
        nama = request.form["nama"]
        stok = request.form["stok"]

        conn = get_db()
        conn.execute(
            "INSERT INTO barang (nama, stok) VALUES (?, ?)",
            (nama, stok)
        )
        conn.commit()
        conn.close()

        return redirect("/barang")

    return render_template("superadmin/tambah_barang.html")

@app.route("/edit-barang/<int:id>", methods=["GET", "POST"])
def edit_barang(id):

    if session.get("role") not in ["admin", "superadmin"]:
        return redirect("/dashboard")

    conn = get_db()

    if request.method == "POST":

        nama = request.form["nama"]
        stok = request.form["stok"]

        conn.execute(
            "UPDATE barang SET nama=?, stok=? WHERE id=?",
            (nama, stok, id)
        )

        conn.commit()
        conn.close()

        return redirect("/barang")

    barang = conn.execute(
        "SELECT * FROM barang WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "superadmin/edit_barang.html",
        barang=barang
    )

if __name__ == "__main__":
    app.run(debug=True)