# Panduan Indonesia — SANRO Hermes Coding Toolkit

**SANRO** adalah ekosistem perangkat lunak yang dikembangkan oleh **Ario Guswara**. **Hermes Agent asli dikembangkan Nous Research**; starter ini merupakan toolkit komunitas independen untuk pekerjaan coding, bukan rilis Hermes Agent resmi.

## Tujuan

Membantu developer yang anggarannya terbatas membangun agent yang menerima tugas, menggunakan coding provider, melakukan tes, lalu menyiapkan **Draft PR** untuk diperiksa manusia. **Instalasi/deploy production tidak diberikan kepada agent.**

## Yang sudah tersedia

Versi **v0.1** dalam repo publik ini berisi validasi tugas, mock demo tanpa model/biaya, antarmuka provider, pratinjau perintah Codex, tes offline, serta petunjuk keamanan. **Belum ada eksekusi otomatis Codex atau GitHub PR oleh kode starter ini.**

Contoh nyata SANRO dari 8–9 November 2026:
- POS Public: jalur one-shot Codex berhasil membuat Draft PR #29 dan #31.
- Superadmin: timer otomatis mengambil Issue #9 dan membuat Draft PR #10 setelah pengujian. Hasil lengkap tercatat di [studi kasus](CASE_STUDIES.md).

**Jangan keliru menyamakan keberhasilan internal SANRO dengan kesiapan starter publik.** Integrasi agent/worker nyata adalah milestone berikutnya, harus diterapkan setelah isolasi/credential aman.

## Cara mencoba tanpa biaya model

Prasyarat: Python 3.11+; tidak perlu ChatGPT, token, VPS atau GitHub access untuk demo.

```bash
git clone https://github.com/arioguswara-oss/Hermes-Autonomous-Codex-Starter.git
cd Hermes-Autonomous-Codex-Starter
python3 -m unittest discover -s tests -v
python3 -m sanro_hermes.cli init-task > /tmp/sanro-task.json
python3 -m sanro_hermes.cli validate /tmp/sanro-task.json
python3 -m sanro_hermes.cli demo /tmp/sanro-task.json
python3 -m sanro_hermes.cli codex-preview /tmp/sanro-task.json
```

`init-task` membuat masa berlaku dua jam dari waktu Anda menjalankan. `demo` **hanya simulasi** (tidak membaca repo target, memanggil model, menyimpan token atau membuat PR). `codex-preview` hanya menampilkan *rencana perintah*, **tidak menjalankannya**.

## Bagaimana menjadi worker sungguhan?

Baca [arsitektur](ARCHITECTURE.md), [operasional](OPERATIONS.md), [keamanan](../SECURITY.md), dan [kontrak provider](PROVIDERS.md). Developer perlu membuat adapter yang menjalankan provider dalam sandbox/VM terpisah, membatasi filesystem dan jaringan, menggunakan izin GitHub paling kecil, merekam klaim tugas satu kali dan melaporkan test/commit/PR. **Jangan tempel perintah bypass sandbox ke shell tanpa isolasi luar.**

## Paket dan biaya

Codex-CLI dapat login menggunakan akun ChatGPT sendiri yang memenuhi syarat, tanpa kunci API berbayar terpisah; penggunaan tetap dibatasi oleh paket/model. Konfigurasi model ringan seperti **GPT-6 Luna** dapat menghemat jatah pada tugas sederhana, tetapi hasil dan kuota berbeda per pengguna. Lihat [catatan biaya](COSTS.md) dan [contoh VPS Contabo serta daftar kebutuhan software](VPS_CONTABO.md). Rio menggunakan Contabo pada implementasi SANRO karena menurut pengalamannya ekonomis, bukan berarti selalu termurah. Biaya VPS/listrik dan provider lain tetap mungkin ada.

## Strategi CI repository public dan private

Untuk **repository public**, GitHub Actions dengan runner standar biasanya menjadi pilihan CI termudah karena gratis sesuai ketentuan GitHub saat ini. Untuk **repository private**, gunakan **SANRO Local CI** yang diinstal dan diisolasi pada VPS/host sendiri agar job tersebut tidak menghabiskan alokasi compute GitHub-hosted Actions. Alternatifnya adalah self-hosted GitHub Actions runner atau runner GitHub berbayar dengan batas biaya yang disetujui Owner.

**Status:** Ini baru **rancangan integrasi**, bukan fitur otomatis dalam toolkit public. SANRO Local CI tidak disertakan dan belum diverifikasi untuk starter ini. Biaya VPS, keamanan, batas resource, redaksi log dan kontrol manusia tetap wajib. Baca [spesifikasi CI](CI_STRATEGY.md), [biaya](COSTS.md), dan [aturan billing GitHub](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

## Untuk komunitas

Dukungan Claude Code, 9router dan model lokal diharapkan melalui PR komunitas, **belum dinyatakan tersedia**. SANRO adalah identitas ekosistem Ario Guswara; penulis modul tambahan memperoleh atribusi masing-masing. Kritik dan kontribusi diterima lewat [CONTRIBUTING](../CONTRIBUTING.md).
