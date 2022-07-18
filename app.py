import io

import numpy as np
import streamlit as st
from PIL import Image


def get_concatenated_images(
    imgs: list[Image.Image],
    direction: str = "Horizontal",
    resize: bool = True,
):
    if direction == "Horizontal":
        max_height = max([im.height for im in imgs])
        if resize:
            imgs = [
                np.array(
                    im.resize((int(im.width * max_height / im.height), max_height))
                )
                for im in imgs
            ]
        else:
            imgs = [
                np.vstack(
                    [
                        np.array(im),
                        np.zeros((max_height - im.height, im.width, 4), dtype=np.uint8),
                    ]
                )
                if im.height != max_height
                else np.array(im)
                for im in imgs
            ]
        img = np.hstack(imgs)
    else:
        max_width = max([im.width for im in imgs])
        if resize:
            imgs = [
                np.array(im.resize((max_width, int(im.height * max_width / im.width))))
                for im in imgs
            ]
        else:
            imgs = [
                np.hstack(
                    [
                        np.array(im),
                        np.zeros((im.height, max_width - im.width, 4), dtype=np.uint8),
                    ]
                )
                if im.width != max_width
                else np.array(im)
                for im in imgs
            ]
        img = np.vstack(imgs)
    return Image.fromarray(img)


with st.form(key="form"):
    uploaded_files = st.file_uploader(
        "Upload images",
        type=["jpg", "jpeg", "png"],
        help="Image format: jpg, jpeg, png",
        accept_multiple_files=True,
    )
    imgs = []
    if uploaded_files is not None:
        for f in uploaded_files:
            img_bytes = f.read()
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
            imgs.append(img)
    ext = st.radio("Output format", ["PDF", "PNG", "JPEG"])
    direction = st.radio("Direction", ["Horizontal", "Vertical"])
    resize = st.radio("Size", ["Resize", "Original"]) == "Resize"
    is_submitted = st.form_submit_button("Submit")

if is_submitted and len(imgs) > 0:
    st.session_state.submitted = True

if "submitted" in st.session_state:
    img = get_concatenated_images(imgs, direction, resize)
    st.image(img)
    buf = io.BytesIO()
    if ext != "PNG":
        img.load()
        bk = Image.new("RGB", img.size, (255, 255, 255))
        bk.paste(img, mask=img.split()[3])
        img = bk
    img.save(buf, format=ext)
    bytes_img = buf.getvalue()

    btn_download = st.download_button(
        label="Download Image",
        data=bytes_img,
        file_name=f"imagename.{ext.lower()}",
    )
