# ✂️ KDPEasy Background Remover

A free VIP gift tool from KDPEasy Studio — removes the background
from any image in 5-15 seconds using AI. PNG transparent output, or
any solid background color you choose. Great for sticker sheets,
cover cutouts, product shots, or scene compositing.

**Live app:** https://kdpeasy-bg-remover.streamlit.app

---

## 🇻🇳 Hướng dẫn deploy (dành cho anh chủ tool)

### Bước 1 — Tạo repo mới trên GitHub
1. Mở https://github.com/new
2. **Repository name:** `kdpeasy-bg-remover`
3. **Public** ✅
4. ✅ Tick "Add a README file"
5. Bấm **Create repository**

### Bước 2 — Upload 3 file vào repo
Trong repo vừa tạo, bấm **Add file → Upload files**, kéo cả 3 file
trong thư mục `C:\Users\Admin\Downloads\KDPEasy-Background-Remover\`:

- `app.py`
- `requirements.txt`
- `README.md`

Bấm **Commit changes**.

### Bước 3 — Deploy lên Streamlit Cloud
1. Mở https://share.streamlit.io
2. Bấm **Create app → Deploy a public app from GitHub**
3. **Repository:** `daodinhthe1989-blip/kdpeasy-bg-remover`
4. **Branch:** `main`
5. **Main file path:** `app.py`
6. **App URL:** `kdpeasy-bg-remover`
7. Bấm **Deploy**

> ⚠️ **Lần đầu mở app sẽ chậm hơn các tool khác** (1-3 phút) vì
> phải tải AI model isnet-general-use (~170MB). Sau lần đầu thì
> nhanh — model được cache lại trên server.

Mật khẩu vào tool: **`KDPGIFT2026`**

---

## 🇺🇸 How customers use it

### What it does
Removes the background from any photo or illustration using AI.
Output is either a transparent PNG (great for stickers, cutouts,
compositing) or a clean solid-color background (great for product
shots or print files).

### Step-by-step
1. **Unlock** with the VIP password from your welcome email.
2. **Pick an AI model** in the left sidebar:
   - **isnet-general-use** — best quality (recommended)
   - **u2net** — balanced speed and quality
   - **u2netp** — fastest, slightly lower quality
3. **Pick an output background:**
   - **Transparent** — PNG with alpha channel
   - **White / Cream / Black** — solid color presets
   - **Custom color** — any color from a color picker
4. **Upload your image** (PNG, JPG, JPEG, WEBP).
5. **Click "Remove background"** and wait 5-15 seconds.
6. **Download** the result.

### Use cases
- 🏷️ **Sticker sheets** — transparent PNG ready for Etsy
- 🎨 **Cover cutouts** — drop your subject onto a new scene
- 📸 **Product shots** — clean white background for listings
- 🧱 **Compositing** — pull characters out of busy AI backgrounds
- 🖼️ **Coloring book characters** — extract for new layouts

### Recommended settings for different jobs
- **Stickers / Etsy printables:** isnet-general-use + Transparent
- **Product shots for KDP/Amazon:** isnet-general-use + White
- **Picture book character cutout:** isnet-general-use + Transparent
- **Quick preview / lots of images:** u2netp + any background

---

## 🛠️ Tech stack
- **Streamlit** — UI
- **rembg + ONNX Runtime** — AI background removal
  (isnet, u2net, u2netp models)
- **Pillow** — image handling

No paid APIs. Runs free on Streamlit Cloud.

---

Made with ❤️ by **KDPEasy Studio** as a thank-you to our VIP list.
