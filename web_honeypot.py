#LIBRARIES
import logging
from flask import Flask, render_template, request, redirect, url_for
from logging.handlers import RotatingFileHandler

#LOGGING FORMAT
logging_format = logging.Formatter('%(asctime)s %(message)s')


#HTTP LOGGER
success_logger=logging.getLogger('success_logger')
success_logger.setLevel(logging.INFO)
success_logger.propagate=False
success_handler = RotatingFileHandler('Web_Success.log',maxBytes=2000,backupCount=5)
success_handler.setFormatter(logging_format)
success_logger.addHandler(success_handler)

failed_logger=logging.getLogger('failed_logger')
failed_logger.setLevel(logging.INFO)
failed_logger.propagate=False
failed_handler = RotatingFileHandler('Web_Failed.log',maxBytes=2000,backupCount=5)
failed_handler.setFormatter(logging_format)
failed_logger.addHandler(failed_handler)


#BASELINE HONEYPOT
app = Flask(__name__)
def web_honeypot(input_username = 'admin',  input_password = 'admin'):


    @app.route('/')

    def index():
        return render_template('wp-admin.html')
    
    @app.route('/wp-admin-login', methods = ['POST'])

    def login():
        username = request.form['username']
        password = request.form['password']

        ip_address = request.remote_addr

        if input_username and input_password and username == input_username and password == input_password:
            success_logger.info(f"- Successful Login - IP: {ip_address} | Username: {username} | Password: {password}")
            return "YOU GOT ACCESS!!!"
        else:
            failed_logger.info(f"- Failed Login Attempt - IP: {ip_address} | Username: {username} | Password: {password}")
            return "Invalid username or password. Please Try Again!"
    return app



def run_web_honeypot(port=8000, input_username='admin', input_password = 'admin'):
    run_whp_app =  web_honeypot(input_username, input_password)
    run_whp_app.run(debug=False,port=port, host="0.0.0.0")
    
    return run_whp_app

#run_web_honeypot(port=8000,input_username= 'admin',  input_password= 'admin')  #Testing