import os

from flask import Flask, render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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

    from . import convert

    app.register_blueprint(convert.bp)

    return app
