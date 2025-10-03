import json
import os
from flask import render_template, Blueprint, request, jsonify, session, make_response, g
from app.logic import perform_ping_scan, perform_traceroute_scan, perform_nslookup_scan, perform_nmap_scan, run_domain_scan, run_email_analysis, analyze_results_with_gemini, get_network_device_info

bp = Blueprint('main', __name__)

def get_translations(language_code):
    translations_path = os.path.join(bp.root_path, 'static', 'translations.json')
    print(f"DEBUG: get_translations - translations_path: {translations_path}")
    with open(translations_path, 'r') as f:
        translations = json.load(f)
    selected_translations = translations.get(language_code, translations.get('en'))
    print(f"DEBUG: get_translations - language_code: {language_code}, returned translations: {selected_translations}")
    return selected_translations


@bp.before_request
def set_language():
    lang_code = request.cookies.get('lang', 'en')
    print(f"DEBUG: set_language - lang_code from cookie: {lang_code}")
    g.lang = get_translations(lang_code)
    g.lang_code = lang_code
    print(f"DEBUG: set_language - g.lang set to: {g.lang}")

@bp.route('/')
def index():
    print(f"DEBUG: index - g.lang being passed to template: {g.lang}")
    return render_template('index.html', lang=g.lang)

@bp.route('/net_analysis')
def net_analysis_page():
    return render_template('net_analysis.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/run_ping', methods=['POST'])
def run_ping():
    try:
        data = request.json
        target = data.get('target')
        if not target:
            return jsonify({'error': 'Target cannot be empty'}), 400
        
        output = perform_ping_scan(target)
        if output['stderr']:
            return jsonify({'error': output['stderr']})
        else:
            return jsonify({'result': output['stdout']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/run_traceroute', methods=['POST'])
def run_traceroute():
    try:
        data = request.json
        target = data.get('target')
        if not target:
            return jsonify({'error': 'Target cannot be empty'}), 400

        output = perform_traceroute_scan(target)
        if output['stderr']:
            return jsonify({'error': output['stderr']})
        else:
            return jsonify({'result': output['stdout']})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/run_nslookup', methods=['POST'])
def run_nslookup():
    try:
        data = request.json
        target = data.get('target')
        if not target:
            return jsonify({'error': 'Target cannot be empty'}), 400

        output = perform_nslookup_scan(target)
        if output['stderr']:
            return jsonify({'error': output['stderr']})
        else:
            return jsonify({'result': output['stdout']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/run_nmap', methods=['POST'])
def run_nmap():
    try:
        data = request.json
        target = data.get('target')
        scan_type = data.get('scan_type')
        if not all([target, scan_type]):
            return jsonify({'error': 'Target and scan_type are required.'}), 400

        output = perform_nmap_scan(target, scan_type)
        if output['stderr']:
            return jsonify({'error': output['stderr']})
        else:
            return jsonify({'result': output['stdout']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analyze_results', methods=['POST'])
def analyze_results():
    try:
        data = request.json
        api_key = data.get('api_key')
        results = data.get('results')
        if not all([api_key, results]):
            return jsonify({'error': 'API key and results are required.'}), 400

        analysis = analyze_results_with_gemini(api_key, results)
        if analysis['status'] == 'completed':
            return jsonify({'analysis': analysis['analysis']})
        else:
            return jsonify({'error': analysis['message']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/domain_subdomain_target')
def domain_subdomain_target_page():
    return render_template('domain_subdomain_target.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/run_domain_scan', methods=['POST'])
def run_domain_scan_route():
    try:
        data = request.json
        target_domain = data.get('target_domain')
        scan_type = data.get('scan_type')
        if not target_domain:
            return jsonify({'error': 'Target domain cannot be empty'}), 400
        result = run_domain_scan(target_domain, scan_type)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/network_target')
def network_target_page():
    return render_template('network_target.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/log_analyzer')
def log_analyzer_page():
    return render_template('log_analyzer.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/network_device_target', methods=['GET', 'POST'])
def network_device_target():
    if request.method == 'POST':
        data = request.json
        device_type = data.get('device_type')
        host = data.get('host')
        username = data.get('username')
        password = data.get('password')

        if not all([device_type, host, username, password]):
            return jsonify({"status": "error", "message": "Missing required fields."}), 400

        result = get_network_device_info(device_type, host, username, password)
        
        if result['status'] == 'completed':
            result['ai_analysis'] = "Ini adalah placeholder untuk analisis AI. Fitur ini akan diimplementasikan selanjutnya."

        return jsonify(result)

    return render_template('network_device_target.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/domain_subdomain_target', methods=['GET', 'POST'])
def domain_subdomain_target():
    if request.method == 'POST':
        target_domain = request.json['target_domain']
        scan_type = request.json['scan_type']
        result = run_domain_scan(target_domain, scan_type)
        return jsonify(result)
    return render_template('domain_subdomain_target.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/email_target', methods=['GET', 'POST'])
def email_target():
    if request.method == 'POST':
        target_email = request.json['target_email']
        result = run_email_analysis(target_email)
        return jsonify(result)
    return render_template('email_target.html', lang=g.lang, lang_code=g.lang_code)

@bp.route('/set_language/<lang_code>')
def set_language_route(lang_code):
    response = make_response(f"Language set to {lang_code}")
    response.set_cookie('lang', lang_code)
    return response
