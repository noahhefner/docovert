import io
import zipfile

from pathlib import Path

resources = Path(__file__).parent / "resources"

def test_docx(client):
    """
    Verify that uploading a markdown file to /convert returns a ZIP containing
    the converted HTML.
    """

    # Send POST request to /convert containing markdown file
    file_path = resources / "test.md"
    data = {
        "files[]": (file_path.open("rb"), file_path.name)
    }
    response = client.post(
        "/convert", 
        data=data,
        content_type="multipart/form-data"
    )

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
        assert expected_html_file in zip_file_list, f"{expected_html_file} not found in ZIP"
        html_content = zipf.read(expected_html_file).decode("utf-8")
        assert "<html" in html_content.lower(), "HTML content is missing <html> tag"