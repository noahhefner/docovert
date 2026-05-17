import os
import tempfile
import zipfile

from flask import Blueprint, jsonify, request, send_file
from pathvalidate import sanitize_filename
import pypandoc

bp = Blueprint("convert", __name__)

# Supported output formats mapping format ID to (pandoc_format, file_extension)
# Some formats have different names in Pandoc than their file extensions
SUPPORTED_OUTPUT_FORMATS = {
    "html": ("html", "html"),
    "markdown": ("markdown", "md"),
    "docx": ("docx", "docx"),
    "odt": ("odt", "odt"),
    "rst": ("rst", "rst"),
    "latex": ("latex", "tex"),
    "rtf": ("rtf", "rtf"),
    "epub": ("epub", "epub"),
    "pdf": ("pdf", "pdf"),
    "plain": ("plain", "txt"),
    "json": ("json", "json"),
}


@bp.route("/formats", methods=["GET"])
def get_supported_formats():
    """Return the list of supported output formats."""
    # Return the display names (keys) rather than the internal Pandoc format names
    return jsonify({"formats": list(SUPPORTED_OUTPUT_FORMATS.keys())})


@bp.route("/convert", methods=["POST"])
def convert_files():
    """Handles file uploads, conversion, and response.

    This function processes POST requests containing one or more files.
    It attempts to convert each file to the specified output format using pypandoc,
    zips the resulting files, and sends the zip archive to the client.

    Expected form data:
        files[]: List of files to convert
        output_format: Target format (default: "html")

    Returns:
        A zip file containing the converted documents on success,
        or a JSON error message on failure.
    """

    if "files[]" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist("files[]")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No selected files"}), 400

    # Get the output format from the request, default to HTML
    output_format_key = request.form.get("output_format", "html").lower()

    # Validate the output format
    if output_format_key not in SUPPORTED_OUTPUT_FORMATS:
        return (
            jsonify(
                {
                    "error": f"Unsupported output format: {output_format_key}",
                    "supported_formats": list(SUPPORTED_OUTPUT_FORMATS.keys()),
                }
            ),
            400,
        )

    # Get the Pandoc format name and file extension
    output_format, output_extension = SUPPORTED_OUTPUT_FORMATS[output_format_key]

    # Special handling for certain formats that require additional flags
    extra_args = []
    if output_format_key in ("html", "pdf", "epub"):
        extra_args = ["--embed-resources", "--standalone"]

    with tempfile.TemporaryDirectory() as tmpdir:
        processed_files = []

        for file in files:
            if file and file.filename:
                filename = sanitize_filename(file.filename)
                input_path = os.path.join(tmpdir, filename)
                file.save(input_path)

                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(tmpdir, f"{base_name}.{output_extension}")

                try:
                    # For binary formats like DOCX and PDF, we need to write to a file
                    if output_format_key in ("docx", "pdf", "odt", "epub"):
                        pypandoc.convert_file(
                            input_path,
                            output_format,
                            outputfile=output_path,
                            extra_args=extra_args,
                        )
                    else:
                        # For text formats, convert to string and write
                        output = pypandoc.convert_file(
                            input_path,
                            output_format,
                            extra_args=extra_args,
                        )
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(output)

                    processed_files.append(output_path)

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

        if not processed_files:
            return (
                jsonify({"error": "No files were successfully converted."}),
                400,
            )

        zip_path = os.path.join(tmpdir, "converted_documents.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for output_file_path in processed_files:
                arcname = os.path.basename(output_file_path)
                zipf.write(output_file_path, arcname)

        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="converted_documents.zip",
        )
