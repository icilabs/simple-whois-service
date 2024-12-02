from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import whois
import datetime
import os

DEBUG = os.environ.get('DEBUG', False)

app = Flask(__name__)


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "CheckDomainAvailability API"}
)
app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.route('/CheckDomainAvailability', methods=['POST'])
def check_domain_availability():
    domains = request.json.get('domains', [])
    availability_results = {}

    i = 0
    for domain in domains:
        i += 1
        if i > 10:
            # Don't allow more than 10 domains at a time
            break
        # check if the domain is fqdn or not
        if '.' not in domain:
            is_available = 'Error: Not a valid domain name'
        else:
            try:
                domain_info = whois.whois(domain)
                # A domain is typically available if the expiration date is in the past
                if domain_info.expiration_date:
                    if isinstance(domain_info.expiration_date, list):
                        # Take the first date if there are multiple dates
                        expiration_date = domain_info.expiration_date[0]
                    else:
                        expiration_date = domain_info.expiration_date

                    is_available = expiration_date < datetime.datetime.now()
                else:
                    # If no expiration date, assume the domain is available
                    is_available = True
            except Exception as e:
                # Handle exceptions (like domain not found, etc.)
                is_available = 'Error: ' + str(e)

        availability_results[domain] = is_available

    return jsonify(availability_results)

@app.route('/DomainInfo')
def get_domain_info():
    domain = request.args.get('domain', None)
    if domain is None:
        return jsonify({'error': 'No domain specified'})

    try:
        domain_info = whois.whois(domain)
        return jsonify(domain_info)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/policy')
def send_policy():
    return send_from_directory('static', 'policy.html')


if __name__ == "__main__":
    app.run(
        debug=DEBUG,
    )
