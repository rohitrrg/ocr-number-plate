from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from functions import extract_plate_1, extract_plate_2, segment_characters, show_results
import cv2
import os

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('home.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = cv2.imread('uploads/'+filename)
            plate_img, plate = extract_plate_1(image)
            if plate is not None:
                print('Cascade')
                char = segment_characters(plate)
                plate_number = show_results(char)
                flash(plate_number)
            else:
                plate = extract_plate_2(image)
                if plate is not None:
                    print('Contours')
                    cv2.imwrite('photo.png', plate)
                    plate = cv2.imread('photo.png')
                    char = segment_characters(plate)
                    plate_number = show_results(char)
                    flash(plate_number)
                else:
                    flash('Not Found')
        else:
            flash('Not Found')

        return redirect('/')


if __name__ == "__main__":
    app.run()
