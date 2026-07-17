import io
import hashlib
from typing import Tuple

import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from rembg import remove, new_session

# ═══════════════════════════════════════════════════════════════════
# 🔐 SECURITY SETTINGS
# ═══════════════════════════════════════════════════════════════════
APP_PASSWORD = "KDPGIFT2026"
BRAND_NAME = "KDPEasy Studio"
TOOL_NAME = "Background Remover"
WELCOME_MESSAGE = "Welcome, VIP Creator!"
# ═══════════════════════════════════════════════════════════════════

# Cap input image dimensions to avoid OOM on Streamlit Cloud free tier
MAX_INPUT_LONG_EDGE = 2400

AI_MODELS = {
    "isnet-general-use (best quality, recommended)": "isnet-general-use",
    "u2net (balanced)":                              "u2net",
    "u2netp (fastest, lower quality)":               "u2netp",
}

BG_PRESETS = {
    "Transparent (PNG)": None,
    "White":             (255, 255, 255),
    "Cream":             (252, 248, 240),
    "Black":             (0, 0, 0),
    "Custom color":      "custom",
}

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TOOL_NAME}",
    page_icon="✂️",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .main > div { padding-top: 2rem; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%); }
    .block-container { max-width: 1200px; }
    h1 { color: #1f2937; font-weight: 700; }
    h2, h3 { color: #1f2937; }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover { background-color: #4338ca; color: white; }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .stDownloadButton>button:hover { background-color: #059669; color: white; }
    div[data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed #cbd5e1;
    }
    .info-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 1rem;
    }
    .gift-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
        color: #78350f;
    }
    .login-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        max-width: 480px;
        margin: 3rem auto;
        text-align: center;
    }
    .login-card h2 { color: #1f2937; margin-bottom: 0.5rem; }
    .login-card .brand {
        color: #4f46e5;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    .preview-box {
        background: white;
        padding: 0.8rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    /* Checkered pattern background for transparent preview */
    .transparent-preview {
        background-image:
            linear-gradient(45deg, #e5e7eb 25%, transparent 25%),
            linear-gradient(-45deg, #e5e7eb 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #e5e7eb 75%),
            linear-gradient(-45deg, transparent 75%, #e5e7eb 75%);
        background-size: 20px 20px;
        background-position: 0 0, 0 10px, 10px -10px, -10px 0;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🔐 Password gate
# ═══════════════════════════════════════════════════════════════════
def check_password() -> bool:
    if st.session_state.get("auth_ok"):
        return True

    st.markdown(
        f"""
        <div class="login-card">
            <div class="brand">{BRAND_NAME} · 🎁 Free VIP Gift</div>
            <h2>✂️ {TOOL_NAME}</h2>
            <p style="color:#6b7280;margin-bottom:1.5rem;">
                Enter your VIP password to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        pw = st.text_input("Password", type="password",
                           label_visibility="collapsed",
                           placeholder="Enter password…")
        ok = st.form_submit_button("🔓 Unlock", use_container_width=True)

    if ok:
        if pw == APP_PASSWORD:
            st.session_state.auth_ok = True
            st.rerun()
        else:
            st.error("❌ Wrong password. Please try again.")
    return False


if not check_password():
    st.stop()


# ═══════════════════════════════════════════════════════════════════
# 🤖 Model session (cached so the model file downloads once)
# ═══════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading AI engine (first time only, ~30s)…")
def get_session(model_name: str):
    return new_session(model_name)


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def shrink_if_huge(img: Image.Image, max_edge: int = MAX_INPUT_LONG_EDGE) -> Image.Image:
    w, h = img.size
    long_edge = max(w, h)
    if long_edge <= max_edge:
        return img
    scale = max_edge / long_edge
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    return img.resize((new_w, new_h), Image.LANCZOS)


def recover_clipped_edges(rgba_img: Image.Image, passes: int) -> Image.Image:
    """Dilate the alpha channel outward by ~1px per pass.

    rembg's mask is a hard cut, which can clip into the subject on hair,
    fur, or soft-contrast edges. Expanding the kept area by a couple of
    pixels reclaims that detail. Pure PIL — no extra dependency, unlike
    rembg's alpha_matting option (which needs pymatting/numba and failed
    to install on Streamlit Cloud).
    """
    if passes <= 0:
        return rgba_img
    r, g, b, a = rgba_img.split()
    for _ in range(passes):
        a = a.filter(ImageFilter.MaxFilter(3))
    return Image.merge("RGBA", (r, g, b, a))


@st.cache_data(show_spinner=False, max_entries=20)
def remove_background_cached(image_bytes: bytes, model_name: str,
                              precise_edges: bool = True,
                              _v: int = 3) -> bytes:
    """Run rembg on the input bytes and return RGBA PNG bytes."""
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    img = shrink_if_huge(img)
    session = get_session(model_name)
    cleaned = remove(img, session=session, post_process_mask=True)
    cleaned = recover_clipped_edges(cleaned, passes=2 if precise_edges else 0)
    buf = io.BytesIO()
    cleaned.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def apply_background(rgba_png_bytes: bytes,
                     bg_rgb: Tuple[int, int, int]) -> bytes:
    """Composite the transparent PNG onto a solid color background."""
    fg = Image.open(io.BytesIO(rgba_png_bytes)).convert("RGBA")
    canvas = Image.new("RGB", fg.size, bg_rgb)
    canvas.paste(fg, mask=fg.split()[-1])
    buf = io.BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════
# Header + logout
# ═══════════════════════════════════════════════════════════════════
hl, hr = st.columns([5, 1])
with hl:
    st.markdown(
        f"<h1>✂️ {TOOL_NAME}  "
        f"<span style='color:#f59e0b;font-size:1rem;'>🎁 VIP gift</span></h1>"
        f"<p style='color:#6b7280;margin-top:-0.5rem;'>"
        f"{BRAND_NAME} — {WELCOME_MESSAGE}</p>",
        unsafe_allow_html=True,
    )
with hr:
    st.write("")
    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    model_label = st.selectbox("AI model", list(AI_MODELS.keys()), index=0)
    model_name = AI_MODELS[model_label]

    precise_edges = st.checkbox(
        "🎯 Recover clipped edges (recommended)",
        value=True,
        help="If the AI cuts a bit into hair, fur, or fine details, this "
             "gently expands the kept area to reclaim it. Turn off only "
             "if you need a tighter, exact cutout on a simple image.",
    )

    bg_label = st.selectbox("Output background", list(BG_PRESETS.keys()), index=0)
    bg_choice = BG_PRESETS[bg_label]

    if bg_choice == "custom":
        custom_hex = st.color_picker("Pick a color", "#FFFFFF")
        bg_rgb = hex_to_rgb(custom_hex)
    elif bg_choice is None:
        bg_rgb = None
    else:
        bg_rgb = bg_choice

    output_filename = st.text_input("Output filename",
                                     value="no-background.png")
    if not output_filename.lower().endswith(".png"):
        output_filename += ".png"

    st.markdown("---")
    st.markdown(
        '<div class="info-card" style="font-size:0.85rem;">'
        "💡 <b>Tip:</b> Use <b>Transparent</b> output for stickers, "
        "cover cutouts, or to drop the subject onto another scene. "
        "Pick a solid color for clean product photos."
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
# Upload
# ═══════════════════════════════════════════════════════════════════
st.markdown("### 1️⃣ Upload your image")

uploaded = st.file_uploader(
    "Drag & drop or browse. Supports PNG, JPG, JPEG, WEBP. "
    f"Images larger than {MAX_INPUT_LONG_EDGE}px on the long edge "
    "are auto-shrunk to save memory.",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
)

if uploaded is None:
    st.info("👆 Upload an image to get started.")
    st.markdown(
        '<div class="gift-card">'
        "🎁 <b>This is a free VIP gift from KDPEasy Studio.</b><br>"
        "Use it on as many images as you'd like. "
        "If you're publishing on KDP, you may also enjoy our paid Suite — "
        "AI Upscaler, Story Composer, and PDF Builder — at "
        "<b>kdpeasy-upscaler.streamlit.app</b>."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()


image_bytes = uploaded.getvalue()
input_image = Image.open(io.BytesIO(image_bytes))
in_w, in_h = input_image.size
size_kb = len(image_bytes) / 1024


# ═══════════════════════════════════════════════════════════════════
# Process button + side-by-side preview
# ═══════════════════════════════════════════════════════════════════
st.markdown("### 2️⃣ Remove the background")

action_col1, action_col2 = st.columns([1, 3])
with action_col1:
    go = st.button("✂️ Remove background", use_container_width=True)
with action_col2:
    st.caption(
        f"Input: **{in_w} × {in_h} px**  •  "
        f"**{size_kb:.0f} KB**  •  "
        f"Model: **{model_label.split(' (')[0]}**"
    )

if go or st.session_state.get("last_rgba_bytes"):
    if go:
        try:
            with st.spinner("Removing background… (5-15 seconds)"):
                rgba_bytes = remove_background_cached(image_bytes, model_name,
                                                       precise_edges)
            st.session_state["last_rgba_bytes"] = rgba_bytes
            st.session_state["last_image_bytes"] = image_bytes
        except Exception as e:
            st.error(f"❌ Could not process the image: {e}")
            st.stop()
    else:
        rgba_bytes = st.session_state["last_rgba_bytes"]

    # Apply chosen background
    if bg_rgb is None:
        final_bytes = rgba_bytes
        is_transparent = True
    else:
        final_bytes = apply_background(rgba_bytes, bg_rgb)
        is_transparent = False

    out_kb = len(final_bytes) / 1024

    st.markdown("### 3️⃣ Before vs after")

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(image_bytes, caption="Original", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with pcol2:
        preview_class = "preview-box transparent-preview" \
            if is_transparent else "preview-box"
        st.markdown(f'<div class="{preview_class}">', unsafe_allow_html=True)
        st.image(final_bytes, caption="Background removed",
                 use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.success(
        f"✅ Done! Output: **{out_kb:.0f} KB**  •  "
        f"{'Transparent PNG' if is_transparent else f'PNG with solid background'}"
    )

    st.download_button(
        label=f"⬇️ Download {output_filename}",
        data=final_bytes,
        file_name=output_filename,
        mime="image/png",
        use_container_width=True,
    )

    st.markdown(
        '<div class="gift-card" style="margin-top:1rem;">'
        "✨ <b>Enjoyed this free tool?</b> "
        "If you publish picture books or coloring books on KDP, "
        "check out our complete creator Suite: "
        "AI Upscaler (300 DPI prints), Story Composer (auto-layout pages), "
        "and PDF Builder (one-click KDP-ready PDFs). "
        "Ask us at <b>daodinhthe1989@gmail.com</b>."
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#9ca3af;font-size:0.85rem;'>"
    f"{BRAND_NAME} — {TOOL_NAME} 🎁  •  "
    f"Made with ❤️ for KDP & Etsy creators"
    f"</div>",
    unsafe_allow_html=True,
)
