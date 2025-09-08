import os
import tempfile
import zipfile

from flask import Blueprint, jsonify, request, send_file
from pathvalidate import sanitize_filename
import pypandoc

bp = Blueprint("convert", __name__, url_prefix="/convert")


@bp.route("", methods=["POST"])
def convert_files():
    """Handles file uploads, conversion, and response.

    This function processes POST requests containing one or more files.
    It attempts to convert each file to HTML using pypandoc, zips the resulting
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
            if file and file.filename:
                filename = sanitize_filename(file.filename)
                input_path = os.path.join(tmpdir, filename)
                file.save(input_path)

                base_name = os.path.splitext(filename)[0]
                html_output_path = os.path.join(tmpdir, f"{base_name}.html")

                try:
                    # Convert file to HTML with pypandoc
                    output = pypandoc.convert_file(
                        input_path,
                        "html",
                        extra_args=["--embed-resources", "--standalone"],
                    )
                    # Write the HTML output to file
                    with open(html_output_path, "w", encoding="utf-8") as f:
                        f.write(output)

                    processed_html_files.append(html_output_path)

                except OSError:
                    return (
                        jsonify(
                            {
                                "error": "Pandoc is not installed or not accessible. "
                                "Install it or run pypandoc.download_pandoc()."
                            }
                        ),
                        500,
                    )
                except RuntimeError as e:
                    return (
                        jsonify(
                            {
                                "error": f"Conversion failed for {filename}",
                                "details": str(e),
                            }
                        ),
                        500,
                    )

        if not processed_html_files:
            return (
                jsonify({"error": "No files were successfully converted."}),
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
