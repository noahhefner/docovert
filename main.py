import os
import subprocess
import tempfile
import zipfile

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"docx"}


def is_allowed_file(filename):
    """Checks if a filename has an allowed extension.

    Args:
        filename: The name of the file to check.

    Returns:
        True if the filename has an allowed extension, False otherwise.
    """

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/static/<path:filename>")
def serve_static_assets(filename):

    try:
        # send_from_directory is a secure way to send files from a directory.
        # It prevents users from accessing files outside the specified folder.
        return send_from_directory("static", filename)
    except FileNotFoundError:
        # Optional: handle the case where the file doesn't exist.
        return "File not found", 404


@app.route("/")
def index():
    """Serves the main HTML user interface.

    Returns:
        The rendered HTML template for the main page.
    """

    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert_files():
    """Handles file uploads, conversion, and response.

    This function processes POST requests containing one or more '.docx' files.
    It converts each valid file to HTML using Pandoc, zips the resulting
    HTML files, and sends the zip archive to the client.

    Returns:
        A zip file containing the converted HTML documents on success,
        or a JSON error message on failure.
    """

    if "files[]" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist("files[]")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No selected files"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        processed_html_files = []

        for file in files:
            if file and is_allowed_file(file.filename):
                filename = secure_filename(file.filename)
                input_path = os.path.join(tmpdir, filename)
                file.save(input_path)

                base_name = os.path.splitext(filename)[0]
                html_output_path = os.path.join(tmpdir, f"{base_name}.html")

                try:
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

        if not processed_html_files:
            return (
                jsonify(
                    {
                        "error": "No valid .docx files were provided or conversion failed."
                    }
                ),
                400,
            )

        zip_path = os.path.join(tmpdir, "converted_documents.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for html_file_path in processed_html_files:
                arcname = os.path.basename(html_file_path)
                zipf.write(html_file_path, arcname)

        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="converted_documents.zip",
        )


if __name__ == "__main__":

    app.run(debug=True, port=5000)
