
import os
import re
from flask import Flask, request, render_template
from markupsafe import escape

app = Flask(__name__)

# Configure the template directory relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.template_folder = os.path.join(BASE_DIR, 'templates')

# Planet information
planet_data = {
    "Mercury": "The smallest and fastest planet in the Solar System.",
    "Venus": "The hottest planet in the Solar System.",
    "Earth": "Our home planet.",
    "Mars": "The Red Planet.",
    "Jupiter": "The largest planet in the Solar System."
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        planet = request.form.get('planet', '').strip()

        # Validate empty input
        if not planet:
            return '<h2>Please enter a planet name.</h2>'

        # Preserve the challenge's expected script-tag blocking behaviour
        if re.search(r'<\s*script\b', planet, re.IGNORECASE):
            return '<h2>Blocked</h2></p>'

        # Escape user input to prevent HTML injection
        sanitized_planet = escape(planet)

        return render_template(
            'details.html',
            planet=sanitized_planet,
            info=get_planet_info(planet)
        )

    return render_template('index.html')


def get_planet_info(planet):
    return planet_data.get(planet, 'Unknown planet.')


if __name__ == '__main__':
    app.run()
