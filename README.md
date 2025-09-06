<p align="center">
  <img src="flaskr/static/logo.png" alt="Logo" width="150">
</p>
      
<h1 align="center">Docovert</h1>

<p align="center">
  <img src="https://img.shields.io/badge/google%20gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white" alt="gemini">
  <img src="https://img.shields.io/badge/Microsoft_Word-2B579A?style=for-the-badge&logo=microsoft-word&logoColor=white" alt="ms word">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="python">
  <img src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white" alt="flask">
  <img src="https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white" alt="bootstrap">
  <img src="https://img.shields.io/badge/NPM-%23CB3837.svg?style=for-the-badge&logo=npm&logoColor=white" alt="npm">
</p>

A simple web application to convert one or more .docx files into self-contained HTML files, with all images embedded directly into the document. The resulting files are bundled into a single .zip archive for easy download.

> [!WARNING]  
> This project is 100% vide-coded and not suitable for production.

![screenshot 1](demo.png)

## Features

- **Drag-and-Drop Interface**: Easily add files by dragging them onto the upload area.
- **Multiple File Uploads**: Select and convert multiple .docx files at once.
- Secure Backend Conversion: Uses the powerful Pandoc engine in a secure, isolated process.
- **Self-Contained HTML**: All images from the document are embedded as Base64 data directly into the HTML file, ensuring there are no broken links.
- **Zipped Archive**: The converted HTML files are delivered in a single, convenient .zip archive.
- **Clean & Responsive UI**: Built with Tailwind CSS for a modern look on any device.

## Core Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **Conversion Engine**: Pandoc

## Prerequisites

Ensure the following tools are installed:

- Python 3.12+
- uv
- Pandoc
- make
- node

## Setup and Installation

Follow these steps to get the application running locally.

1. Clone the Repository

```sh
git clone https://noahhefner/docovert.git
cd docovert
```

2. Install dependencies

```sh
make setup
```

3. Run the Application

```sh
make run
```

4. Access the Web App

Navigate to `http://localhost:5000` in a web browser.

## Run With Docker

1. Build the Docker image

```sh
make build
```

2. Run the image

```sh
make run-docker
```

3. Access the Web App

Navigate to `http://localhost:8080` in a web browser.

## Code Formatting

Format code with the `format` target:

```sh
make format
```

## Future Improvements

- Support for more input formats (e.g., `.md`, `.rtf`, `.odt`).
- Add a real-time progress bar for uploads and conversions.
- If only one file is converted, download it directly as `.html` instead of a `.zip`.
