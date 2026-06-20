# Vehicle Tracking System (VTS)

A comprehensive Flask-based web application for tracking vehicle entry and exit with camera integration, OCR license plate detection, and analytics.

## ✨ Features

- 🔐 **Secure Authentication** - Login system with session management
- 📸 **Camera Integration** - Automatic vehicle detection via webcam or IP camera
- 🔍 **OCR Plate Detection** - Automatic license plate recognition using EasyOCR
- 🎨 **Color Detection** - Automatic vehicle color identification
- ✍️ **Manual Entry** - Fallback manual data entry option
- 📊 **History & Reports** - Comprehensive analytics with interactive charts
  - Daily/Weekly/Monthly statistics
  - Peak hours analysis
  - Vehicle color distribution
  - Entry/Exit trends
- 📥 **Export Functionality** - Download reports in Excel format
- 📱 **Responsive Design** - Modern UI that works on all devices
- 🎬 **Live Camera Feed** - Real-time monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL Server
- Webcam or IP Camera (optional)

### Installation

1. **Clone or navigate to the project directory**
```bash
cd vehicle_tracking_system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**

Copy the example environment file and update with your credentials:
```bash
copy .env.example .env
```

Edit `.env` and configure:
- Database credentials
- Secret key for Flask sessions
- Camera source (if using IP camera)

4. **Set up Database**

Create the MySQL database and tables:
```sql
CREATE DATABASE vehicle_tracking;
USE vehicle_tracking;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicles (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_number VARCHAR(50),
    owner_name VARCHAR(100),
    vehicle_color VARCHAR(50),
    entry_time DATETIME,
    exit_time DATETIME,
    status VARCHAR(20),
    detection_type VARCHAR(20),
    entry_image VARCHAR(255),
    exit_image VARCHAR(255)
);

-- Create default admin user (password: admin123)
INSERT INTO users (username, password) VALUES 
('admin', 'admin123');
```

5. **Run the Application**
```bash
python app.py
```

6. **Access the Application**

Open your browser and navigate to:
```
http://localhost:5000
```

Login with:
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure

```
vehicle_tracking_system/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── database.py               # Database connection handler
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create from .env.example)
├── .env.example             # Environment variables template
│
├── modules/                  # Core modules
│   ├── camera_module.py     # Camera capture functionality
│   ├── plate_detection.py   # OCR license plate detection
│   ├── color_detection.py   # Vehicle color detection
│   └── report_generator.py  # Report and analytics generation
│
├── templates/               # HTML templates
│   ├── layout.html          # Base template with navigation
│   ├── login.html           # Login page
│   ├── admin_dashboard.html # Dashboard
│   ├── camera_entry.html    # Camera-based entry
│   ├── manual_entry.html    # Manual entry form
│   ├── vehicle_exit.html    # Vehicle exit
│   ├── vehicle_records.html # All records table
│   ├── history_reports.html # Analytics and reports
│   └── live_camera.html     # Live camera feed
│
└── static/                  # Static assets
    ├── css/
    │   └── modern.css       # Styling
    ├── js/
    │   ├── main.js          # Common utilities
    │   └── reports.js       # Reports page functionality
    └── images/              # Captured vehicle images
        ├── entry/
        └── exit/
```

## 🎯 Usage

### Dashboard
View real-time statistics of vehicles currently inside and system status.

### Camera Entry
1. Click "Camera Entry" from the navigation
2. Click "Capture" to take a photo
3. System automatically detects license plate and color
4. Record is saved to database

### Manual Entry
1. Click "Manual Entry"
2. Fill in vehicle details manually
3. Submit to record entry

### Vehicle Exit
1. Click "Vehicle Exit"
2. Enter vehicle number
3. Submit to record exit time

### History & Reports
Access comprehensive analytics:
- **Overview Tab**: Summary statistics and key metrics
- **Analytics Tab**: Interactive charts showing trends
- **Detailed Records Tab**: Full table with filtering and search

### Export Reports
Click "Download Excel" to export all records in Excel format.

## 🔧 Configuration

### Database Settings
Edit `.env`:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=vehicle_tracking
```

### Camera Settings
For IP Camera (DroidCam, etc.):
```env
CAMERA_SOURCE=http://192.168.1.5:4747/video
```

For default webcam:
```env
CAMERA_SOURCE=0
```

### Security
Change the secret key in production:
```env
SECRET_KEY=your_very_secure_random_key_here
FLASK_ENV=production
```

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL
- **OCR**: EasyOCR
- **Computer Vision**: OpenCV
- **Charts**: Chart.js
- **UI Framework**: Custom CSS with modern design
- **Icons**: Font Awesome

## 📊 API Endpoints

The application provides RESTful API endpoints for reports:

- `GET /api/reports/summary` - Summary statistics
- `GET /api/reports/weekly` - Weekly trend data
- `GET /api/reports/monthly` - Monthly aggregates
- `GET /api/reports/hourly` - Hourly distribution
- `GET /api/reports/color_distribution` - Color statistics

All endpoints require authentication.

## 🔒 Security Features

- Environment-based configuration (no hardcoded credentials)
- Session-based authentication
- Parameterized SQL queries (SQL injection protection)
- Secure file handling
- CSRF protection ready

## 🐛 Troubleshooting

### Camera not working
- Check camera permissions
- Verify camera source URL in `.env`
- Test with device's default camera (set `CAMERA_SOURCE=0`)

### Database connection error
- Verify MySQL is running
- Check credentials in `.env`
- Ensure database exists

### OCR not detecting plates
- Ensure good lighting
- Position camera for clear view of plates
- Check image quality

## 📝 License

This project is for educational purposes.

## 👨‍💻 Support

For issues and questions, please refer to the documentation or create an issue in the project repository.

---

**Developed with ❤️ for efficient vehicle tracking**
