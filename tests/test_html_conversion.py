import io
import zipfile

from pathlib import Path

resources = Path(__file__).parent / "resources"


def test_html_to_html(client):
    """
    Verify that uploading an HTML file and converting to HTML returns a ZIP
    containing the converted HTML.
    """

    # Send POST request to /convert containing HTML file with format HTML
    file_path = resources / "test.html"
    data = {
        "files[]": (file_path.open("rb"), file_path.name),
        "output_format": "html",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"
    assert "converted_documents.zip" in response.headers["Content-Disposition"]
    assert len(response.data) > 0

    # Unzip the ZIP and check the HTML file inside
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        assert len(zip_file_list) > 0, "ZIP file is empty"
        expected_html_file = "test.html"
        assert expected_html_file in zip_file_list, (
            f"{expected_html_file} not found in ZIP"
        )
        html_content = zipf.read(expected_html_file).decode("utf-8")
        assert "<html" in html_content.lower(), "HTML content is missing <html> tag"


def test_html_to_markdown(client):
    """
    Verify that uploading an HTML file and converting to Markdown returns a ZIP
    containing the converted Markdown file.
    """

    # Send POST request to /convert containing HTML file with format markdown
    file_path = resources / "test.html"
    data = {
        "files[]": (file_path.open("rb"), file_path.name),
        "output_format": "markdown",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"
    assert "converted_documents.zip" in response.headers["Content-Disposition"]
    assert len(response.data) > 0

    # Unzip the ZIP and check the markdown file inside
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        assert len(zip_file_list) > 0, "ZIP file is empty"
        expected_md_file = "test.md"
        assert expected_md_file in zip_file_list, (
            f"{expected_md_file} not found in ZIP"
        )
        md_content = zipf.read(expected_md_file).decode("utf-8")
        assert len(md_content) > 0, "Markdown content is empty"


def test_html_to_docx(client):
    """
    Verify that uploading an HTML file and converting to DOCX returns a ZIP
    containing the converted Word document.
    """

    # Send POST request to /convert containing HTML file with format docx
    file_path = resources / "test.html"
    data = {
        "files[]": (file_path.open("rb"), file_path.name),
        "output_format": "docx",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"
    assert "converted_documents.zip" in response.headers["Content-Disposition"]
    assert len(response.data) > 0

    # Unzip the ZIP and check the docx file inside
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        assert len(zip_file_list) > 0, "ZIP file is empty"
        expected_docx_file = "test.docx"
        assert expected_docx_file in zip_file_list, (
            f"{expected_docx_file} not found in ZIP"
        )


def test_html_to_rst(client):
    """
    Verify that uploading an HTML file and converting to reStructuredText
    returns a ZIP containing the converted RST file.
    """

    # Send POST request to /convert containing HTML file with format rst
    file_path = resources / "test.html"
    data = {
        "files[]": (file_path.open("rb"), file_path.name),
        "output_format": "rst",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"
    assert "converted_documents.zip" in response.headers["Content-Disposition"]
    assert len(response.data) > 0

    # Unzip the ZIP and check the rst file inside
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        assert len(zip_file_list) > 0, "ZIP file is empty"
        expected_rst_file = "test.rst"
        assert expected_rst_file in zip_file_list, (
            f"{expected_rst_file} not found in ZIP"
        )
        rst_content = zipf.read(expected_rst_file).decode("utf-8")
        assert len(rst_content) > 0, "RST content is empty"


def test_html_to_plain(client):
    """
    Verify that uploading an HTML file and converting to plain text
    returns a ZIP containing the converted TXT file.
    """

    # Send POST request to /convert containing HTML file with format plain
    file_path = resources / "test.html"
    data = {
        "files[]": (file_path.open("rb"), file_path.name),
        "output_format": "plain",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"
    assert "converted_documents.zip" in response.headers["Content-Disposition"]
    assert len(response.data) > 0

    # Unzip the ZIP and check the txt file inside
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        assert len(zip_file_list) > 0, "ZIP file is empty"
        expected_txt_file = "test.txt"
        assert expected_txt_file in zip_file_list, (
            f"{expected_txt_file} not found in ZIP"
        )
        txt_content = zipf.read(expected_txt_file).decode("utf-8")
        assert len(txt_content) > 0, "TXT content is empty"


def test_invalid_format(client):
    """
    Verify that requesting an invalid output format returns a 400 error
    with a helpful error message.
    """

    file_path = resources / "test.html"
    data = {
        "files[]": (file_path.open("rb"), file_path.name),
        "output_format": "invalid_format",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 400
    response_json = response.get_json()
    assert "error" in response_json
    assert "Unsupported output format" in response_json["error"]
    assert "supported_formats" in response_json


def test_default_format(client):
    """
    Verify that when no output_format is specified, it defaults to HTML.
    """

    # Send POST request without specifying output_format
    file_path = resources / "test.html"
    data = {"files[]": (file_path.open("rb"), file_path.name)}
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"

    # Verify the output is HTML (default)
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        expected_html_file = "test.html"
        assert expected_html_file in zip_file_list, (
            f"{expected_html_file} not found in ZIP"
        )


def test_multiple_files_different_formats(client):
    """
    Verify that converting multiple files to the same format works correctly.
    """

    # Send POST request with multiple files
    file_path_html = resources / "test.html"
    file_path_md = resources / "test.md"
    data = {
        "files[]": [
            (file_path_html.open("rb"), file_path_html.name),
            (file_path_md.open("rb"), file_path_md.name),
        ],
        "output_format": "markdown",
    }
    response = client.post("/convert", data=data, content_type="multipart/form-data")

    # Check response
    assert response.status_code == 200, response.data.decode()
    assert response.headers["Content-Type"] == "application/zip"

    # Unzip and verify both files were converted
    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zipf:
        zip_file_list = zipf.namelist()
        assert len(zip_file_list) == 2, f"Expected 2 files, got {len(zip_file_list)}"
        assert "test.md" in zip_file_list
        # The HTML file should also be converted to markdown (test_1.md or similar)
        md_files = [f for f in zip_file_list if f.endswith(".md")]
        assert len(md_files) >= 1, "No markdown files found in output"


def test_formats_endpoint(client):
    """
    Verify that the /formats endpoint returns the list of supported formats.
    """

    response = client.get("/formats")

    # Check response
    assert response.status_code == 200
    response_json = response.get_json()
    assert "formats" in response_json
    formats = response_json["formats"]
    assert isinstance(formats, list)
    assert len(formats) > 0
    # Verify some expected formats are present
    assert "html" in formats
    assert "markdown" in formats
    assert "docx" in formats
