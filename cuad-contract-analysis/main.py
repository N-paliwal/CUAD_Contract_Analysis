"""
Main execution script for CUAD Contract Analysis Pipeline
"""
import argparse
import logging
from pathlib import Path
from typing import List
import pandas as pd
import json
from tqdm import tqdm
from dotenv import load_dotenv

import config
from src.data_loader import load_cuad_contracts
from src.text_extractor import extract_text_from_pdf
from src.llm_processor import LLMProcessor
from src.utils import normalize_text, extract_contract_id, count_words

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contract_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='CUAD Contract Analysis Pipeline'
    )
    parser.add_argument(
        '--num-contracts',
        type=int,
        default=config.NUM_CONTRACTS,
        help='Number of contracts to process'
    )
    parser.add_argument(
        '--provider',
        type=str,
        default=config.LLM_PROVIDER,
        choices=['openai', 'anthropic', 'mistral'],  # ← Fixed!
        help='LLM provider to use'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=config.LLM_MODEL,
        help='LLM model to use'
    )
    parser.add_argument(
        '--enable-semantic-search',
        action='store_true',
        help='Enable semantic search (bonus feature)'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode with single contract'
    )
    parser.add_argument(
        '--contract-path',
        type=str,
        help='Path to single contract for test mode'
    )
    parser.add_argument(
        '--output-format',
        type=str,
        default=config.OUTPUT_FORMAT,
        choices=['csv', 'json', 'both'],
        help='Output format'
    )
    
    return parser.parse_args()


def process_single_contract(pdf_path: Path, llm_processor: LLMProcessor) -> dict:
    """Process a single contract"""
    logger.info(f"Processing contract: {pdf_path.name}")

    try:
        logger.info("  Extracting text from PDF...")
        raw_text = extract_text_from_pdf(pdf_path)

        logger.info("  Normalizing text...")
        contract_text = normalize_text(raw_text)

        if not contract_text or len(contract_text) < 100:
            logger.warning(f"  Insufficient text extracted from {pdf_path.name}")
            return {
                'contract_id': extract_contract_id(pdf_path),
                'summary': "Failed to extract sufficient text",
                'termination_clause': "Not found",
                'confidentiality_clause': "Not found",
                'liability_clause': "Not found",
                'status': 'error'
            }

        logger.info(f"  Extracted {len(contract_text)} characters")

        logger.info("  Processing with LLM...")
        results = llm_processor.process_contract(contract_text)

        results['contract_id'] = extract_contract_id(pdf_path)
        results['contract_length'] = str(len(contract_text))  # Convert to string
        results['word_count'] = str(count_words(contract_text))  # Convert to string
        results['summary_word_count'] = str(count_words(results.get('summary', '')))  # Convert to string
        results['status'] = 'success'


        logger.info(f"  Successfully processed {pdf_path.name}")
        return results

    except Exception as e:
        logger.error(f"  Error processing {pdf_path.name}: {e}")
        return {
            'contract_id': extract_contract_id(pdf_path),
            'summary': f"Error: {str(e)}",
            'termination_clause': "Error",
            'confidentiality_clause': "Error",
            'liability_clause': "Error",
            'status': 'error'
        }


def save_results(results: List[dict], output_format: str):
    """Save results to file(s)"""
    df = pd.DataFrame(results)

    column_order = [
        'contract_id',
        'summary',
        'termination_clause',
        'confidentiality_clause',
        'liability_clause',
        'status'
    ]

    for col in df.columns:
        if col not in column_order:
            column_order.append(col)

    df = df[column_order]

    if output_format in ['csv', 'both']:
        csv_path = config.OUTPUT_CSV
        df.to_csv(csv_path, index=False)
        logger.info(f"Results saved to: {csv_path}")

    if output_format in ['json', 'both']:
        json_path = config.OUTPUT_JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to: {json_path}")


def print_summary_statistics(results: List[dict]):
    """Print summary statistics of processing"""
    total = len(results)
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = total - successful
    
    logger.info("=" * 80)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total contracts processed: {total}")
    logger.info(f"Successful: {successful} ({successful/total*100:.1f}%)")
    logger.info(f"Failed: {failed} ({failed/total*100:.1f}%)")
    
    if successful > 0:
        termination_found = sum(
            1 for r in results 
            if r.get('termination_clause') not in ['Not found', 'Error', None]
        )
        confidentiality_found = sum(
            1 for r in results 
            if r.get('confidentiality_clause') not in ['Not found', 'Error', None]
        )
        liability_found = sum(
            1 for r in results 
            if r.get('liability_clause') not in ['Not found', 'Error', None]
        )
        
        logger.info(f"\nClause Extraction Success Rates:")
        logger.info(f"  Termination clauses: {termination_found}/{total} ({termination_found/total*100:.1f}%)")
        logger.info(f"  Confidentiality clauses: {confidentiality_found}/{total} ({confidentiality_found/total*100:.1f}%)")
        logger.info(f"  Liability clauses: {liability_found}/{total} ({liability_found/total*100:.1f}%)")
        
        # Fix: Convert to int if it's a string
        summary_lengths = []
        for r in results:
            if r.get('status') == 'success':
                word_count = r.get('summary_word_count', 0)
                # Convert to int if it's a string
                if isinstance(word_count, str):
                    try:
                        word_count = int(word_count)
                    except ValueError:
                        word_count = 0
                summary_lengths.append(word_count)
        
        if summary_lengths:
            avg_summary_length = sum(summary_lengths) / len(summary_lengths)
            logger.info(f"\nAverage summary length: {avg_summary_length:.1f} words")
    
    logger.info("=" * 80)

def main():
    """Main execution function"""
    args = parse_arguments()

    logger.info("=" * 80)
    logger.info("CUAD CONTRACT ANALYSIS PIPELINE")
    logger.info("=" * 80)
    logger.info(f"LLM Provider: {args.provider}")
    logger.info(f"LLM Model: {args.model}")
    logger.info(f"Number of contracts: {args.num_contracts}")
    logger.info(f"Output format: {args.output_format}")
    logger.info(f"Semantic search: {'Enabled' if args.enable_semantic_search else 'Disabled'}")
    logger.info("=" * 80)

    logger.info("Initializing LLM processor...")
    llm_processor = LLMProcessor(provider=args.provider, model=args.model)

    if args.test_mode and args.contract_path:
        logger.info(f"Running in test mode with: {args.contract_path}")
        contract_files = [Path(args.contract_path)]
    else:
        logger.info("Loading contracts from CUAD dataset...")
        contract_files = load_cuad_contracts(
            data_dir=config.RAW_DATA_DIR,
            num_contracts=args.num_contracts
        )

    logger.info(f"Found {len(contract_files)} contracts to process")

    results = []

    for pdf_path in tqdm(contract_files, desc="Processing contracts"):
        result = process_single_contract(pdf_path, llm_processor)
        results.append(result)

    logger.info("\nSaving results...")
    save_results(results, args.output_format)

    print_summary_statistics(results)

    if args.enable_semantic_search and results:
        logger.info("\nBuilding semantic search index...")
        try:
            from src.embeddings import SemanticSearchEngine

            search_engine = SemanticSearchEngine()
            search_engine.build_index(results)
            logger.info("Semantic search index built successfully!")

            query = "termination for breach"
            logger.info(f"\nExample search: '{query}'")
            search_results = search_engine.search(query, top_k=3)
            for i, result in enumerate(search_results, 1):
                logger.info(f"{i}. Contract: {result['contract_id']} (Score: {result['score']:.3f})")
                logger.info(f"   Clause: {result['text'][:100]}...")
        except ImportError:
            logger.warning("Semantic search dependencies not installed.")
        except Exception as e:
            logger.error(f"Error building semantic search: {e}")

    logger.info("\n" + "=" * 80)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()