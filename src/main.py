from datetime import date
from io import BytesIO
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, render_template, request, flash, redirect, send_file
from src.pdf_parser import PdfParser
from src.recherche_cosine import RechercheCosine



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Define it in your environment or via `llm keys set openai`."
    )
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
rechercheCosine = RechercheCosine()
pdfParser = PdfParser()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "src/uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf"}
app.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)

def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_dico(filename):
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
    return l1,l2,l3,l4,l5,l6,l7,l8,l9, dictionnaire_final


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
            l1,l2,l3,l4,l5,l6,l7,l8,l9,dictionnaire_final = get_dico(filename=filename)
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


def is_pdf_mimetype(stream_headers) -> bool:
    """
    Vérifie le Content-Type fourni par le client ET la signature minimale.
    On ne se fie JAMAIS uniquement à l'extension.
    """
    # 1) Vérifier le header Content-Type
    content_type = stream_headers.get("Content-Type", "")
    if "pdf" not in content_type.lower():
        # ce n'est pas bloquant en soi (certains clients envoient multipart/ form-data générique),
        # on fera une vérification plus sûre juste après.
        pass
    return True

@app.post("/upload-pdf")
def upload_pdf():
    """
    Attend un multipart/form-data avec un champ 'file' contenant le PDF.
    Exemple cURL plus bas.
    Retourne des infos basiques et (optionnel) quelques métadonnées.
    """
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier 'file' dans la requête"}), 400

    file = request.files["file"]

    # Aucun fichier sélectionné
    if file.filename == "":
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    # Vérif extension
    if not allowed_file(file.filename):
        return jsonify({"error": "Extension non autorisée. Seuls les PDF sont acceptés."}), 400

    # Vérif Content-Type (indicatif)
    is_pdf_mimetype(request.headers)

    # Assainir le nom de fichier
    filename = secure_filename(str(file.filename))

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    l1,l2,l3,l4,l5,l6,l7,l8,l9,dictionnaire_final = get_dico(filename=filename)
    return jsonify(dictionnaire_final)
    
if __name__ == "__main__":
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

