import os
import json
import subprocess
import shlex
import dns.resolver
import google.generativeai as genai
import sublist3r
import paramiko
import nmap


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {'stdout': result.stdout, 'stderr': None}
        else:
            error_output = result.stdout + "\n" + result.stderr
            return {'stdout': None, 'stderr': error_output.strip()}
    except subprocess.TimeoutExpired:
        return {'stdout': None, 'stderr': 'Error: Command timed out after 30 seconds.'}
    except Exception as e:
        return {'stdout': None, 'stderr': f"An unexpected error occurred: {str(e)}"}

def perform_ping_scan(target):
    sanitized_target = shlex.quote(target)
    command = ['ping', '-c', '4', sanitized_target]
    return run_command(command)

def perform_traceroute_scan(target):
    sanitized_target = shlex.quote(target)
    command = ['traceroute', sanitized_target]
    return run_command(command)

def perform_nslookup_scan(target):
    sanitized_target = shlex.quote(target)
    command = ['nslookup', sanitized_target]
    return run_command(command)

def perform_nmap_scan(target, scan_type):
    nm = nmap.PortScanner()
    scan_args = {
        'ping_scan': '-sn',
        'quick_scan': '-T4 -F',
        'intense_scan': '-T4 -A -v',
        'udp_scan': '-sU',
        'vuln_scan': '--script vuln'
    }
    arguments = scan_args.get(scan_type)
    if not arguments:
        return {'stdout': None, 'stderr': f"Invalid scan type: {scan_type}"}

    try:
        nm.scan(hosts=str(target), arguments=arguments)
        output_string = ""
        for host in nm.all_hosts():
            output_string += f"----------------------------------------------------\n"
            output_string += f"Host : {host} ({nm[host].hostname()})\n"
            output_string += f"State : {nm[host].state()}\n"
            for proto in nm[host].all_protocols():
                output_string += f"----------\n"
                output_string += f"Protocol : {proto}\n"
                ports = nm[host][proto].keys()
                for port in sorted(ports):
                    state = nm[host][proto][port]['state']
                    name = nm[host][proto][port]['name']
                    product = nm[host][proto][port].get('product', '')
                    version = nm[host][proto][port].get('version', '')
                    extrainfo = nm[host][proto][port].get('extrainfo', '')
                    script_output = nm[host][proto][port].get('script', {})
                    output_string += f"port : {port}\tstate : {state}\tname : {name}\tproduct : {product} {version} {extrainfo}\n"
                    if script_output:
                        output_string += "Script output:\n"
                        for script_id, data in script_output.items():
                            output_string += f"  {script_id}:\n{data}\n"
        if not output_string:
            return {'stdout': nm.csv(), 'stderr': "No open ports or specific results found. Raw Nmap output provided."}
        return {'stdout': output_string, 'stderr': None}
    except nmap.PortScannerError as e:
        return {'stdout': None, 'stderr': f"Nmap error: {str(e)}. Is Nmap installed on the system?"}
    except Exception as e:
        return {'stdout': None, 'stderr': f"An unexpected error occurred: {str(e)}"}
def get_network_device_info(device_type, host, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, timeout=10)
        if device_type == 'mikrotik':
            command = "/export"
        elif device_type == 'cisco_ios':
            command = "show running-config"
        else:
            return {"status": "error", "message": f"Unsupported device type: {device_type}"}
        stdin, stdout, stderr = client.exec_command(command)
        config_data = stdout.read().decode('utf-8')
        error_data = stderr.read().decode('utf-8')
        client.close()
        if error_data:
            return {"status": "error", "message": error_data}
        return {"status": "completed", "config_data": config_data}
    except paramiko.AuthenticationException:
        return {"status": "error", "message": "Authentication failed. Please check username and password."}
    except paramiko.SSHException as e:
        return {"status": "error", "message": f"SSH connection error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

def run_domain_scan(target_domain, scan_type):
    if scan_type == 'subdomain_enum':
        try:
            subdomains = sublist3r.main(target_domain, 40, '', ports=None, silent=True, verbose=False, enable_bruteforce=False, engines=None)
            return {"status": "completed", "results": subdomains}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "Unsupported scan type for domain."}

def run_email_analysis(target_email):
    # Placeholder for email analysis logic
    print(f"Performing email analysis for {target_email}")
    return {"status": "completed", "results": f"Email analysis for {target_email} completed (placeholder)."}

def analyze_results_with_gemini(api_key, results):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        prompt = f"""
        You are a cybersecurity expert and network analyst.
        Your task is to analyze the following network scan results and provide a professional and easy-to-understand report.

        Raw Scan Results:
        ---
        {results}
        ---

        Your report should include:
        1.  **Executive Summary:** A brief summary of the most important findings.
        2.  **Detailed Findings:** A detailed explanation of each finding, including potential risks and their impact.
        3.  **Recommendations:** Concrete steps that can be taken to remediate identified security issues.
        4.  **Risk Level:** Classification of the risk level (Critical, High, Medium, Low) for each finding.

        Use Markdown format for your report.
        """
        response = model.generate_content(prompt)
        return {'status': 'completed', 'analysis': response.text}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}