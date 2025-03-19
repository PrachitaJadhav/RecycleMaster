from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        selected_language = request.form.get("language")
        return redirect(url_for("join"))  # Redirect to join page

    return render_template("index.html")

@app.route("/join")
def join():
    return render_template("join.html")

if __name__ == "__main__":
    app.run(debug=True)
