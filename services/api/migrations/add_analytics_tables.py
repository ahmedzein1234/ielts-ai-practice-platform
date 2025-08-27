"""
Database migration script to create analytics tables for Phase 4.
"""

import sqlite3
import json
from datetime import datetime, timedelta
import uuid

def create_analytics_tables():
    """Create all analytics-related tables."""
    
    # Connect to the database
    conn = sqlite3.connect('ielts_platform.db')
    cursor = conn.cursor()
    
    try:
        # Create analytics_events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT,
                event_type TEXT NOT NULL,
                event_name TEXT NOT NULL,
                event_data TEXT,
                page_url TEXT,
                referrer TEXT,
                user_agent TEXT,
                ip_address TEXT,
                device_type TEXT,
                browser TEXT,
                os TEXT,
                screen_resolution TEXT,
                duration_ms INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create performance_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                module_type TEXT,
                skill_area TEXT,
                difficulty_level TEXT,
                metadata TEXT,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create predictive_models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_models (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                model_type TEXT NOT NULL,
                model_version TEXT,
                predicted_value REAL NOT NULL,
                confidence_score REAL,
                prediction_interval_lower REAL,
                prediction_interval_upper REAL,
                actual_value REAL,
                accuracy_score REAL,
                input_features TEXT,
                target_date DATE,
                predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                validated_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create comparative_analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparative_analyses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                comparison_group TEXT NOT NULL,
                user_percentile REAL,
                group_average REAL,
                group_median REAL,
                group_std_dev REAL,
                user_rank INTEGER,
                total_in_group INTEGER,
                comparison_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create custom_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                report_type TEXT NOT NULL,
                filters TEXT,
                metrics TEXT,
                visualizations TEXT,
                is_scheduled BOOLEAN DEFAULT FALSE,
                schedule_frequency TEXT,
                export_format TEXT,
                email_recipients TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                last_generated DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create report_executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_executions (
                id TEXT PRIMARY KEY,
                custom_report_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                data_points INTEGER,
                file_size_bytes INTEGER,
                file_url TEXT,
                error_message TEXT,
                error_details TEXT,
                FOREIGN KEY (custom_report_id) REFERENCES custom_reports (id)
            )
        ''')
        
        # Create analytics_dashboards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_dashboards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                is_default BOOLEAN DEFAULT FALSE,
                layout_config TEXT,
                widget_configs TEXT,
                default_filters TEXT,
                refresh_interval INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create data_exports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_exports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                export_type TEXT NOT NULL,
                format TEXT NOT NULL,
                filters TEXT,
                fields TEXT,
                date_range TEXT,
                status TEXT NOT NULL,
                progress_percentage REAL DEFAULT 0.0,
                file_url TEXT,
                file_size_bytes INTEGER,
                requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type ON analytics_events (event_type)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_user_id ON performance_metrics (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_recorded_at ON performance_metrics (recorded_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_metric_name ON performance_metrics (metric_name)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictive_models_user_id ON predictive_models (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictive_models_predicted_at ON predictive_models (predicted_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_reports_user_id ON custom_reports (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_reports_created_at ON custom_reports (created_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_exports_user_id ON data_exports (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_exports_requested_at ON data_exports (requested_at)')
        
        # Insert sample data
        insert_sample_data(cursor)
        
        conn.commit()
        print("✅ Analytics tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating analytics tables: {e}")
        raise
    finally:
        conn.close()

def insert_sample_data(cursor):
    """Insert sample analytics data."""
    
    # Get a sample user ID
    cursor.execute("SELECT id FROM users LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("⚠️ No users found, skipping sample data insertion")
        return
    
    user_id = result[0]
    
    # Sample analytics events
    sample_events = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': str(uuid.uuid4()),
            'event_type': 'page_view',
            'event_name': 'Dashboard Visit',
            'event_data': json.dumps({'page': 'dashboard', 'duration': 120}),
            'page_url': '/dashboard',
            'device_type': 'desktop',
            'browser': 'Chrome',
            'os': 'Windows',
            'timestamp': datetime.now() - timedelta(days=1)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': str(uuid.uuid4()),
            'event_type': 'assessment_attempt',
            'event_name': 'Reading Test Started',
            'event_data': json.dumps({'test_type': 'reading', 'difficulty': 'medium'}),
            'page_url': '/assessments/reading',
            'device_type': 'desktop',
            'browser': 'Chrome',
            'os': 'Windows',
            'timestamp': datetime.now() - timedelta(hours=2)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': str(uuid.uuid4()),
            'event_type': 'content_interaction',
            'event_name': 'Video Watched',
            'event_data': json.dumps({'content_id': 'video_001', 'duration': 300}),
            'page_url': '/content/video/001',
            'device_type': 'mobile',
            'browser': 'Safari',
            'os': 'iOS',
            'timestamp': datetime.now() - timedelta(hours=1)
        }
    ]
    
    for event in sample_events:
        cursor.execute('''
            INSERT INTO analytics_events 
            (id, user_id, session_id, event_type, event_name, event_data, page_url, 
             device_type, browser, os, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['id'], event['user_id'], event['session_id'], event['event_type'],
            event['event_name'], event['event_data'], event['page_url'],
            event['device_type'], event['browser'], event['os'], event['timestamp']
        ))
    
    # Sample performance metrics
    sample_metrics = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'metric_name': 'reading_score',
            'metric_value': 7.5,
            'metric_unit': 'band',
            'module_type': 'reading',
            'skill_area': 'comprehension',
            'difficulty_level': 'medium',
            'recorded_at': datetime.now() - timedelta(days=7)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'metric_name': 'listening_score',
            'metric_value': 6.5,
            'metric_unit': 'band',
            'module_type': 'listening',
            'skill_area': 'understanding',
            'difficulty_level': 'medium',
            'recorded_at': datetime.now() - timedelta(days=5)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'metric_name': 'writing_score',
            'metric_value': 6.0,
            'metric_unit': 'band',
            'module_type': 'writing',
            'skill_area': 'task_achievement',
            'difficulty_level': 'medium',
            'recorded_at': datetime.now() - timedelta(days=3)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'metric_name': 'speaking_score',
            'metric_value': 7.0,
            'metric_unit': 'band',
            'module_type': 'speaking',
            'skill_area': 'fluency',
            'difficulty_level': 'medium',
            'recorded_at': datetime.now() - timedelta(days=1)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'metric_name': 'study_time',
            'metric_value': 120,
            'metric_unit': 'minutes',
            'module_type': 'general',
            'skill_area': 'engagement',
            'difficulty_level': 'medium',
            'recorded_at': datetime.now() - timedelta(hours=2)
        }
    ]
    
    for metric in sample_metrics:
        cursor.execute('''
            INSERT INTO performance_metrics 
            (id, user_id, metric_name, metric_value, metric_unit, module_type, 
             skill_area, difficulty_level, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric['id'], metric['user_id'], metric['metric_name'], metric['metric_value'],
            metric['metric_unit'], metric['module_type'], metric['skill_area'],
            metric['difficulty_level'], metric['recorded_at']
        ))
    
    # Sample predictive models
    sample_predictions = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'model_type': 'score_prediction',
            'model_version': '1.0',
            'predicted_value': 7.2,
            'confidence_score': 0.85,
            'prediction_interval_lower': 6.8,
            'prediction_interval_upper': 7.6,
            'target_date': datetime.now() + timedelta(days=30),
            'predicted_at': datetime.now() - timedelta(days=1)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'model_type': 'improvement_rate',
            'model_version': '1.0',
            'predicted_value': 0.15,
            'confidence_score': 0.78,
            'prediction_interval_lower': 0.10,
            'prediction_interval_upper': 0.20,
            'target_date': datetime.now() + timedelta(days=14),
            'predicted_at': datetime.now() - timedelta(days=2)
        }
    ]
    
    for prediction in sample_predictions:
        cursor.execute('''
            INSERT INTO predictive_models 
            (id, user_id, model_type, model_version, predicted_value, confidence_score,
             prediction_interval_lower, prediction_interval_upper, target_date, predicted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction['id'], prediction['user_id'], prediction['model_type'],
            prediction['model_version'], prediction['predicted_value'],
            prediction['confidence_score'], prediction['prediction_interval_lower'],
            prediction['prediction_interval_upper'], prediction['target_date'],
            prediction['predicted_at']
        ))
    
    # Sample custom reports
    sample_reports = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Weekly Progress Report',
            'description': 'Comprehensive weekly progress analysis',
            'report_type': 'user_progress',
            'filters': json.dumps({'date_range': 'last_7_days'}),
            'metrics': json.dumps(['reading_score', 'listening_score', 'study_time']),
            'visualizations': json.dumps(['line_chart', 'bar_chart']),
            'is_scheduled': True,
            'schedule_frequency': 'weekly',
            'export_format': 'pdf',
            'is_active': True
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Performance Analysis',
            'description': 'Detailed performance breakdown by module',
            'report_type': 'performance_analysis',
            'filters': json.dumps({'modules': ['reading', 'listening', 'writing', 'speaking']}),
            'metrics': json.dumps(['score_trends', 'improvement_rate', 'weak_areas']),
            'visualizations': json.dumps(['radar_chart', 'heatmap']),
            'is_scheduled': False,
            'export_format': 'excel',
            'is_active': True
        }
    ]
    
    for report in sample_reports:
        cursor.execute('''
            INSERT INTO custom_reports 
            (id, user_id, name, description, report_type, filters, metrics, visualizations,
             is_scheduled, schedule_frequency, export_format, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report['id'], report['user_id'], report['name'], report['description'],
            report['report_type'], report['filters'], report['metrics'],
            report['visualizations'], report['is_scheduled'], report['schedule_frequency'],
            report['export_format'], report['is_active']
        ))
    
    # Sample analytics dashboard
    sample_dashboard = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'name': 'My Learning Dashboard',
        'description': 'Personalized learning analytics dashboard',
        'is_default': True,
        'layout_config': json.dumps({
            'grid': '2x2',
            'widgets': [
                {'type': 'score_chart', 'position': [0, 0], 'size': [1, 1]},
                {'type': 'progress_ring', 'position': [0, 1], 'size': [1, 1]},
                {'type': 'activity_timeline', 'position': [1, 0], 'size': [1, 1]},
                {'type': 'insights_panel', 'position': [1, 1], 'size': [1, 1]}
            ]
        }),
        'widget_configs': json.dumps({
            'score_chart': {'time_range': '30_days', 'modules': ['reading', 'listening', 'writing', 'speaking']},
            'progress_ring': {'target_score': 7.5, 'current_score': 6.8},
            'activity_timeline': {'days': 7, 'activities': ['study', 'tests', 'practice']},
            'insights_panel': {'max_insights': 5, 'categories': ['improvement', 'weaknesses', 'recommendations']}
        }),
        'default_filters': json.dumps({'date_range': 'last_30_days'}),
        'refresh_interval': 300
    }
    
    cursor.execute('''
        INSERT INTO analytics_dashboards 
        (id, user_id, name, description, is_default, layout_config, widget_configs,
         default_filters, refresh_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        sample_dashboard['id'], sample_dashboard['user_id'], sample_dashboard['name'],
        sample_dashboard['description'], sample_dashboard['is_default'],
        sample_dashboard['layout_config'], sample_dashboard['widget_configs'],
        sample_dashboard['default_filters'], sample_dashboard['refresh_interval']
    ))
    
    # Sample data exports
    sample_exports = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'export_type': 'performance_data',
            'format': 'csv',
            'filters': json.dumps({'date_range': 'last_30_days'}),
            'fields': json.dumps(['score', 'module', 'date', 'duration']),
            'status': 'completed',
            'progress_percentage': 100.0,
            'file_url': '/exports/performance_data_001.csv',
            'file_size_bytes': 2048,
            'completed_at': datetime.now() - timedelta(hours=1)
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'export_type': 'study_analytics',
            'format': 'excel',
            'filters': json.dumps({'modules': ['reading', 'listening']}),
            'fields': json.dumps(['study_time', 'scores', 'improvements']),
            'status': 'pending',
            'progress_percentage': 0.0
        }
    ]
    
    for export in sample_exports:
        cursor.execute('''
            INSERT INTO data_exports 
            (id, user_id, export_type, format, filters, fields, status, progress_percentage,
             file_url, file_size_bytes, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            export['id'], export['user_id'], export['export_type'], export['format'],
            export['filters'], export['fields'], export['status'], export['progress_percentage'],
            export.get('file_url'), export.get('file_size_bytes'), export.get('completed_at')
        ))
    
    print("✅ Sample analytics data inserted successfully!")

if __name__ == "__main__":
    create_analytics_tables()
