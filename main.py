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
    parser.add_argument('--skip-processing', action='store_true', 
                       help='Skip data processing and start server directly')
    parser.add_argument('--process-only', action='store_true',
                       help='Run data processing only, do not start server')
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
    
    success = True
    
    # Step 1: Data Processing (unless skipped)
    if not args.skip_processing:
        logger.info("Starting data processing pipeline...")
        processor = DataProcessor()
        success = processor.process_all()
        
        if not success:
            logger.error("Data processing failed")
            if args.process_only:
                sys.exit(1)
            else:
                logger.warning("Starting server despite processing failure - using existing data")
    
    # Step 2: Start Flask Server (unless process-only mode)
    if not args.process_only:
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
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    import os
    main()
