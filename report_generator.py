from datetime import datetime, timedelta
from database import get_database_connection

class ReportGenerator:
    """Generate various reports and analytics for vehicle tracking"""
    
    @staticmethod
    def get_summary_stats():
        """Get overall summary statistics"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        stats = {}
        
        # Total vehicles ever recorded
        cursor.execute("SELECT COUNT(*) as total FROM vehicles")
        stats['total_vehicles'] = cursor.fetchone()['total']
        
        # Currently inside
        cursor.execute("SELECT COUNT(*) as inside FROM vehicles WHERE status='INSIDE'")
        stats['current_inside'] = cursor.fetchone()['inside']
        
        # Total exited
        cursor.execute("SELECT COUNT(*) as exited FROM vehicles WHERE status='EXITED'")
        stats['total_exited'] = cursor.fetchone()['exited']
        
        # Today's entries
        cursor.execute("""
            SELECT COUNT(*) as today_entries 
            FROM vehicles 
            WHERE DATE(entry_time) = CURDATE()
        """)
        stats['today_entries'] = cursor.fetchone()['today_entries']
        
        # Today's exits
        cursor.execute("""
            SELECT COUNT(*) as today_exits 
            FROM vehicles 
            WHERE DATE(exit_time) = CURDATE() AND status='EXITED'
        """)
        stats['today_exits'] = cursor.fetchone()['today_exits']
        
        # Average parking duration (in minutes)
        cursor.execute("""
            SELECT AVG(TIMESTAMPDIFF(MINUTE, entry_time, exit_time)) as avg_duration
            FROM vehicles 
            WHERE exit_time IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_parking_duration'] = round(result['avg_duration'] or 0, 2)
        
        connection.close()
        return stats
    
    @staticmethod
    def get_daily_report(date=None):
        """Get report for a specific day"""
        if date is None:
            date = datetime.now().date()
        
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Entries for the day
        cursor.execute("""
            SELECT COUNT(*) as entries, 
                   COUNT(CASE WHEN detection_type='CAMERA' THEN 1 END) as camera_entries,
                   COUNT(CASE WHEN detection_type='MANUAL' THEN 1 END) as manual_entries
            FROM vehicles 
            WHERE DATE(entry_time) = %s
        """, (date,))
        
        daily_data = cursor.fetchone()
        
        # Exits for the day
        cursor.execute("""
            SELECT COUNT(*) as exits
            FROM vehicles 
            WHERE DATE(exit_time) = %s AND status='EXITED'
        """, (date,))
        
        daily_data['exits'] = cursor.fetchone()['exits']
        
        connection.close()
        return daily_data
    
    @staticmethod
    def get_weekly_report():
        """Get report for the last 7 days"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE(entry_time) as date,
                COUNT(*) as entries,
                COUNT(CASE WHEN status='EXITED' THEN 1 END) as exits
            FROM vehicles 
            WHERE entry_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(entry_time)
            ORDER BY date ASC
        """)
        
        weekly_data = cursor.fetchall()
        connection.close()
        return weekly_data
    
    @staticmethod
    def get_monthly_report():
        """Get report for the current month"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DAY(entry_time) as day,
                COUNT(*) as entries,
                COUNT(CASE WHEN status='EXITED' THEN 1 END) as exits
            FROM vehicles 
            WHERE MONTH(entry_time) = MONTH(CURDATE())
                AND YEAR(entry_time) = YEAR(CURDATE())
            GROUP BY DAY(entry_time)
            ORDER BY day ASC
        """)
        
        monthly_data = cursor.fetchall()
        connection.close()
        return monthly_data
    
    @staticmethod
    def get_hourly_distribution():
        """Get vehicle entry distribution by hour"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                HOUR(entry_time) as hour,
                COUNT(*) as count
            FROM vehicles 
            WHERE entry_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY HOUR(entry_time)
            ORDER BY hour ASC
        """)
        
        hourly_data = cursor.fetchall()
        connection.close()
        return hourly_data
    
    @staticmethod
    def get_color_distribution():
        """Get distribution of vehicle colors"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                vehicle_color,
                COUNT(*) as count
            FROM vehicles 
            WHERE vehicle_color IS NOT NULL AND vehicle_color != 'Unknown'
            GROUP BY vehicle_color
            ORDER BY count DESC
        """)
        
        color_data = cursor.fetchall()
        connection.close()
        return color_data
    
    @staticmethod
    def get_detection_type_stats():
        """Get statistics by detection type (Camera vs Manual)"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                detection_type,
                COUNT(*) as count
            FROM vehicles 
            GROUP BY detection_type
        """)
        
        detection_data = cursor.fetchall()
        connection.close()
        return detection_data
    
    @staticmethod
    def get_date_range_report(start_date, end_date):
        """Get report for a custom date range"""
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE(entry_time) as date,
                COUNT(*) as entries,
                COUNT(CASE WHEN status='EXITED' THEN 1 END) as exits
            FROM vehicles 
            WHERE DATE(entry_time) BETWEEN %s AND %s
            GROUP BY DATE(entry_time)
            ORDER BY date ASC
        """, (start_date, end_date))
        
        range_data = cursor.fetchall()
        connection.close()
        return range_data
