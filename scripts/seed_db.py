#!/usr/bin/env python3
"""
Development script to populate sample metadata
"""

import asyncio
from sqlalchemy.orm import sessionmaker
from app.models.db import engine, Base
from app.models.documents import Document
from app.models.datasets import Dataset

async def seed_database():
    """Populate database with sample data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Sample documents
        sample_docs = [
            Document(
                filename="sales_data.csv",
                file_path="/data/sales_data.csv",
                content="Sample CSV content",
                metadata={"type": "csv", "columns": ["date", "sales", "region"]},
                file_size=1024,
                mime_type="text/csv"
            ),
            Document(
                filename="customer_data.json",
                file_path="/data/customer_data.json",
                content="Sample JSON content",
                metadata={"type": "json", "structure": "nested"},
                file_size=2048,
                mime_type="application/json"
            )
        ]
        
        for doc in sample_docs:
            db.add(doc)
        
        db.commit()
        
        # Sample datasets
        sample_datasets = [
            Dataset(
                name="Sales Data",
                description="Monthly sales data by region",
                schema={
                    "columns": [
                        {"name": "date", "type": "date"},
                        {"name": "sales", "type": "float"},
                        {"name": "region", "type": "string"}
                    ]
                },
                source_file_id=1,
                row_count=1000,
                column_count=3
            )
        ]
        
        for dataset in sample_datasets:
            db.add(dataset)
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
