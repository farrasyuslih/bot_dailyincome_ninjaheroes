![License: NonCommercial](https://img.shields.io/badge/license-NonCommercial-red.svg)
## 📜 License
This project is under a **Proprietary License**.
> ✅ Free to use for **personal, educational** purposes  
> ❌ Not for resale, AI training, or commercial use  
> 📬 Contact: farrasyualih.prg@gmail.com for license inquiries

# Ninja Heroes Daily Income Bot

## Setup
1. Clone repository ini
2. Copy `config.env.example` menjadi `config.env`
3. Edit `config.env` dengan data login Anda:
   ```env
   EMAIL=your_email@example.com
   PASSWORD=your_password
   SERVER=Server (servernumber) - VILLAGENAME
   ```
4. Install dependencies:
   ```bash
   pip install selenium python-dotenv
   ```
5. Jalankan bot:
   ```bash
   python ninja_heroes_bot.py
   ```

## ⚠️ Penting
- Jangan pernah commit file `config.env` yang berisi data asli Anda
- File `config.env` sudah ada di `.gitignore`
