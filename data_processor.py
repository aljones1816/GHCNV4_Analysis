#!/usr/bin/env python3
"""
Standalone data processing module for GHCN climate data.
This module handles downloading, processing, and storing climate data
independently from the web server.
"""

import logging
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from scripts.raw_data_extract import download_all_data
from scripts.transform_gistemp_adjusted import transform_giss_data
from scripts.transform_crutem_adjusted import transform_crutem_data
from scripts.transform_ghcn_raw import transform_ghcn_data
from database import get_db_manager
from config import get_config

# Get configuration
config = get_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles all climate data processing operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.data_dir = config.DATA_DIR
        self.db_manager = get_db_manager(database_url or config.DATABASE_URL)
        config.init_directories()
    
    def download_data(self) -> bool:
        """Download all climate datasets."""
        start_time = datetime.utcnow()
        try:
            logger.info("Starting data download...")
            download_all_data()
            logger.info("Data download completed successfully")
            
            self.db_manager.log_processing_run(
                process_type='download',
                status='success',
                message='All datasets downloaded successfully',
                started_at=start_time
            )
            return True
            
        except Exception as e:
            logger.error(f"Data download failed: {e}")
            self.db_manager.log_processing_run(
                process_type='download',
                status='failure',
                message=str(e),
                started_at=start_time
            )
            return False
    
    def transform_and_store_data(self) -> Dict[str, bool]:
        """Transform all downloaded datasets and store in database."""
        transformations = [
            ("giss", transform_giss_data, "data/clean/giss_anomalies_clean.csv"),
            ("crutem", transform_crutem_data, "data/clean/crutem_anomalies_clean.csv"),
            ("ghcn", transform_ghcn_data, "data/clean/ghcnm_anomalies_clean.csv")
        ]
        
        results = {}
        total_records = 0
        
        for dataset_name, transform_func, csv_path in transformations:
            start_time = datetime.utcnow()
            try:
                logger.info(f"Transforming {dataset_name.upper()} data...")
                
                # Run transformation
                transform_func()
                
                # Load the transformed data
                df = pd.read_csv(csv_path)
                
                # Handle different column names for anomaly data
                anomaly_col = 'anomaly (deg C)'
                if anomaly_col not in df.columns:
                    # Try alternative column names
                    possible_cols = [col for col in df.columns if 'anomaly' in col.lower()]
                    if possible_cols:
                        anomaly_col = possible_cols[0]
                    else:
                        raise ValueError(f"No anomaly column found in {csv_path}")
                
                # Store in database
                success = self.db_manager.store_climate_data(
                    dataset=dataset_name,
                    df=df,
                    anomaly_col=anomaly_col
                )
                
                if success:
                    records_count = len(df)
                    total_records += records_count
                    logger.info(f"{dataset_name.upper()} data transformation and storage completed successfully ({records_count} records)")
                    results[dataset_name] = True
                    
                    self.db_manager.log_processing_run(
                        process_type='transform',
                        status='success',
                        message=f'{dataset_name.upper()} data processed successfully',
                        records_processed=records_count,
                        started_at=start_time
                    )
                else:
                    raise Exception("Database storage failed")
                    
            except Exception as e:
                logger.error(f"{dataset_name.upper()} data transformation failed: {e}")
                results[dataset_name] = False
                
                self.db_manager.log_processing_run(
                    process_type='transform',
                    status='failure',
                    message=f'{dataset_name.upper()}: {str(e)}',
                    started_at=start_time
                )
        
        return results
    
    def process_all(self) -> bool:
        """Run the complete data processing pipeline."""
        start_time = datetime.utcnow()
        logger.info("Starting complete data processing pipeline")
        
        try:
            # Step 1: Download data
            if not self.download_data():
                self.db_manager.log_processing_run(
                    process_type='complete',
                    status='failure',
                    message='Pipeline failed at download stage',
                    started_at=start_time
                )
                return False
            
            # Step 2: Transform and store data
            results = self.transform_and_store_data()
            
            # Determine overall success
            successful_datasets = [name for name, success in results.items() if success]
            failed_datasets = [name for name, success in results.items() if not success]
            
            if all(results.values()):
                logger.info("Complete data processing pipeline completed successfully")
                self.db_manager.log_processing_run(
                    process_type='complete',
                    status='success',
                    message=f'All datasets processed successfully: {", ".join(successful_datasets)}',
                    started_at=start_time
                )
                return True
            elif successful_datasets:
                logger.warning(f"Pipeline completed with partial success. Failed: {', '.join(failed_datasets)}")
                self.db_manager.log_processing_run(
                    process_type='complete',
                    status='partial',
                    message=f'Successful: {", ".join(successful_datasets)}. Failed: {", ".join(failed_datasets)}',
                    started_at=start_time
                )
                return False
            else:
                logger.error("Pipeline failed - no datasets processed successfully")
                self.db_manager.log_processing_run(
                    process_type='complete',
                    status='failure',
                    message='No datasets processed successfully',
                    started_at=start_time
                )
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error in processing pipeline: {e}")
            self.db_manager.log_processing_run(
                process_type='complete',
                status='failure',
                message=f'Unexpected error: {str(e)}',
                started_at=start_time
            )
            return False

def main():
    """Entry point for standalone data processing."""
    processor = DataProcessor()
    success = processor.process_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()