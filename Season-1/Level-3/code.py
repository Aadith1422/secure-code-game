# Welcome to Secure Code Game Season-1/Level-3!

# You know how to play by now, good luck!

import os
from flask import Flask, request

### Unrelated to the exercise -- Starts here -- Please ignore
app = Flask(__name__)
@app.route("/")
def source():
    TaxPayer('foo', 'bar').get_tax_form_attachment(request.args["input"])
    TaxPayer('foo', 'bar').get_prof_picture(request.args["input"])
### Unrelated to the exercise -- Ends here -- Please ignore

class TaxPayer:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.prof_picture = None
        self.tax_form_attachment = None

    # returns the path of an optional profile picture that users can set
    def get_prof_picture(self, path=None):
        # setting a profile picture is optional
        if not path:
            return None

        base_dir = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
        requested_path = os.path.realpath(os.path.join(base_dir, path))

        # Allow access to files only within the current directory and its subdirectories
        if os.path.commonpath([base_dir, requested_path]) != base_dir:
            return None

        if not os.path.isfile(requested_path):
            return None

        with open(requested_path, 'rb') as picture:
            self.prof_picture = bytearray(picture.read())

        return requested_path
        
      
    # returns the path of an attached tax form that every user should submit
    def get_tax_form_attachment(self, path=None):

        if not path:
            raise Exception("Error: Tax form is required for all users")

        base_dir = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
        requested_path = os.path.realpath(path)

        # Allow access to files only within the current directory and its subdirectories
        if os.path.commonpath([base_dir, requested_path]) != base_dir:
            return None

        if not os.path.isfile(requested_path):
            return None

        with open(requested_path, 'rb') as tax_form:
            tax_data = bytearray(tax_form.read())

        return requested_path

