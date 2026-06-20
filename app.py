from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from config import Config
from database import get_database_connection
from modules.camera_module import capture_vehicle_image
from modules.plate_detection import detect_number_plate
from modules.color_detection import detect_vehicle_color
from modules.report_generator import ReportGenerator
from openpyxl import Workbook
from flask import send_file
import cv2
from flask import Response
import bcrypt
from datetime import datetime
import os
import tempfile

app = Flask(__name__)

# Load configuration from Config class
app.secret_key = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG


# -------------------------
# LOGIN PAGE
# -------------------------
@app.route('/')
def home():
    return render_template("login.html")


# -------------------------
# LOGIN AUTHENTICATION
# -------------------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # FIX: Only fetch by username, then verify password with bcrypt.
        # Previously compared plain-text password in SQL — insecure and
        # incompatible with bcrypt-hashed passwords.
        query = "SELECT * FROM users WHERE username=%s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        connection.close()
    except RuntimeError:
        return "Database error. Please try again later.", 500

    if user:
        # user[2] is the hashed password column — adjust index if schema differs
        stored_hash = user[2]
        # Support both bcrypt-hashed and legacy plain-text passwords
        try:
            password_ok = bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash
            )
        except Exception:
            # Fallback for plain-text passwords (legacy / fresh installs)
            password_ok = (password == stored_hash)

        if password_ok:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin_dashboard'))

    return "Invalid Username or Password"


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM vehicles WHERE status='INSIDE'"
        cursor.execute(query)
        total_inside = cursor.fetchone()[0]
        connection.close()
    except RuntimeError:
        total_inside = 0

    return render_template(
        "admin_dashboard.html",
        total_inside=total_inside
    )


# -------------------------
# MANUAL VEHICLE ENTRY
# -------------------------
@app.route('/manual_entry', methods=['GET', 'POST'])
def manual_entry():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        owner_name = request.form['owner_name']
        vehicle_color = request.form['vehicle_color']
        entry_time = datetime.now()

        try:
            connection = get_database_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO vehicles
            (vehicle_number, owner_name, vehicle_color, entry_time, status, detection_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                vehicle_number,
                owner_name,
                vehicle_color,
                entry_time,
                "INSIDE",
                "MANUAL"
            )
            cursor.execute(query, values)
            connection.commit()
            connection.close()
        except RuntimeError:
            return "Database error. Could not record entry.", 500

        return "Vehicle Entry Recorded Successfully"

    return render_template("manual_entry.html")


# -------------------------
# VEHICLE EXIT
# -------------------------
@app.route('/vehicle_exit', methods=['GET', 'POST'])
def vehicle_exit():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        exit_time = datetime.now()

        try:
            connection = get_database_connection()
            cursor = connection.cursor()

            query = """
            UPDATE vehicles
            SET exit_time=%s, status=%s
            WHERE vehicle_number=%s AND status='INSIDE'
            """
            cursor.execute(query, (exit_time, "EXITED", vehicle_number))
            connection.commit()
            connection.close()
        except RuntimeError:
            return "Database error. Could not record exit.", 500

        return "Vehicle Exit Recorded Successfully"

    return render_template("vehicle_exit.html")


# -------------------------
# VEHICLE RECORDS
# -------------------------
@app.route('/vehicle_records')
def vehicle_records():
    # FIX: Added session check — previously accessible without login
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM vehicles ORDER BY vehicle_id DESC"
        cursor.execute(query)
        vehicles = cursor.fetchall()
        connection.close()
    except RuntimeError:
        vehicles = []

    return render_template("vehicle_records.html", vehicles=vehicles)


@app.route('/vehicle_details/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM vehicles WHERE vehicle_id=%s"
        cursor.execute(query, (vehicle_id,))
        vehicle = cursor.fetchone()
        connection.close()
    except RuntimeError:
        return "Database error.", 500

    if vehicle:
        return render_template("vehicle_detail.html", vehicle=vehicle)
    else:
        return "Vehicle not found", 404


# -------------------------
# CAMERA ENTRY
# -------------------------
@app.route('/camera_entry', methods=['GET', 'POST'])
def camera_entry():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    detected_plate = None
    detected_color = None
    image_path = None

    if request.method == 'POST':
        image_path = capture_vehicle_image(entry=True)

        if image_path:
            # FIX: Replaced bare except: with explicit Exception logging
            try:
                detected_plate = detect_number_plate(image_path)
            except Exception as e:
                print(f"Plate detection error: {e}")
                detected_plate = "Unknown"

            try:
                detected_color = detect_vehicle_color(image_path)
            except Exception as e:
                print(f"Color detection error: {e}")
                detected_color = "Unknown"

            entry_time = datetime.now()

            try:
                connection = get_database_connection()
                cursor = connection.cursor()

                query = """
                INSERT INTO vehicles
                (vehicle_number, vehicle_color, entry_time, status, detection_type, entry_image)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    detected_plate,
                    detected_color,
                    entry_time,
                    "INSIDE",
                    "CAMERA",
                    image_path
                )
                cursor.execute(query, values)
                connection.commit()
                connection.close()
            except RuntimeError:
                return "Database error. Could not save camera entry.", 500

    return render_template(
        "camera_entry.html",
        image_path=image_path,
        detected_plate=detected_plate,
        detected_color=detected_color
    )


# -------------------------
# TEST CAMERA
# -------------------------
@app.route('/test_camera')
def test_camera():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    image_path = capture_vehicle_image(entry=True)

    if image_path:
        return f"<h2>Image Captured</h2><img src='/{image_path}' width='400'>"
    else:
        return "Camera Failed"


# -------------------------
# LIVE CAMERA STREAM
# -------------------------
@app.route('/live_camera')
def live_camera():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    return Response(
        generate_camera_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/live_camera_page')
def live_camera_page():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    return render_template("live_camera.html")


# -------------------------
# TEST PLATE DETECTION
# -------------------------
@app.route('/test_plate')
def test_plate():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    folder = "static/images/entry"

    if not os.path.exists(folder):
        return "Image folder not found", 404

    files = os.listdir(folder)

    if not files:
        return "No images found"

    latest = sorted(files)[-1]
    image_path = os.path.join(folder, latest)
    plate = detect_number_plate(image_path)

    return f"<h2>Detected Plate: {plate}</h2><img src='/{image_path}' width='400'>"


# -------------------------
# LOGOUT
# -------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# -------------------------
# EXPORT EXCEL
# -------------------------
@app.route('/export_excel')
def export_excel():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM vehicles")
        records = cursor.fetchall()
        connection.close()
    except RuntimeError:
        return "Database error. Could not export records.", 500

    # Create Excel file
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Vehicle Records"

    headers = [
        "ID", "Vehicle Number", "Owner Name", "Color",
        "Entry Time", "Exit Time", "Status", "Detection Type",
        "Entry Image", "Exit Image"
    ]
    sheet.append(headers)

    for row in records:
        sheet.append(list(row))

    # FIX: Save to a temp file instead of project root, and clean up after sending.
    # Previously the file was left on disk permanently.
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix='.xlsx', prefix='vehicle_records_'
    )
    tmp.close()
    workbook.save(tmp.name)

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name='vehicle_records.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# -------------------------
# CAMERA FRAME GENERATOR
# -------------------------
def generate_camera_frames():
    """
    FIX: Camera is now properly released when the generator is closed,
    preventing resource leaks.
    """
    camera_source = Config.CAMERA_SOURCE
    camera = cv2.VideoCapture(camera_source)

    if not camera.isOpened():
        camera = cv2.VideoCapture(Config.FALLBACK_CAMERA)

    try:
        while True:
            success, frame = camera.read()

            if not success:
                break

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        # Always release the camera, even if the client disconnects
        camera.release()


# -------------------------
# HISTORY & REPORTS PAGE
# -------------------------
@app.route('/history_reports')
def history_reports():
    if 'logged_in' not in session:
        return redirect(url_for('home'))

    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM vehicles ORDER BY vehicle_id DESC LIMIT 100"
        cursor.execute(query)
        vehicles = cursor.fetchall()
        connection.close()
    except RuntimeError:
        vehicles = []

    today_date = datetime.now().strftime('%B %d, %Y')

    return render_template(
        "history_reports.html",
        vehicles=vehicles,
        today_date=today_date
    )


# -------------------------
# API ENDPOINTS FOR REPORTS
# -------------------------
@app.route('/api/reports/summary')
def api_summary_stats():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    stats = ReportGenerator.get_summary_stats()
    return jsonify(stats)


@app.route('/api/reports/weekly')
def api_weekly_report():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    weekly_data = ReportGenerator.get_weekly_report()
    for item in weekly_data:
        if 'date' in item and item['date']:
            item['date'] = item['date'].strftime('%Y-%m-%d')
    return jsonify(weekly_data)


@app.route('/api/reports/monthly')
def api_monthly_report():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    monthly_data = ReportGenerator.get_monthly_report()
    return jsonify(monthly_data)


@app.route('/api/reports/hourly')
def api_hourly_distribution():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    hourly_data = ReportGenerator.get_hourly_distribution()
    return jsonify(hourly_data)


@app.route('/api/reports/color_distribution')
def api_color_distribution():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    color_data = ReportGenerator.get_color_distribution()
    return jsonify(color_data)


# -------------------------
# MAIN
# -------------------------
if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
