import logging
from flask import Flask, render_template, jsonify
from database import get_db_manager
from config import get_config

# Get configuration
config = get_config()

# Configure logging for Flask app
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize database with error handling
try:
    db_manager = get_db_manager(config.DATABASE_URL)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    # Create a dummy db_manager for health checks to work
    db_manager = None

@app.route('/')
def index():
    """Render the main visualization page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Simple health check endpoint for Railway."""
    return jsonify({'status': 'healthy', 'message': 'Climate app is running'})

@app.route('/process-data')
def trigger_data_processing():
    """Manually trigger data processing."""
    try:
        if db_manager is None:
            return jsonify({'error': 'Database not initialized'}), 503
            
        from data_processor import DataProcessor
        processor = DataProcessor()
        success = processor.process_all()
        
        if success:
            return jsonify({'status': 'success', 'message': 'Data processing completed'})
        else:
            return jsonify({'status': 'error', 'message': 'Data processing failed'}), 500
            
    except Exception as e:
        logger.error(f"Error in data processing: {e}")
        return jsonify({'error': f'Data processing failed: {str(e)}'}), 500

@app.get('/data')
def dataset():
    """Get climate data for visualization."""
    try:
        if db_manager is None:
            return jsonify({'error': 'Database not initialized', 'years': [], 'giss': [], 'crutem': [], 'ghcn': []}), 500
            
        # Get data from database
        data = db_manager.get_climate_data(['giss', 'crutem', 'ghcn'])

        if 'error' in data:
            logger.error(f"Database error: {data['error']}")
            return jsonify({'error': 'Failed to retrieve data'}), 500

        # Ensure all datasets are present and handle missing data
        for dataset in ['giss', 'crutem', 'ghcn']:
            if dataset not in data:
                data[dataset] = [None] * len(data.get('years', []))

        logger.info(f"Successfully retrieved data for {len(data.get('years', []))} years")
        return jsonify(data)

    except Exception as e:
        logger.error(f"Unexpected error in /data endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.get('/status')
def processing_status():
    """Get the status of the most recent data processing run."""
    try:
        if db_manager is None:
            return jsonify({'message': 'Database not initialized'}), 503
            
        status = db_manager.get_latest_processing_status()
        if status:
            return jsonify(status)
        else:
            return jsonify({'message': 'No processing runs found'}), 404

    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        return jsonify({'error': 'Failed to get processing status'}), 500

@app.post('/analyze')
def analyze_datasets():
    """Perform statistical analysis on selected datasets."""
    try:
        from flask import request
        import numpy as np
        from scipy.stats import pearsonr

        data = request.get_json()
        datasets = data.get('datasets', [])
        start_year = data.get('start_year')
        end_year = data.get('end_year')

        if not datasets:
            return jsonify({'error': 'No datasets specified'}), 400

        # Get filtered data
        climate_data = db_manager.get_climate_data(datasets)

        if 'error' in climate_data:
            return jsonify({'error': climate_data['error']}), 500

        # Filter by year range if specified
        if start_year and end_year:
            filtered_years = []
            filtered_data = {}

            for i, year in enumerate(climate_data['years']):
                if start_year <= year <= end_year:
                    filtered_years.append(year)
                    for dataset in datasets:
                        if dataset not in filtered_data:
                            filtered_data[dataset] = []
                        if dataset in climate_data:
                            filtered_data[dataset].append(climate_data[dataset][i])

            climate_data['years'] = filtered_years
            climate_data.update(filtered_data)

        # Calculate correlation matrix
        correlations = {}
        if len(datasets) > 1:
            for i, dataset1 in enumerate(datasets):
                if dataset1 not in climate_data:
                    continue
                correlations[dataset1] = {}

                for j, dataset2 in enumerate(datasets):
                    if dataset2 not in climate_data:
                        continue

                    if i != j:
                        # Filter out None values
                        data1 = climate_data[dataset1]
                        data2 = climate_data[dataset2]

                        valid_pairs = [(d1, d2) for d1, d2 in zip(data1, data2)
                                     if d1 is not None and d2 is not None]

                        if len(valid_pairs) > 2:
                            vals1, vals2 = zip(*valid_pairs)
                            correlation, p_value = pearsonr(vals1, vals2)
                            correlations[dataset1][dataset2] = {
                                'correlation': round(correlation, 4),
                                'p_value': round(p_value, 6),
                                'n_samples': len(valid_pairs)
                            }
                        else:
                            correlations[dataset1][dataset2] = {
                                'correlation': None,
                                'p_value': None,
                                'n_samples': len(valid_pairs)
                            }

        # Calculate trend statistics
        trends = {}
        for dataset in datasets:
            if dataset in climate_data and climate_data[dataset]:
                years = climate_data['years']
                values = climate_data[dataset]

                # Filter valid data points
                valid_data = [(year, val) for year, val in zip(years, values)
                            if val is not None]

                if len(valid_data) > 2:
                    years_valid, values_valid = zip(*valid_data)

                    # Calculate linear trend
                    years_array = np.array(years_valid)
                    values_array = np.array(values_valid)

                    coefficients = np.polyfit(years_array, values_array, 1)
                    slope_per_year = coefficients[0]
                    slope_per_decade = slope_per_year * 10

                    # Calculate R-squared
                    trend_line = coefficients[0] * years_array + coefficients[1]
                    ss_res = np.sum((values_array - trend_line) ** 2)
                    ss_tot = np.sum((values_array - np.mean(values_array)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                    trends[dataset] = {
                        'slope_per_year': round(slope_per_year, 6),
                        'slope_per_decade': round(slope_per_decade, 4),
                        'r_squared': round(r_squared, 4),
                        'n_samples': len(valid_data),
                        'period': f"{min(years_valid)}-{max(years_valid)}"
                    }

        return jsonify({
            'correlations': correlations,
            'trends': trends,
            'period': f"{min(climate_data['years'])}-{max(climate_data['years'])}" if climate_data['years'] else None,
            'total_years': len(climate_data['years']) if climate_data['years'] else 0
        })

    except ImportError:
        return jsonify({'error': 'scipy not available for advanced statistics'}), 500
    except Exception as e:
        logger.error(f"Error in statistical analysis: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
