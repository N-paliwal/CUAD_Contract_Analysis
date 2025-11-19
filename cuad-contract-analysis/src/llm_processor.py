"""
LLM-based contract analysis and clause extraction - IMPROVED VERSION
Implements chunking, keyword filtering, and enhanced prompt engineering
"""
import os
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv
import logging
import re
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 1000) -> List[str]:
    """Split text into overlapping chunks to handle long contracts"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += chunk_size - overlap
    
    logger.debug(f"Split text into {len(chunks)} chunks")
    return chunks


def find_relevant_sections(contract_text: str, clause_type: str) -> List[str]:
    """Find sections likely to contain the clause using keywords"""
    
    keywords = {
        "termination": [
            "terminat", "cancel", "expire", "dissolve", "cease", 
            "end of term", "term and termination", "duration", "renewal"
        ],
        "confidentiality": [
            "confidential", "proprietary", "non-disclosure", "NDA", 
            "secret", "information", "disclosure", "protect"
        ],
        "liability": [
            "liab", "indemnif", "warrant", "disclaim", "limit", 
            "cap", "damages", "loss", "harm", "injury", "risk"
        ]
    }
    
    relevant_keywords = keywords.get(clause_type, [])
    
    # Split by paragraphs
    paragraphs = re.split(r'\n\s*\n', contract_text)
    
    relevant_sections = []
    for para in paragraphs:
        if len(para.strip()) < 50:  # Skip very short paragraphs
            continue
        
        para_lower = para.lower()
        # Check if paragraph contains any keywords
        if any(keyword.lower() in para_lower for keyword in relevant_keywords):
            relevant_sections.append(para)
    
    logger.debug(f"Found {len(relevant_sections)} relevant sections for {clause_type}")
    
    # If too many sections, take the most keyword-dense ones
    if len(relevant_sections) > 10:
        # Score by keyword density
        scored_sections = []
        for section in relevant_sections:
            section_lower = section.lower()
            score = sum(1 for kw in relevant_keywords if kw.lower() in section_lower)
            scored_sections.append((score, section))
        
        scored_sections.sort(reverse=True, key=lambda x: x[0])
        relevant_sections = [s[1] for s in scored_sections[:10]]
    
    return relevant_sections if relevant_sections else [contract_text]


def deduplicate_clauses(clauses: List[str]) -> List[str]:
    """Remove duplicate or very similar clauses"""
    if not clauses:
        return []
    
    unique = []
    for clause in clauses:
        clause_clean = clause.strip().lower()
        # Check if this clause is substantially different from existing ones
        is_duplicate = False
        for existing in unique:
            existing_clean = existing.strip().lower()
            # If 80% similar, consider duplicate
            if clause_clean in existing_clean or existing_clean in clause_clean:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(clause)
    
    return unique


class LLMProcessor:
    """Process contracts using LLM APIs with improved accuracy"""
    
    def __init__(self, provider: str = "mistral", model: str = "mistral-small-latest"):
        self.provider = provider
        self.model = model
        self.client: Any = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize API client based on provider"""
        if self.provider == "mistral":
            import openai
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError("MISTRAL_API_KEY not found in environment variables")
            
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.mistral.ai/v1"
            )
            logger.info(f"Initialized Mistral client with model: {self.model}")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.0, 
                  max_tokens: int = 8192) -> str:
        """Call LLM API with retry logic"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
    
    def extract_clause(self, contract_text: str, clause_type: str,
                      use_few_shot: bool = True) -> str:
        """Extract specific clause from contract using improved multi-stage approach"""
        
        # Stage 1: Find relevant sections using keywords
        logger.debug(f"Stage 1: Finding relevant sections for {clause_type}")
        relevant_sections = find_relevant_sections(contract_text, clause_type)
        
        # Stage 2: Extract from each relevant section
        all_findings = []
        
        if len(relevant_sections) == 1 and relevant_sections[0] == contract_text:
            # No specific sections found, use chunking on full text
            logger.debug(f"Stage 2: No specific sections found, using full text chunking")
            chunks = chunk_text(contract_text, chunk_size=10000, overlap=1000)
            
            for i, chunk in enumerate(chunks):
                logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
                result = self._extract_from_text(chunk, clause_type, use_few_shot)
                if result != "Not found":
                    all_findings.append(result)
        else:
            # Process relevant sections
            logger.debug(f"Stage 2: Processing {len(relevant_sections)} relevant sections")
            for i, section in enumerate(relevant_sections[:8]):  # Limit to 8 sections
                logger.debug(f"Processing section {i+1}/{min(len(relevant_sections), 8)}")
                result = self._extract_from_text(section, clause_type, use_few_shot)
                if result != "Not found":
                    all_findings.append(result)
        
        # Stage 3: Merge and deduplicate findings
        if not all_findings:
            logger.debug(f"No {clause_type} clause found")
            return "Not found"
        
        # Split any multi-clause responses
        all_clauses = []
        for finding in all_findings:
            # Split by delimiter if present
            clauses = [c.strip() for c in finding.split("|||")]
            all_clauses.extend(clauses)
        
        # Deduplicate
        unique_clauses = deduplicate_clauses(all_clauses)
        
        logger.debug(f"Found {len(unique_clauses)} unique {clause_type} clause(s)")
        
        # Return merged result
        return " ||| ".join(unique_clauses) if unique_clauses else "Not found"
    
    def _extract_from_text(self, text: str, clause_type: str, use_few_shot: bool) -> str:
        """Extract clause from a specific text segment"""
        system_prompt = self._build_extraction_system_prompt()
        user_prompt = self._build_extraction_user_prompt(text, clause_type, use_few_shot)
        
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._call_api(messages, temperature=0.0, max_tokens=8192)
        return self._parse_clause_response(response)
    
    def generate_summary(self, contract_text: str,
                        word_limit: tuple = (100, 150)) -> str:
        """Generate contract summary"""
        
        # For very long contracts, use first portion and key sections
        if len(contract_text) > 20000:
            # Take beginning and search for key sections
            summary_text = contract_text[:15000]
            
            # Try to find key sections
            key_terms = ["whereas", "recitals", "purpose", "obligations", "payment", 
                        "term", "termination", "liability", "indemnif"]
            
            for term in key_terms:
                pattern = re.compile(rf'\n[^\n]*{term}[^\n]*\n', re.IGNORECASE)
                matches = pattern.findall(contract_text)
                if matches:
                    summary_text += "\n\n" + "\n".join(matches[:3])
        else:
            summary_text = contract_text
        
        system_prompt = """You are a legal expert specializing in contract analysis.
Your task is to generate concise, accurate summaries of legal contracts.
Focus on extracting the most important information."""
        
        user_prompt = f"""Please provide a summary of the following contract in {word_limit[0]}-{word_limit[1]} words.

The summary MUST include:
1. Purpose of the agreement (what is this contract for?)
2. Key obligations of each party (what must each party do?)
3. Notable risks or penalties (what happens if obligations aren't met?)

Contract Text:
{summary_text[:18000]}

Provide ONLY the summary, nothing else.

Summary:"""
        
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_api(messages, temperature=0.3, max_tokens=500)
    
    def _build_extraction_system_prompt(self) -> str:
        """Build system prompt for clause extraction"""
        return """You are a legal AI assistant specialized in contract analysis and clause extraction.

Your task is to identify and extract specific types of clauses from legal contracts with high accuracy.

CRITICAL INSTRUCTIONS:
- Extract ONLY the relevant clause text, maintaining exact wording from the contract
- If multiple instances of the clause exist, extract ALL of them separated by " ||| "
- Extract complete clauses - don't cut off mid-sentence
- If the clause spans multiple paragraphs, include all relevant paragraphs
- If the clause is definitely not present in the provided text, respond with "NOT_FOUND"
- Be thorough but precise - include all relevant text but exclude unrelated content
- Look for the substance of the clause, not just section headers"""
    
    def _build_extraction_user_prompt(self, contract_text: str,
                                     clause_type: str,
                                     use_few_shot: bool) -> str:
        """Build QA-style user prompt for clause extraction"""
        
        examples = ""
        if use_few_shot:
            examples = self._get_few_shot_examples(clause_type)
        
        questions = {
            "termination": """Question: What are the termination provisions in this contract?

Description: Look for clauses that specify:
- Conditions under which the agreement can be terminated (termination for cause, convenience, etc.)
- Notice periods required for termination
- Rights of either party to terminate
- Automatic termination conditions
- Effects of termination
- Survival of obligations after termination""",
            
            "confidentiality": """Question: What are the confidentiality and non-disclosure obligations?

Description: Look for clauses that specify:
- What information is considered confidential or proprietary
- Obligations to protect confidential information
- Restrictions on disclosure to third parties
- Permitted uses of confidential information
- Duration of confidentiality obligations
- Exceptions to confidentiality (e.g., publicly available information)
- Return or destruction of confidential information""",
            
            "liability": """Question: What are the liability, limitation of liability, and indemnification provisions?

Description: Look for clauses that specify:
- Limitations on liability (caps on damages, excluded types of damages)
- Indemnification obligations (who indemnifies whom and for what)
- Disclaimers of warranties
- Allocation of risk between parties
- Liability for breach of specific obligations
- Exclusions of consequential or indirect damages
- Maximum liability amounts"""
        }
        
        question_text = questions.get(clause_type, f"What are the {clause_type} provisions?")
        
        prompt = f"""{question_text}

{examples}

Contract Text to Analyze:
---
{contract_text}
---

Instructions:
- Extract ALL relevant clauses that answer the question above
- If multiple relevant clauses exist in different parts of the text, extract all of them separated by " ||| "
- Provide the exact text from the contract - do not paraphrase or summarize
- Include complete sentences and paragraphs
- If you find NO relevant clause in this text, respond with exactly "NOT_FOUND"

Extracted Clause(s):"""
        
        return prompt
    
    def _get_few_shot_examples(self, clause_type: str) -> str:
        """Get few-shot examples for specific clause type with realistic contract language"""
        
        if clause_type == "termination":
            return """Here are examples of termination clause extraction:

Example 1:
Contract Text: "Either Party may terminate this Agreement at any time, with or without cause, upon thirty (30) days prior written notice to the other Party. Upon termination for any reason, all rights and obligations of the Parties shall cease, except for those obligations that by their nature are intended to survive termination, including but not limited to confidentiality obligations, payment obligations, and indemnification obligations."

Extracted Clause: Either Party may terminate this Agreement at any time, with or without cause, upon thirty (30) days prior written notice to the other Party. Upon termination for any reason, all rights and obligations of the Parties shall cease, except for those obligations that by their nature are intended to survive termination, including but not limited to confidentiality obligations, payment obligations, and indemnification obligations.

Example 2:
Contract Text: "This Agreement shall automatically terminate upon the occurrence of any of the following events: (a) the bankruptcy or insolvency of either party; (b) a material breach by either party that remains uncured for thirty (30) days after written notice of such breach; or (c) the mutual written agreement of both parties to terminate."

Extracted Clause: This Agreement shall automatically terminate upon the occurrence of any of the following events: (a) the bankruptcy or insolvency of either party; (b) a material breach by either party that remains uncured for thirty (30) days after written notice of such breach; or (c) the mutual written agreement of both parties to terminate.

"""
        
        elif clause_type == "confidentiality":
            return """Here are examples of confidentiality clause extraction:

Example 1:
Contract Text: "The Receiving Party agrees to hold and maintain the Confidential Information in strict confidence and to take all reasonable precautions to protect such Confidential Information. The Receiving Party shall not, without the prior written approval of the Disclosing Party, disclose any Confidential Information to any third parties, except to those employees, contractors, and advisors who need to know such information and who have been advised of the confidential nature of such information."

Extracted Clause: The Receiving Party agrees to hold and maintain the Confidential Information in strict confidence and to take all reasonable precautions to protect such Confidential Information. The Receiving Party shall not, without the prior written approval of the Disclosing Party, disclose any Confidential Information to any third parties, except to those employees, contractors, and advisors who need to know such information and who have been advised of the confidential nature of such information.

Example 2:
Contract Text: "All information and materials furnished by one party to the other party, whether furnished before or after the date of this Agreement, that are marked as confidential or proprietary or that would reasonably be understood to be confidential given the nature of the information and circumstances of disclosure, shall be deemed 'Confidential Information' and shall be subject to the confidentiality obligations set forth herein for a period of five (5) years from the date of disclosure."

Extracted Clause: All information and materials furnished by one party to the other party, whether furnished before or after the date of this Agreement, that are marked as confidential or proprietary or that would reasonably be understood to be confidential given the nature of the information and circumstances of disclosure, shall be deemed 'Confidential Information' and shall be subject to the confidentiality obligations set forth herein for a period of five (5) years from the date of disclosure.

"""
        
        elif clause_type == "liability":
            return """Here are examples of liability clause extraction:

Example 1:
Contract Text: "IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATED TO THIS AGREEMENT, EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. THE TOTAL LIABILITY OF PROVIDER UNDER THIS AGREEMENT SHALL NOT EXCEED THE TOTAL FEES PAID BY CLIENT TO PROVIDER DURING THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM."

Extracted Clause: IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATED TO THIS AGREEMENT, EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. THE TOTAL LIABILITY OF PROVIDER UNDER THIS AGREEMENT SHALL NOT EXCEED THE TOTAL FEES PAID BY CLIENT TO PROVIDER DURING THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM.

Example 2:
Contract Text: "Company shall indemnify, defend, and hold harmless Contractor and its officers, directors, employees, and agents from and against any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable attorneys' fees) arising out of or resulting from: (i) any breach by Company of its obligations under this Agreement; (ii) any negligent or willful acts or omissions by Company; or (iii) any claims that Company's materials or instructions infringe upon or violate any intellectual property rights of any third party."

Extracted Clause: Company shall indemnify, defend, and hold harmless Contractor and its officers, directors, employees, and agents from and against any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable attorneys' fees) arising out of or resulting from: (i) any breach by Company of its obligations under this Agreement; (ii) any negligent or willful acts or omissions by Company; or (iii) any claims that Company's materials or instructions infringe upon or violate any intellectual property rights of any third party.

"""
        
        return ""
    
    def _parse_clause_response(self, response: str) -> str:
        """Parse and clean clause extraction response"""
        # Remove common prefixes
        prefixes = [
            "Extracted Clause(s):",
            "Extracted Termination Clause:",
            "Extracted Confidentiality Clause:",
            "Extracted Liability Clause:",
            "Extracted Clause:",
            "The clause is:",
            "Answer:",
            "Clause:",
        ]
        
        response_cleaned = response.strip()
        for prefix in prefixes:
            if response_cleaned.startswith(prefix):
                response_cleaned = response_cleaned[len(prefix):].strip()
        
        # Check for NOT_FOUND
        if "NOT_FOUND" in response_cleaned.upper() or "NOT FOUND" in response_cleaned.upper():
            return "Not found"
        
        # Check for explicit "no clause" statements
        no_clause_indicators = [
            "no termination clause",
            "no confidentiality clause",
            "no liability clause",
            "clause is not present",
            "does not contain",
            "no such clause",
            "clause not found"
        ]
        
        response_lower = response_cleaned.lower()
        if any(indicator in response_lower for indicator in no_clause_indicators):
            return "Not found"
        
        # Must have minimum length to be valid
        if len(response_cleaned) < 20:
            return "Not found"
        
        return response_cleaned.strip()
    
    def process_contract(self, contract_text: str) -> Dict[str, str]:
        """Process entire contract - extract clauses and generate summary"""
        results: Dict[str, str] = {}
        
        logger.info("Extracting termination clause...")
        results['termination_clause'] = self.extract_clause(
            contract_text, "termination", use_few_shot=True
        )
        
        logger.info("Extracting confidentiality clause...")
        results['confidentiality_clause'] = self.extract_clause(
            contract_text, "confidentiality", use_few_shot=True
        )
        
        logger.info("Extracting liability clause...")
        results['liability_clause'] = self.extract_clause(
            contract_text, "liability", use_few_shot=True
        )
        
        logger.info("Generating contract summary...")
        results['summary'] = self.generate_summary(contract_text)
        
        return results