import os

# Set up environment variable to be used when wkhtmltopdf (used by pdfkit) runs against Xvfb
# See https://stackoverflow.com/questions/36582594/a-virtual-display-for-ubuntu-server
os.environ.setdefault("DISPLAY", ":1")
