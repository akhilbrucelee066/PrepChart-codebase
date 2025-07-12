from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Simple file-based storage
CHARTS_FILE = 'charts.json'
PROGRESS_FILE = 'progress.json'

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

def load_charts():
    if os.path.exists(CHARTS_FILE):
        with open(CHARTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_charts(charts):
    with open(CHARTS_FILE, 'w') as f:
        json.dump(charts, f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_progress(chart_id):
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress_data = json.load(f)
                return progress_data.get(str(chart_id), [])
        except json.JSONDecodeError:
            return []
    return []

def save_progress(chart_id, progress_data):
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                try:
                    all_progress = json.load(f)
                except json.JSONDecodeError:
                    all_progress = {}
        else:
            all_progress = {}
        
        all_progress[str(chart_id)] = progress_data
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(all_progress, f, cls=CustomJSONEncoder)
    except Exception as e:
        print(f"Error saving progress: {str(e)}")
        raise

def calculate_weighted_progress(rows, progress_data):
    """Calculate simple progress based on completed tasks"""
    completed_by_difficulty = {'EASY': 0, 'MEDIUM': 0, 'HARD': 0}
    total_by_difficulty = {'EASY': 0, 'MEDIUM': 0, 'HARD': 0}
    
    # Count total tasks for each difficulty
    for row in rows:
        difficulty = str(row[0]).upper()
        total_by_difficulty[difficulty] += 1
    
    # Count completed tasks for each difficulty
    for i, is_completed in enumerate(progress_data):
        if is_completed and i < len(rows):
            difficulty = str(rows[i][0]).upper()
            completed_by_difficulty[difficulty] += 1
    
    # Calculate simple progress percentage
    total_tasks = len(rows)
    completed_tasks = sum(completed_by_difficulty.values())
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        'percentage': round(progress, 2),
        'completed_by_difficulty': completed_by_difficulty,
        'total_by_difficulty': total_by_difficulty
    }

@app.route('/')
def index():
    charts = load_charts()
    return render_template('index.html', charts=charts)

@app.route('/upload_chart', methods=['POST'])
def upload_chart():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        charts = load_charts()
        chart_id = str(len(charts) + 1)
        charts[chart_id] = {
            'name': filename.rsplit('.', 1)[0],
            'filename': filename,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_charts(charts)
        
        flash('Chart uploaded successfully!', 'success')
        return redirect(url_for('index'))

    flash('Invalid file type. Only CSV files are allowed.', 'error')
    return redirect(url_for('index'))

@app.route('/view_chart/<chart_id>')
def view_chart(chart_id):
    charts = load_charts()
    if chart_id not in charts:
        flash('Chart not found', 'error')
        return redirect(url_for('index'))
        
    chart = charts[chart_id]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], chart['filename'])
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Get headers and rows
        headers = df.columns.tolist()
        rows = df.values.tolist()
        
        # Load progress data
        progress_data = load_progress(chart_id)
        
        # Ensure progress data array is long enough
        while len(progress_data) < len(rows):
            progress_data.append(False)
        
        # Calculate weighted progress
        progress_stats = calculate_weighted_progress(rows, progress_data)
        
        return render_template('view_chart.html', 
                             chart=chart,
                             headers=headers,
                             rows=rows,
                             progress=progress_stats['percentage'],
                             progress_data=progress_data,
                             progress_stats=progress_stats,
                             chart_id=chart_id)
    except Exception as e:
        flash(f'Error reading chart: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete_chart/<chart_id>', methods=['POST'])
def delete_chart(chart_id):
    charts = load_charts()
    if chart_id in charts:
        chart = charts[chart_id]
        # Delete the CSV file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], chart['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        # Remove from charts dictionary
        del charts[chart_id]
        save_charts(charts)
        flash('Chart deleted successfully!', 'success')
    else:
        flash('Chart not found', 'error')
    return redirect(url_for('index'))

@app.route('/update_progress/<chart_id>', methods=['POST'])
def update_progress(chart_id):
    try:
        data = request.get_json()
        row_index = data['rowIndex']
        is_checked = data['isChecked']
        
        # Load current progress and chart data
        progress_data = load_progress(chart_id)
        charts = load_charts()
        chart = charts[chart_id]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], chart['filename'])
        
        # Read CSV to get difficulties
        df = pd.read_csv(file_path)
        rows = df.values.tolist()
        
        # Extend progress array if needed
        while len(progress_data) <= row_index:
            progress_data.append(False)
        
        # Update progress
        progress_data[row_index] = is_checked
        
        # Save progress
        save_progress(chart_id, progress_data)
        
        # Calculate new weighted progress
        progress_stats = calculate_weighted_progress(rows, progress_data)
        
        return jsonify({
            'success': True,
            'progress': progress_stats['percentage'],
            'completed_by_difficulty': progress_stats['completed_by_difficulty'],
            'total_by_difficulty': progress_stats['total_by_difficulty'],
            'completed_weight': progress_stats['completed_weight'],
            'total_weight': progress_stats['total_weight']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
