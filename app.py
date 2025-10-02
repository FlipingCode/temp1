print("Script started")
import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, session, redirect, url_for 

from backend.features.data_processing import DataProcessor
from backend.features.hmpi_calculation import  HMPICalculation
from backend.features.basic_output import HMPIOutput
from backend.features.better_df import PrettyColumns
from backend.features.geospatial_analysis import GeoSpatialAnalyser
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

    df.to_pickle(os.path.join('data', 'uploads', 'df_cache.pkl'))
    session['df_cache'] = os.path.join('data', 'uploads', 'df_cache.pkl')

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
    print(df)
    df.to_pickle(session['df_cache'])

    df2 = format.prettify(df)
    print("It Works")

    return jsonify({
        'message': 'HMPI calculated successfully!',
        'rows': len(df2),
        'columns': list(df2.columns),
        'preview': df2.head(30).to_dict(orient='records')
        })

# Generate Map
@app.route('/map', methods=['GET'])
def generate_map():

    if 'df_cache' not in session:
        return "No data uploaded", 400
    
    df = pd.read_pickle(session['df_cache'])

    if 'HMPI' not in df.columns:
        # Optionally auto-calculate
        df = calculator.calculate(df)
        df.to_pickle(session['df_cache'])
        print("HMPI column calculated automatically.")

    print("Running Geospatial Analysis Module")
    if processor.coordinates_check(df):
        map_html = geospatial.geospatial_analysis(df)
        # Instead of saving a full HTML file, return just the map <div> as string
        return map_html
    else:
        return "No coordinates found in data.", 400

if __name__ == '__main__':
    app.run(debug=True)

 # On Windows: venv\Scripts\activate
 # python app.py