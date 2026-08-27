from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """Serve the main web interface."""
    from app import __version__
    return render_template('index.html', version=__version__)
