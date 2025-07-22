"""
Database models and operations for climate data storage.
Supports SQLite for development and PostgreSQL for production (AWS RDS).
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

logger = logging.getLogger(__name__)

Base = declarative_base()

class ClimateData(Base):
    """Model for storing climate anomaly data."""
    __tablename__ = 'climate_data'
    
    id = Column(Integer, primary_key=True)
    dataset = Column(String(50), nullable=False)  # 'giss', 'crutem', 'ghcn'
    year = Column(Integer, nullable=False)
    anomaly = Column(Float, nullable=False)  # Temperature anomaly in degrees C
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        Index('idx_dataset_year', 'dataset', 'year'),
    )

class ProcessingLog(Base):
    """Model for tracking data processing runs."""
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True)
    process_type = Column(String(50), nullable=False)  # 'download', 'transform', 'complete'
    status = Column(String(20), nullable=False)  # 'success', 'failure', 'partial'
    message = Column(String(500))
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    records_processed = Column(Integer, default=0)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_url: str = "sqlite:///climate_data.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def store_climate_data(self, dataset: str, df: pd.DataFrame, year_col: str = 'year', 
                          anomaly_col: str = 'anomaly (deg C)') -> bool:
        """Store climate data from a pandas DataFrame."""
        try:
            with self.get_session() as session:
                # Clear existing data for this dataset
                session.query(ClimateData).filter(ClimateData.dataset == dataset).delete()
                
                # Insert new data
                records = []
                for _, row in df.iterrows():
                    record = ClimateData(
                        dataset=dataset,
                        year=int(row[year_col]),
                        anomaly=float(row[anomaly_col])
                    )
                    records.append(record)
                
                session.add_all(records)
                session.commit()
                
                logger.info(f"Stored {len(records)} records for dataset {dataset}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to store climate data for {dataset}: {e}")
            return False
    
    def get_climate_data(self, datasets: Optional[List[str]] = None) -> Dict:
        """Retrieve climate data for visualization."""
        try:
            with self.get_session() as session:
                query = session.query(ClimateData)
                
                if datasets:
                    query = query.filter(ClimateData.dataset.in_(datasets))
                
                results = query.order_by(ClimateData.year).all()
                
                # Organize data by dataset
                data = {}
                years = set()
                
                for record in results:
                    if record.dataset not in data:
                        data[record.dataset] = {}
                    data[record.dataset][record.year] = record.anomaly
                    years.add(record.year)
                
                # Convert to format expected by frontend
                sorted_years = sorted(list(years))
                response = {'years': sorted_years}
                
                for dataset in data:
                    response[dataset] = [data[dataset].get(year) for year in sorted_years]
                
                return response
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve climate data: {e}")
            return {'years': [], 'error': str(e)}
    
    def log_processing_run(self, process_type: str, status: str, message: str = None, 
                          records_processed: int = 0, started_at: datetime = None) -> bool:
        """Log a data processing run."""
        try:
            with self.get_session() as session:
                log_entry = ProcessingLog(
                    process_type=process_type,
                    status=status,
                    message=message,
                    started_at=started_at or datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    records_processed=records_processed
                )
                session.add(log_entry)
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to log processing run: {e}")
            return False
    
    def get_latest_processing_status(self) -> Optional[Dict]:
        """Get the status of the most recent processing run."""
        try:
            with self.get_session() as session:
                latest = session.query(ProcessingLog)\
                    .filter(ProcessingLog.process_type == 'complete')\
                    .order_by(ProcessingLog.completed_at.desc())\
                    .first()
                
                if latest:
                    return {
                        'status': latest.status,
                        'completed_at': latest.completed_at,
                        'message': latest.message,
                        'records_processed': latest.records_processed
                    }
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get latest processing status: {e}")
            return None

# Global database instance
db_manager = None

def get_db_manager(database_url: str = "sqlite:///climate_data.db") -> DatabaseManager:
    """Get or create the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager(database_url)
        db_manager.create_tables()
    return db_manager