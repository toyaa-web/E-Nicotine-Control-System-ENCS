from flask import Flask, render_template_string, request
import datetime

app = Flask(__name__)
MINIMUM_AGE = 21

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ENCS | E-Nicotine Control System</title>
    <style>
        body {
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
            background: #0f172a;
            height: 100vh;
            overflow: hidden;
            color: white;
        }

        /* Animated grid background */
        body::before {
            content: "";
            position: absolute;
            width: 200%;
            height: 200%;
            background-image: linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
            background-size: 40px 40px;
            animation: moveGrid 20s linear infinite;
        }

        @keyframes moveGrid {
            from { transform: translate(0,0); }
            to { transform: translate(-200px,-200px); }
        }

        /* Floating orbs */
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.3;
            animation: float 10s ease-in-out infinite alternate;
        }

        .orb1 {
            width: 400px;
            height: 400px;
            background: #3b82f6;
            top: -100px;
            left: -100px;
        }

        .orb2 {
            width: 350px;
            height: 350px;
            background: #1d4ed8;
            bottom: -120px;
            right: -100px;
            animation-duration: 14s;
        }

        @keyframes float {
            from { transform: translateY(0px); }
            to { transform: translateY(40px); }
        }

        .navbar {
            position: relative;
            padding: 18px 50px;
            display: flex;
            justify-content: space-between;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            z-index: 2;
        }

        .logo {
            font-weight: bold;
            letter-spacing: 2px;
            font-size: 18px;
        }

        .main {
            position: relative;
            height: calc(100vh - 70px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2;
        }

        .card {
            background: rgba(255,255,255,0.06);
            backdrop-filter: blur(18px);
            padding: 45px;
            border-radius: 18px;
            width: 440px;
            text-align: center;
            box-shadow: 0 0 60px rgba(59,130,246,0.3);
            animation: fadeIn 1s ease-in-out;
            transition: 0.3s;
        }

        .card:hover {
            transform: translateY(-6px);
            box-shadow: 0 0 90px rgba(59,130,246,0.4);
        }

        h1 {
            margin-bottom: 5px;
            font-size: 24px;
        }

        .subtitle {
            font-size: 13px;
            opacity: 0.8;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.05);
            color: white;
            font-size: 14px;
        }

        input:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 12px rgba(59,130,246,0.6);
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border-radius: 8px;
            border: none;
            background: #3b82f6;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #2563eb;
            transform: scale(1.03);
        }

        .result {
            margin-top: 20px;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            animation: fadeIn 0.5s ease-in-out;
        }

        .allowed {
            background: rgba(34,197,94,0.2);
            color: #22c55e;
        }

        .denied {
            background: rgba(239,68,68,0.2);
            color: #ef4444;
        }

        footer {
            position: relative;
            text-align: center;
            padding: 12px;
            font-size: 12px;
            opacity: 0.6;
            z-index: 2;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        
    </style>
</head>
<body>

<div class="orb orb1"></div>
<div class="orb orb2"></div>

<div class="navbar">
    <div class="logo">ENCS</div>
    <div>Minimum Age: {{min_age}}+</div>
</div>

<div class="main">
    <div class="card">
        <h1>E-Nicotine Control System</h1>
        <div class="subtitle">
            Digital Age Verification for Vape Access Control
        </div>

        <form method="POST">
            <input type="text" name="nama" placeholder="Nama Lengkap" required>
            <input type="text" name="nik" placeholder="NIK (16 Digit)" maxlength="16" required>
            <input type="number" name="umur" placeholder="Umur" required>
            <button type="submit">VERIFIKASI</button>
        </form>


        {% if hasil %}
            <div class="result {{ status }}">
                {{ hasil }}
            </div>
        {% endif %}
    </div>
</div>

<footer>
Penelitian Terapan – Olimpiade Penelitian Siswa Indonesia (OPSI)
</footer>

</body>
</html>
"""


def validasi_nik(nik):
    if len(nik) != 16 or not nik.isdigit():
        return False, "NIK harus 16 digit angka"

    try:
        tanggal = int(nik[6:8])
        bulan = int(nik[8:10])
        tahun = int(nik[10:12])

        # Jika perempuan (tanggal > 40)
        if tanggal > 40:
            tanggal -= 40

        # Konversi tahun (asumsi 1900/2000)
        tahun += 2000 if tahun < 30 else 1900

        tanggal_lahir = datetime.date(tahun, bulan, tanggal)
        today = datetime.date.today()

        umur = today.year - tanggal_lahir.year
        if (today.month, today.day) < (tanggal_lahir.month, tanggal_lahir.day):
            umur -= 1

        return True, umur

    except:
        return False, "Tanggal lahir dalam NIK tidak valid"



@app.route("/", methods=["GET", "POST"])
def home():
    hasil = ""
    status = ""

    if request.method == "POST":
        nama = request.form["nama"]
        nik = request.form["nik"]
        umur_input = int(request.form["umur"])

        valid, hasil_nik = validasi_nik(nik)

        if not valid:
            hasil = hasil_nik
            status = "denied"

        else:
            umur_dari_nik = hasil_nik

            if umur_dari_nik != umur_input:
                hasil = "✖ Umur tidak sesuai dengan data KTP"
                status = "denied"

            elif umur_dari_nik >= MINIMUM_AGE:
                waktu = datetime.datetime.now()
                with open("transaksi_web.txt", "a") as file:
                    file.write(f"{waktu} | {nama} | {nik}\n")

                hasil = "✔ Verifikasi KTP Berhasil - Transaksi Diizinkan"
                status = "allowed"

            else:
                hasil = "✖ Umur pada KTP belum memenuhi syarat"
                status = "denied"

    return render_template_string(
        HTML,
        hasil=hasil,
        status=status,
        min_age=MINIMUM_AGE
  )

if __name__ == "__main__": app.run(debug=True)

