import os
from flask import Flask, render_template, request, send_file
from huffman import compress, decompress, huffman_decode
import json
from docx import Document
import PyPDF2

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
        if request.method == "POST":
            text = ""

            # Case 1: User uploaded a file
            if "file" in request.files and request.files["file"].filename:
                file = request.files["file"]
                filename = file.filename.lower()
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                # Handle .txt
                if filename.endswith(".txt"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()

                # Handle .docx
                elif filename.endswith(".docx"):
                    doc = Document(filepath)
                    text = "\n".join([para.text for para in doc.paragraphs])

                # Handle .pdf
                elif filename.endswith(".pdf"):
                    pdf_reader = PyPDF2.PdfReader(open(filepath, "rb"))
                    extracted = []

                    for i in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[i]
                        extracted.append(page.extract_text() or "")

                    text = "\n".join(extracted)

                
                elif filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    bit_string = data["bit_string"]
                    codes = data["codes"]

                    decompressed_text = huffman_decode(bit_string, codes)

                    output_file = "decompressed.txt"
                    output_path = os.path.join(COMPRESSED_FOLDER, output_file)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(decompressed_text)

                    return render_template(
                                "result.html",
                                decompressed=decompressed_text[:500],
                                original="",
                                compressed="",
                                codes=None,
                                ratio="",
                                download_file=output_file
                            )


                else:
                    return render_template("index.html", error="Only .txt, .docx, and .pdf files are supported!")

            # Case 2: If no file, check manual text input
            elif request.form.get("text"):
                text = request.form["text"]

            # If still empty → error
            if not text.strip():
                return render_template("index.html", error="Please enter text or upload a file!")

            # Now compress & process
            compressed, root, codes = compress(text)
            decompressed = decompress(compressed, root)
            compression_ratio = round(len(compressed) / (len(text) * 8), 3)

            compressed_path = os.path.join(COMPRESSED_FOLDER, "compressed.json")
            with open(compressed_path, "w", encoding="utf-8") as f:
                json.dump({"bit_string": compressed, "codes": codes}, f)

            return render_template("result.html",
                            original=text[:300] + "..." if len(text) > 300 else text,
                            compressed=compressed[:200] + "..." if len(compressed) > 200 else compressed,
                            decompressed=decompressed[:200] + "..." if len(decompressed) > 200 else decompressed,
                            ratio=compression_ratio,
                            codes=codes,
                            download_file="compressed.json")

        return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(COMPRESSED_FOLDER, filename), as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
