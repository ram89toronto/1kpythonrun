import streamlit as st
from mss import mss
from PIL import Image
import io

st.title("Screenshot Capture and Crop")

# --- Session State Initialization ---
if 'screenshot_bytes' not in st.session_state:
    st.session_state.screenshot_bytes = None
if 'cropped_image' not in st.session_state:
    st.session_state.cropped_image = None
if 'crop_coords' not in st.session_state:
    st.session_state.crop_coords = (0, 0, 500, 500)

def take_screenshot():
    """Captures the primary monitor's screen."""
    with mss() as sct:
        monitor = sct.monitors[1]  # Get information of monitor 1
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        # Convert to bytes for storing in session state
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        st.session_state.screenshot_bytes = img_bytes.getvalue()
        st.session_state.cropped_image = None # Reset cropped image on new screenshot


# --- UI Elements ---
if st.button("Take Screenshot"):
    take_screenshot()

if st.session_state.screenshot_bytes:
    st.subheader("Your Screenshot")
    screenshot_image = Image.open(io.BytesIO(st.session_state.screenshot_bytes))
    st.image(screenshot_image, caption="Full Screenshot", use_column_width=True)

    st.subheader("Crop Your Image")

    # Get image dimensions for slider limits
    img_width, img_height = screenshot_image.size

    # User input for cropping
    left = st.slider("Left", 0, img_width, st.session_state.crop_coords[0])
    top = st.slider("Top", 0, img_height, st.session_state.crop_coords[1])
    right = st.slider("Right", left, img_width, min(st.session_state.crop_coords[2], img_width))
    bottom = st.slider("Bottom", top, img_height, min(st.session_state.crop_coords[3], img_height))

    st.session_state.crop_coords = (left, top, right, bottom)

    if st.button("Crop Image"):
        if right > left and bottom > top:
            cropped = screenshot_image.crop((left, top, right, bottom))
            st.session_state.cropped_image = cropped
        else:
            st.error("Invalid crop dimensions. Right must be greater than Left, and Bottom must be greater than Top.")

if st.session_state.cropped_image:
    st.subheader("Cropped Image")
    st.image(st.session_state.cropped_image, caption="Cropped Image")

    # --- Download Button ---
    # Convert cropped image to bytes for download
    buf = io.BytesIO()
    st.session_state.cropped_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Cropped Image",
        data=byte_im,
        file_name="cropped_screenshot.png",
        mime="image/png"
    )
