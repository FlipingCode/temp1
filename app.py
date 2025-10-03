print("Script started")
import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response 

from backend.features.data_processing import DataProcessor
from backend.features.hmpi_calculation import  HMPICalculation
from backend.features.basic_output import HMPIOutput
from backend.features.better_df import PrettyColumns
from backend.features.geospatial_analysis import GeoSpatialAnalyser
from backend.features.report_generation import ReportGenerator
from werkzeug.utils import secure_filename

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)
app.secret_key = 'some-secret'

UPLOAD_FOLDER = os.path.join('data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initiating Functions
processor = DataProcessor()
calculator = HMPICalculation()
outputter = HMPIOutput()
format = PrettyColumns()
geospatial = GeoSpatialAnalyser()
reporter = ReportGenerator()
    
# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Analyzer Page
@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

# Info Page
@app.route('/info')
def info():
    return render_template('info.html')

# Upload
@app.route('/upload', methods=['POST'])
def upload_file():

    # Check for input file
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file=request.files['file']

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Processing Input Data
    df=processor.load(filepath) 
    print("Data Loaded Successfully")

    # --- Start of Fix ---
    # Save the raw dataframe for calculation, but we will save the formatted one later
    df.to_pickle(os.path.join('data', 'uploads', 'df_cache.pkl'))
    session['df_cache'] = os.path.join('data', 'uploads', 'df_cache.pkl')
    # --- End of Fix ---

    # Saving filepath in session 
    session['uploaded_file'] = filepath

    # Send a preview back to frontend
    return jsonify({
            'message': 'File uploaded and cleaned successfully!',
            'rows': len(df),
            'columns': list(df.columns),
            'preview': df.head(30).to_dict(orient='records')
        })

# Calculate
@app.route('/calculate', methods=['POST'])
def calculate_hmpi():
    if 'uploaded_file' not in session:
        return jsonify({'error': 'No file uploaded'}), 400

    filepath = session['uploaded_file']
    df = processor.load(filepath)

    # Calculating HMPI
    print("Running Calculation Module")
    df = calculator.calculate(df)
    df_pretty = format.prettify(df.copy()) # Prettify a copy for display
    
    # --- Start of Fix ---
    # Save the prettified dataframe so the report has the correct columns
    df_pretty.to_pickle(session['df_cache']) 
    # --- End of Fix ---

    return jsonify({
        'message': 'HMPI calculated successfully!',
        'rows': len(df_pretty),
        'columns': list(df_pretty.columns),
        'preview': df_pretty.head(30).to_dict(orient='records')
        })

# Generate Map
@app.route('/map', methods=['GET'])
def generate_map():

    if 'df_cache' not in session:
        return "No data uploaded", 400
    
    df = pd.read_pickle(session['df_cache'])

    # The dataframe from pickle is now the prettified one, so we check for 'HMPI'
    if 'HMPI' not in df.columns:
        return "HMPI column not found, please re-analyze your data.", 400

    print("Running Geospatial Analysis Module")
    # The data processor will find 'Latitude' and 'Longitude' even if they are named differently
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        map_html = geospatial.geospatial_analysis(df)
        return map_html
    else:
        return "No coordinates found in data.", 400

# Generate Report
@app.route('/report', methods=['POST'])
def generate_report_route():
    if 'df_cache' not in session:
        return "No data available to generate a report.", 400

    df = pd.read_pickle(session['df_cache'])
    report_data = request.get_json()
    # --- Start of Fix ---
    # Pass the path to the static folder to the report generator
    static_folder_path = os.path.join(app.root_path, 'frontend', 'static')
    pdf_bytes = reporter.generate_report(df, report_data, static_folder_path)
    # --- End of Fix ---
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=hmpi_report.pdf'}
    )


if __name__ == '__main__':
    app.run(debug=True)
 # On Windows: venv\Scripts\activate
 # python app.py
