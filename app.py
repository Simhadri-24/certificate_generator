from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import io, os, base64

app = Flask(__name__)

# Template and font paths
TEMPLATE_PATH = "static/certificate_template.jpg"
CUSTOM_FONT_PATH = "fonts/GreatVibes-Regular.ttf"    # optional font
FALLBACK_FONT = "arial.ttf"  # make sure this exists on your system

# Helper functions
def load_font_for_size(size):
    """Load custom or fallback font."""
    if CUSTOM_FONT_PATH and os.path.exists(CUSTOM_FONT_PATH):
        try:
            return ImageFont.truetype(CUSTOM_FONT_PATH, size)
        except Exception:
            pass
    try:
        return ImageFont.truetype(FALLBACK_FONT, size)
    except Exception:
        return ImageFont.load_default()

def fit_font_to_width(draw, text, max_width, starting_size=130, min_size=20):
    """Adjust font size to fit within given width."""
    size = starting_size
    while size >= min_size:
        font = load_font_for_size(size)
        text_w = draw.textlength(text, font=font)
        if text_w <= max_width:
            return font, size, text_w
        size -= 2
    # fallback
    min_font = load_font_for_size(min_size)
    min_text_w = draw.textlength(text, font=min_font)
    return min_font, min_size, min(min_text_w, max_width)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_certificate():
    name = request.form.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not os.path.exists(TEMPLATE_PATH):
        return jsonify({"error": "Template not found"}), 404

    # Load image
    image = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size

    # Font settings
    max_width_fraction = 0.65
    max_text_width = img_w * max_width_fraction
    font, size, text_w = fit_font_to_width(draw, name, max_text_width, starting_size=180)

    # Position
    x = (img_w - text_w) / 2
    y = int(img_h * 0.420)

    # Draw text
    text_color = (25, 25, 25)
    draw.text((x, y), name, font=font, fill=text_color)

    # Output as JPG
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=95)
    base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{base64_img}"

    return jsonify({"image": data_uri})

if __name__ == "__main__":
    app.run(debug=True)
