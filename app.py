from datetime import datetime
import os
import time
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session , jsonify
import firebase_admin
from firebase_admin import credentials, auth, db
import threading
import logging
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a secret key for flash messages
CORS(app)
# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate("credential_file_location.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'database_url_from_firebase'
})




# Function to generate random current data between 30 and 60
def generate_current():
    return round(random.uniform(0.03, 0.04), 2)

# Initialize total voltage and total current variables
total_bill = 0
total_current = 0
Kw = 0

# Function to update data every 5 seconds
def update_data():
    global total_current, Kw, total_bill  # Include all variables you modify
    
    while True:
        # Generate random voltage and current data
        current = generate_current()

        # Update total voltage and total current
        total_current += current
        Kw += 230 * current / 1000
        total_bill += 8 * Kw
        
        # Push data to Firebase Realtime Database under 'sensor_data'
        db.reference('sensor_data').set({
            'CURRENT': current,
            'TOTAL_CURRENT': total_current,
            'POWER_IN_Kw': Kw,
            'BILL_IN_RUPEES': total_bill,
        })

        # Sleep for 5 seconds
        time.sleep(5)


        # Function to plot live data


# Start update_data function in a separate thread
update_thread = threading.Thread(target=update_data)
update_thread.daemon = True
update_thread.start()

# Route to serve sensor data as JSON
@app.route('/sensor_data')
def get_sensor_data():
    # Get sensor data from Firebase
    sensor_data = db.reference('sensor_data').get()
    return jsonify(sensor_data)







ref = db.reference('sensor_data')
@app.route('/data')
def get_data():
    # Simulate data generation (replace with your actual Firebase logic)
    current = generate_current()

    # Update total voltage and current (if applicable to your use case)
    # ...

    # Prepare data to send to the client
    data = {
        'CURRENT': current,
        'TOTAL_CURRENT': total_current,
            'POWER_IN_Kw': Kw,
            'BILL_IN_RUPEES': total_bill,
        # Include 'TOTAL_VOLTAGE' and 'TOTAL_CURRENT' if relevant
    }

    return jsonify(data)



import logging
@app.route('/line_chart')
def line_chart():
    # Fetch data from Firebase
    data = ref.get()

    logging.info("Fetched data from Firebase: %s", data)

    if data is None or not data:
        # Data is undefined or empty, handle gracefully
        logging.warning("No data available from Firebase")
        return render_template('error.html', message="No data available")

    # Prepare data for the chart
    labels = list(data.keys())  # Assuming timestamps are keys in the data
    
    # Extract voltage and current data from each entry in the data
    voltage_data = []
    current_data = []
    for entry in data.values():
        if isinstance(entry, dict):
            voltage_data.append(entry.get('VOLTAGE', 0))  # Replace 0 with default value if 'VOLTAGE' key is not present
            current_data.append(entry.get('CURRENT', 0))  # Replace 0 with default value if 'CURRENT' key is not present
        else:
            logging.warning("Invalid data format for entry: %s", entry)

    logging.info("Labels: %s", labels)
    logging.info("Voltage data: %s", voltage_data)
    logging.info("Current data: %s", current_data)

    return render_template('line_chart.html', labels=labels, voltage_data=voltage_data, current_data=current_data)







# Mockup room data
room_data = {
    'Room 1': 'room1.jpg',
    # Add data for other rooms as needed
}

# Mockup socket data
socket_data = {
    'Socket 1': 'socket1.jpg',
    # Add data for other sockets as needed
}

# Mockup Arduino data
arduino_data = {
    'Arduino ESP32': 'arduino_esp32.jpg',
    # Add data for other Arduinos as needed
}

# Variable to store the status of Arduino socket (ON or OFF)
arduino_socket_status = 'OFF'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')







# Define other routes...
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy1')
def privacy1():
    return render_template('privacy1.html')

@app.route('/led')
def led():
    return render_template('led.html')


from flask import redirect

@app.route('/admin_info')
def admin_info():
    return redirect("admin_info.html", code=302)





@app.route('/rooms')
def rooms():
    return render_template('rooms.html', room_data=room_data)

@app.route('/update_led_status')
def update_led_status():
    return render_template('update_led_status.html')
    

@app.route('/room1')
def room1():
    return render_template('room1.html')

@app.route('/room2error')
def room2error():
    return render_template('room2error.html')

@app.route('/room3error')
def room3error():
    return render_template('room3error.html')


@app.route('/socket1')
def socket1():
    return render_template('socket1.html')

@app.route('/socket2')
def socket2():
    return render_template('socket2.html')

@app.route('/switch_socket_status')
def switch_socket_status():
    return render_template('switch_socket_status.html')

@app.route('/chart')
def chart():
    # Your view function logic here
    return render_template('chart.html')

@app.route('/chart1')
def chart1():
    # Your view function logic here
    return render_template('chart1.html')



@app.route('/room/<room_name>')
def room(room_name):
    if room_name in socket_data:
        return render_template('socket1.html', socket_name='Socket 1', arduino_data=arduino_data)
    else:
        return render_template('room_not_found.html', room_name=room_name)
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=email, password=password)

            # Optionally, you can store additional user data in Firebase Realtime Database or Firestore here

            flash('User created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Failed to create user: {e}', 'error')

    messages = list(session.pop('_flashes', []))
    return render_template('signup.html', messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.get_user_by_email(email)
            # Log the user in, perhaps using session cookies or JWT tokens
            flash('Login Successful!', 'success')
            return redirect(url_for('home'))  # Replace 'home' with the appropriate endpoint        
        except Exception as e:
            flash(f'Failed to log in: {e}', 'error')

    messages = list(session.pop('_flashes', []))

    return render_template('login.html', messages=messages)








@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.get_user_by_email(email)  # Check if the user exists
            if user.custom_claims and user.custom_claims.get('admin') == True:
                # User is an admin, authenticate using Firebase
                user = auth.sign_in_with_email_and_password(email, password)
                flash('Admin Login Successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('You are not authorized to access the admin panel.', 'error')
        except auth.AuthError as e:
            error_message = e.detail
            flash(f'Admin Login Failed: {error_message}', 'error')

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Add admin dashboard logic here
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
