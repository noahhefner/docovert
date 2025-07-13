import os
import subprocess
import tempfile
import zipfile

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration ---
# Define the allowed file extension.
ALLOWED_EXTENSIONS = {"docx"}


# --- Helper Function ---
def is_allowed_file(filename):
    """Checks if a filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Main Routes ---
@app.route("/")
def index():
    """Serves the main HTML user interface."""
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert_files():
    """
    Handles file uploads, conversion using Pandoc, zipping, and sending the result.
    """
    # 1. --- Basic Request Validation ---
    if "files[]" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist("files[]")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No selected files"}), 400

    # 2. --- Create a Secure Temporary Directory to Work In ---
    with tempfile.TemporaryDirectory() as tmpdir:
        processed_html_files = (
            []
        )  # To keep track of the successfully converted HTML files.

        for file in files:
            # 3. --- Validate and Save Each File ---
            if file and is_allowed_file(file.filename):
                filename = secure_filename(file.filename)
                input_path = os.path.join(tmpdir, filename)
                file.save(input_path)

                # 4. --- Prepare for Pandoc Conversion ---
                base_name = os.path.splitext(filename)[0]
                html_output_path = os.path.join(tmpdir, f"{base_name}.html")

                # 5. --- Run Pandoc as a Subprocess ---
                try:
                    # Use --self-contained to embed all images directly into the HTML file.
                    command = [
                        "pandoc",
                        input_path,
                        "-o",
                        html_output_path,
                        "--standalone",
                        "--self-contained",
                    ]
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    processed_html_files.append(html_output_path)

                except FileNotFoundError:
                    return (
                        jsonify(
                            {
                                "error": "Pandoc is not installed or not in the system's PATH."
                            }
                        ),
                        500,
                    )
                except subprocess.CalledProcessError as e:
                    return (
                        jsonify(
                            {
                                "error": f"Pandoc failed to convert {filename}",
                                "details": e.stderr,
                            }
                        ),
                        500,
                    )

        # 6. --- Check if Any Files Were Processed ---
        if not processed_html_files:
            return (
                jsonify(
                    {
                        "error": "No valid .docx files were provided or conversion failed."
                    }
                ),
                400,
            )

        # 7. --- Zip the Resulting HTML Files ---
        zip_path = os.path.join(tmpdir, "converted_documents.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for html_file_path in processed_html_files:
                arcname = os.path.basename(html_file_path)
                zipf.write(html_file_path, arcname)

        # 8. --- Send the Zip File to the User for Download ---
        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="converted_documents.zip",
        )


# --- Main Execution ---
if __name__ == "__main__":
    # Remember to set up a 'templates' folder with your 'index.html' file inside.
    app.run(debug=True, port=5000)
