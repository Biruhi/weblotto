from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# Database connection configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'youtube_link'
}

# Global variables to store the latest video ID and timestamp
latest_video_id = ''
last_update_time = datetime.now()

# Connect to MySQL
def connect_db():
    connection = mysql.connector.connect(**db_config)
    return connection

# Fetch the latest video ID from MySQL
def fetch_latest_video_id():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT video FROM videos ORDER BY id DESC LIMIT 1")  # Fetch the latest video ID
    data = cursor.fetchone()  # Get one row
    connection.close()
    return data[0] if data else ''

# Function to continuously fetch the latest video ID every minute
def update_video_id_periodically():
    global latest_video_id, last_update_time
    while True:
        latest_video_id = fetch_latest_video_id()
        last_update_time = datetime.now()
        time.sleep(60)  # Fetch video ID every minute

# Start the background thread to fetch the latest video ID
def start_video_update_manager():
    thread = threading.Thread(target=update_video_id_periodically)
    thread.start()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Handle form submission
        user_input = request.form.get('user_input')
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO videos (video) VALUES (%s)", (user_input,))
        connection.commit()
        connection.close()

    # Pass the latest video ID and timestamp to the frontend
    return render_template('index.html', random_data=latest_video_id, last_update_time=last_update_time)

@app.route('/get_latest_data', methods=['GET'])
def get_latest_data():
    """API endpoint to fetch the latest video ID and timestamp."""
    return jsonify({
        'random_data': latest_video_id,
        'last_update_time': last_update_time.isoformat()  # Pass the last update time
    })

if __name__ == '__main__':
    # Start the video update manager thread
    start_video_update_manager()
    
    # Run the Flask app
    app.run(debug=True)
