from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw
import qrcode
import io

app = Flask(__name__)

LOGO_SCALE = 5
BOX_MARGIN = 8

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form.get("data")
        logo_file = request.files.get("logo")

        if not data or not logo_file:
            return "Missing data or logo.", 400

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        logo = Image.open(logo_file).convert("RGBA")
        qr_w, qr_h = img_qr.size
        logo_size = qr_w // LOGO_SCALE
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        logo_w, logo_h = logo.size
        pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)

        draw = ImageDraw.Draw(img_qr)
        draw.rectangle(
            [pos[0] - BOX_MARGIN, pos[1] - BOX_MARGIN,
             pos[0] + logo_w + BOX_MARGIN, pos[1] + logo_h + BOX_MARGIN],
            fill="white"
        )

        img_qr.paste(logo, pos, mask=logo)

        img_io = io.BytesIO()
        img_qr.save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png",
                         as_attachment=True, download_name="qr_code.png")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
