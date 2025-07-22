#!/usr/bin/env python3
"""
Main entry point for the GHCN Climate Data Analysis application.
This script runs data processing and starts the Flask web server.
"""

import logging
import sys
import argparse
from data_processor import DataProcessor
from config import get_config

def main():
    parser = argparse.ArgumentParser(description='GHCN Climate Data Analysis')
    parser.add_argument('--process-data', action='store_true',
                       help='Run data processing (annual update)')
    parser.add_argument('--env', choices=['development', 'production', 'testing'],
                       default='development', help='Environment to run in')
    
    args = parser.parse_args()
    
    # Get configuration for the specified environment
    config = get_config(args.env)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting GHCN Climate Analysis in {args.env} mode")
    
    # Optional: Data Processing (only if requested)
    if args.process_data:
        logger.info("Running data processing pipeline...")
        try:
            processor = DataProcessor()
            success = processor.process_all()
            if not success:
                logger.error("Data processing failed")
                sys.exit(1)
            logger.info("Data processing completed successfully")
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            sys.exit(1)
    
    # Start Flask Server
    logger.info("Starting Flask web server...")
    
    try:
        from server import app
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Starting Flask server on 0.0.0.0:{port}")
        app.run(
            debug=config.DEBUG,
            host='0.0.0.0',
            port=port
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()
