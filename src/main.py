from datetime import date
from io import BytesIO
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, request, redirect, send_file
from src.pdf_parser import PdfParser
from src.recherche_cosine import RechercheCosine


rechercheCosine = RechercheCosine()
pdfParser = PdfParser()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "src/uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf"}
app.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/get_cosine")
def get_cosine() -> str:
    doc = pd.read_csv("final.csv")

    return render_template(
        "cosine.html",
        l1=doc.get("preconisation"),
        l2=doc.get("decision"),
        l3=doc.get("cosine_distance"),
        items=doc.get("cosine_distance"),
    )


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            pdf = pdfParser.parse_document(filename)
            date = pdfParser.extract_date(pdf)
            decisions = pdfParser.extract_decisions(pdf)
            vecteurs_decisions = rechercheCosine.creer_vecteurs_decisions(
                decisions, filename
            )
            dictionnaire_final = rechercheCosine.trouver_cosine_pour_preconisations(
                list_decision=decisions, vecteurs_decisions=vecteurs_decisions, date=date
            )
            l1 = dictionnaire_final.get("Thème")
            l2 = dictionnaire_final.get("Sous-Thème")
            l3 = dictionnaire_final.get("Constat")
            l4 = dictionnaire_final.get("Titre préconisation")
            l5 = dictionnaire_final.get("Détail préconisation")
            l6 = dictionnaire_final.get("Date de la décision")
            l7 = dictionnaire_final.get("Titre décision")
            l8 = dictionnaire_final.get("Détail décision")
            l9 = dictionnaire_final.get("Coefficient de similarité")
            rechercheCosine.result_to_exel(dictionnaire_final, filename)
            return render_template(
                "cosine.html",
                l1=l1,
                l2=l2,
                l3=l3,
                l4=l4,
                l5=l5,
                l6=l6,
                l7=l7,
                l8=l8,
                l9=l9,
                filename = filename
            )
            
    return render_template("upload.html")


@app.route('/export-excel/<path:requested_name>')
def export_excel(requested_name):
    dataframe = pd.read_excel("src/finals/"+requested_name+".xlsx")

    # Créer un fichier Excel en mémoire
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Similarite")
    output.seek(0)

    filename = f"similarite_cosine_{requested_name}_{date.today().isoformat()}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    app.run(debug=True)
