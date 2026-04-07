from PIL import Image
from flask import Flask, request, send_file, render_template
import io
import os
# from sys import argv
# from pathlib import Path

app = Flask(__name__)

# Homepage
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/crop', methods=['POST'])
def crop():
    # read the arguments
    file = request.files['pic']
    try:
        original_image = Image.open(file).convert('RGBA')
        original_name = os.path.splitext(file.filename)[0]
        new_filename = f"cropped_{original_name}"
        target_left = int(request.form['l'])
        target_top = int(request.form['t'])
        target_right = int(request.form['r'])
        target_bottom = int(request.form['b'])
    except Exception as e:
        return str(e), 400
    if target_right <= target_left or target_bottom <= target_top:
        return 'Invalid arguments'

    # expand the target area to include the whole original image
    bias_left = max(0, 0 - target_left)
    bias_top = max(0, 0 - target_top)
    bias_right = max(0, target_right - original_image.width)
    bias_bottom = max(0, target_bottom - original_image.height)
    canvas = Image.new("RGBA", (original_image.width + bias_left + bias_right,
        original_image.height + bias_top + bias_bottom), (0, 0, 0, 0))
    canvas.paste(original_image, (bias_left, bias_top))
    target_left += bias_left
    target_right += bias_left
    target_top += bias_top
    target_bottom += bias_top

    # output
    result = canvas.crop((target_left, target_top, target_right, target_bottom))
    img_io = io.BytesIO()
    result.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png", as_attachment=True, download_name=new_filename)


if __name__ == "__main__":
    app.run(debug=True)