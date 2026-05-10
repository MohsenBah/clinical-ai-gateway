import json
import logging
from pathlib import Path
from typing import List, Dict, Any

import chromadb
import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from sentence_transformers import SentenceTransformer

from gateway.config import settings

logger = logging.getLogger(__name__)


class DataIngestionService:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.collection_name
        )
        self.embedding_model = SentenceTransformer(settings.embedding_model)

        # Initialize Presidio engines
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def load_synthetic_data(self, data_path: str) -> pd.DataFrame:
        """Load synthetic clinical data from JSON/CSV files."""
        path = Path(data_path)

        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        elif path.suffix.lower() == '.csv':
            return pd.read_csv(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def redact_phi(self, text: str) -> str:
        """Use Presidio to detect and redact PHI from text."""
        if not text:
            return text

        try:
            # Analyze text for PHI
            results = self.analyzer.analyze(
                text=text,
                language='en',
                entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",
                         "US_SSN", "US_DRIVER_LICENSE", "US_PASSPORT",
                         "US_BANK_NUMBER", "CREDIT_CARD", "IP_ADDRESS"]
            )

            # Anonymize detected PHI
            if results:
                anonymized = self.anonymizer.anonymize(
                    text=text,
                    analyzer_results=results
                )
                return anonymized.text
            else:
                return text
        except Exception as e:
            logger.warning(f"PHI redaction failed: {e}")
            return text

    def process_clinical_record(self, record: Dict[str, Any]) -> Dict[str, str]:
        """Process a clinical record: redact PHI and create searchable text."""
        # Combine relevant fields into searchable text
        searchable_fields = [
            record.get('patient_name', ''),
            record.get('diagnosis', ''),
            record.get('medications', ''),
            record.get('symptoms', ''),
            record.get('treatment_plan', ''),
            record.get('notes', '')
        ]

        combined_text = ' '.join(str(field) for field in searchable_fields if field)

        # Redact PHI from the combined text
        redacted_text = self.redact_phi(combined_text)

        return {
            'id': str(record.get('id', record.get('patient_id', ''))),
            'original_text': combined_text,
            'redacted_text': redacted_text,
            'metadata': {
                'patient_id': record.get('patient_id', ''),
                'record_type': record.get('record_type', 'clinical_note'),
                'date': record.get('date', ''),
                'phi_redacted': len(combined_text) != len(redacted_text)
            }
        }

    def ingest_data(self, data_path: str) -> int:
        """Ingest clinical data into the vector database."""
        logger.info(f"Starting data ingestion from {data_path}")

        # Load data
        df = self.load_synthetic_data(data_path)
        logger.info(f"Loaded {len(df)} records")

        documents = []
        metadatas = []
        ids = []

        for _, record in df.iterrows():
            processed = self.process_clinical_record(record.to_dict())

            if processed['redacted_text'].strip():
                documents.append(processed['redacted_text'])
                metadatas.append(processed['metadata'])
                ids.append(processed['id'])

        if not documents:
            logger.warning("No valid documents to ingest")
            return 0

        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(documents).tolist()

        # Add to vector database
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Successfully ingested {len(documents)} documents")
        return len(documents)

    def search_similar(self, query: str, n_results: int = None) -> List[Dict[str, Any]]:
        """Search for similar clinical records."""
        if n_results is None:
            n_results = settings.max_context_docs

        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )

        return [
            {
                'document': doc,
                'metadata': meta,
                'distance': dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]

    def clear_collection(self):
        """Clear all data from the collection."""
        self.chroma_client.delete_collection(name=settings.collection_name)
        self.collection = self.chroma_client.create_collection(
            name=settings.collection_name
        )
        logger.info("Collection cleared")