# Zeuniverse: Logo Kit (Otan Tile)

Ikon aplikasi Zeuniverse adalah kepala Otan: tile orange dengan wajah Otan memenuhi seluruh ikon, mengikuti
cara Duolingo memakai maskotnya. Semua master berupa SVG fill-only (tanpa teks hidup, gambar raster, filter, atau stroke).
Semua file di-generate ulang dari `../build_kit.py`.

## Isi folder

| Folder | Isi |
|---|---|
| `master/` | `zeuniverse-icon.svg` (master utama), `-icon-small.svg` (untuk ≤ 32 px), `-icon-mono.svg` (satu warna, lubang asli), `-head.svg` (kepala tanpa tile), `-face.svg` (fitur saja, untuk permukaan orange), `-icon-fullbleed.svg` / `-icon-maskable.svg` (untuk platform yang memotong sendiri), wordmark, lockup horizontal dan stacked (navy / putih) |
| `variants/` | Ikon satu warna (hitam, putih, orange, navy) dan lockup satu warna (hitam, putih, navy) |
| `expressions/` | Set ekspresi Otan: default, happy, wink, wow, astronaut |
| `web/` | `favicon.ico`, `favicon.svg`, PNG 16/32/48, `apple-touch-icon.png`, `icon-192/512.png`, `maskable-512.png`, `site.webmanifest`, `head-snippet.html` |
| `png/` | PNG 1024 px untuk ikon dan ekspresi, PNG lebar 2000 px untuk lockup dan wordmark |
| `board/` | Board presentasi (`zeuniverse-board.html`) dan slide PNG dengan mockup |

## Warna

| Nama | HEX | RGB | CMYK (konversi awal) | Pantone (kandidat) |
|---|---|---|---|---|
| Otan Orange (utama) | `#F5822A` | 245 130 42 | 0 47 83 4 | ≈ 1495 C / 158 C |
| Fur Shade (jambul) | `#D9661C` | 217 102 28 | 0 53 87 15 | ≈ 7579 C |
| Peach Skin | `#FCD3A6` | 252 211 166 | 0 16 34 1 | ≈ 155 C |
| Space Navy (wordmark, mata) | `#2B2862` | 43 40 98 | 56 59 0 62 | ≈ 275 C |

Warna khusus karakter (dipakai hanya di dalam wajah): mulut `#3B1F3A`, lidah `#E8637A`, pipi `#F4917A`, hidung `#9A5430`, alis `#C2551C`.

Nilai CMYK adalah konversi otomatis, dan Pantone adalah kandidat terdekat. Cocokkan keduanya dengan swatch book dan proof dari percetakan sebelum dicetak.

**Kontras (WCAG):**
- Navy di atas putih: 13.3 : 1
- Navy di atas orange: 5.1 : 1, aman untuk teks
- Navy di atas peach: 9.5 : 1
- Putih di atas orange: **2.6 : 1**, jangan dipakai untuk teks kecil atau tombol. Pakai navy.

## Versi mana untuk apa

- **App icon, avatar, sticker:** `zeuniverse-icon.svg`.
- **Ukuran 32 px ke bawah (favicon, tab, notifikasi):** `zeuniverse-icon-small.svg`. Versi ini tanpa jambul, hidung, pipi, dan lidah, dengan satu kilau besar di tiap mata.
- **iOS / Android / PWA:** pakai `icon-fullbleed` atau `maskable`, karena platform-nya sudah memotong sudut sendiri. Jangan memasukkan tile membulat ke dalam tile lain.
- **Header website, dokumen:** lockup horizontal. **Merch, poster, splash:** lockup stacked.
- **Latar gelap:** lockup `-white` (wordmark putih, ikon tetap berwarna).
- **Sablon, emboss, bordir, fax:** versi satu warna di `variants/`.
- **Latar orange (kaos, banner):** `zeuniverse-face.svg` langsung di atas orange, tanpa tile.

## Ruang kosong dan ukuran minimum

- **Ruang kosong:** minimal ¼ tinggi ikon di setiap sisi (64 unit pada ikon 256). Untuk lockup, ukurannya diambil dari tinggi ikon di dalam lockup.
- **Jarak di dalam lockup:** jarak ikon ke wordmark sudah dikunci (52 unit horizontal, 48 unit stacked). Jangan diubah.
- **Ukuran minimum:**
  - Ikon penuh: 48 px. Di bawahnya, ganti ke versi small.
  - Ikon small: 16 px.
  - Lockup horizontal: lebar 160 px / 35 mm.
  - Wordmark saja: lebar 100 px / 25 mm.

## Wordmark

`zeuniverse` huruf kecil, dibangun custom sebagai geometri monoline rounded: stroke 22 unit pada x-height 100,
mangkuk lingkaran r 39, dan "s" dari dua elips. Wordmark ini tidak memakai font, jadi tidak ada lisensi font yang perlu dicek.
Titik huruf i selalu berwarna Otan Orange, kecuali di versi satu warna.

Untuk teks pendamping, sarannya font rounded open-source, misalnya Nunito atau Fredoka (lisensi OFL). Font ini tidak dipakai di dalam logo.

## Ekspresi

Ekspresi dipakai seperti Duolingo: untuk notifikasi, streak, event, dan feedback benar/salah. Aturannya:
- Bentuk tile, warna, masker wajah, dan jambul tidak boleh berubah. Yang boleh berubah hanya mata, alis, dan mulut.
- App icon resmi selalu memakai `otan-default` atau `zeuniverse-icon`.
- Ekspresi musiman (misalnya topi atau kostum) boleh ditambahkan di atas tile, selama wajah tetap terbaca di 48 px.

## Jangan

- Mengganti orange tile dengan warna lain, atau memberi gradient atau bayangan.
- Memutar, memiringkan, atau meregangkan ikon atau wordmark.
- Mengetik ulang "zeuniverse" dengan font lain.
- Menaruh ikon berwarna di atas foto ramai tanpa ruang kosong.
- Memakai versi detail penuh di bawah 32 px.
- Menaruh teks putih di atas orange.

## Hasil uji

- Ukuran 16 / 24 / 32 / 48 / 64 px sudah dirender dan dicek. Versi small terbaca sebagai wajah di 16 px.
- Satu warna: master mono memakai lubang asli (`evenodd`), bukan putih palsu, jadi aman untuk sablon dan latar apa pun.
- Hasil `svg_audit.py`:
  - Ikon mono: 100/100.
  - Ikon warna: 91/100. Satu-satunya peringatan adalah 9 warna, yang wajar untuk ikon maskot.
  - Lockup: 81/100, karena kilau mata putih di atas tile. Ini disengaja.

## Catatan terbuka

- Belum ada pengecekan merek dagang. Lakukan pencarian di PDKI (DJKI) dan reverse image search sebelum peluncuran.
- Ujung huruf "s" sedikit membulat lebih dari stroke-nya, karena pita elips adalah pendekatan. Ini tidak terlihat pada ukuran normal, tapi bisa dirapikan di Illustrator atau Figma kalau logo akan dipakai sangat besar (signage).
- File AI, EPS, atau PDF belum dibuat karena di mesin ini tidak ada Illustrator atau Inkscape. SVG bisa langsung dibuka dan diekspor dari Figma atau Illustrator.
