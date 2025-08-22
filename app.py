from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from stegano import lsb
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable cache in dev

# Home Page
@app.route("/")
def home():
    # Renders the main home page with links to encode and decode
    return render_template("index.html")

# Encode Page
@app.route("/encode", methods=["GET", "POST"])
def encode():
    if request.method == "POST":
        if "cover_image" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        cover_image = request.files["cover_image"]
        secret_message = request.form["secret_message"]
        password = request.form["password"]

        if cover_image and secret_message and password:
            output_file = "static/encoded.png"
            lsb.hide(cover_image, secret_message + "::" + password).save(output_file)
            # Sends the encoded image as a downloadable attachment
            return send_file(output_file, as_attachment=True)

    # Renders the encode form page
    return render_template("encode.html")

# Decode Page
@app.route("/decode", methods=["GET", "POST"])
def decode():
    if request.method == "POST":
        if "stego_image" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        stego_image = request.files["stego_image"]
        password = request.form["password"]

        if stego_image and password:
            stego_image.save("static/stego.png")
            secret = lsb.reveal("static/stego.png")

            if secret and "::" in secret:
                message, stored_password = secret.split("::")
                if password == stored_password:
                    # Renders the result page with the secret message
                    return render_template("result.html", message=message)
                else:
                    # Renders the result page with a wrong password message
                    return render_template("result.html", message="❌ Wrong Password")
            else:
                # Renders the result page if no hidden message is found
                return render_template("result.html", message="❌ No hidden message found")

    # Renders the decode form page
    return render_template("decode.html")

if __name__ == "__main__":
    app.run(debug=True)