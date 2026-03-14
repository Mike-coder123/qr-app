from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw
import qrcode
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form.get("data")
        logo_file = request.files.get("logo")

        if not data or not logo_file:
            return "Missing data or logo.", 400

        logo_scale = int(request.form.get("logo_scale", 5))
        box_margin = int(request.form.get("box_margin", 8))
        box_size   = int(request.form.get("box_size", 10))
        border     = int(request.form.get("border", 4))
        fill_color = request.form.get("fill_color", "#000000")
        back_color = request.form.get("back_color", "#ffffff")

        logo_scale = max(3, min(logo_scale, 10))
        box_margin = max(0, min(box_margin, 30))
        box_size   = max(5, min(box_size, 20))
        border     = max(1, min(border, 10))

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

        logo = Image.open(logo_file).convert("RGBA")
        qr_w, qr_h = img_qr.size
        logo_size = qr_w // logo_scale
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        logo_w, logo_h = logo.size
        pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)

        draw = ImageDraw.Draw(img_qr)
        draw.rectangle(
            [pos[0] - box_margin, pos[1] - box_margin,
             pos[0] + logo_w + box_margin, pos[1] + logo_h + box_margin],
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