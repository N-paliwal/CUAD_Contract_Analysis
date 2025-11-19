"""
Data loading and management for CUAD dataset
"""
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

def load_cuad_contracts(data_dir: Path, num_contracts: int = 50) -> List[Path]:
    """
    Load contract PDF files from CUAD dataset

    Args:
        data_dir: Directory containing contract PDFs
        num_contracts: Number of contracts to load

    Returns:
        List of paths to PDF files
    """
    pdf_files = []

    possible_dirs = [
        data_dir,
        data_dir / "CUAD_v1",
        data_dir / "full_contract_pdf",
        data_dir / "CUAD_v1" / "full_contract_pdf"
    ]

    for directory in possible_dirs:
        if directory.exists():
            pdfs = list(directory.glob("*.pdf"))
            if pdfs:
                pdf_files.extend(pdfs)
                break

    if not pdf_files:
        logger.warning(f"No PDF files found in {data_dir}")
        logger.info("Please download and extract CUAD dataset to data/raw/")
        logger.info("Download from: https://zenodo.org/record/4595826")
        return []

    pdf_files = sorted(pdf_files)[:num_contracts]
    logger.info(f"Loaded {len(pdf_files)} contract files")
    return pdf_files
