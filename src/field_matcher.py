import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FieldMatch:
    field_name: str
    data_key: str
    confidence: float
    reasoning: str

class FieldMatcher:
    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.anthropic = None
        if anthropic_api_key or os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic = Anthropic(api_key=anthropic_api_key or os.getenv('ANTHROPIC_API_KEY'))
        
        # Common field patterns for fallback matching
        self.field_patterns = {
            'first_name': [
                r'\bfirst\s*name\b', r'\bfname\b', r'\bgiven\s*name\b',
                r'\bforename\b', r'\bname\s*\(first\)', r'\bfirst\b'
            ],
            'last_name': [
                r'\blast\s*name\b', r'\blname\b', r'\bsurname\b', r'\bfamily\s*name\b',
                r'\bname\s*\(last\)', r'\blast\b'
            ],
            'full_name': [
                r'\bfull\s*name\b', r'\bname\b', r'\bcomplete\s*name\b',
                r'\byour\s*name\b', r'\bapplicant\s*name\b'
            ],
            'email': [
                r'\bemail\b', r'\be-mail\b', r'\bemail\s*address\b',
                r'\bcontact\s*email\b', r'\bmail\b'
            ],
            'phone': [
                r'\bphone\b', r'\btelephone\b', r'\bmobile\b', r'\bcell\b',
                r'\bphone\s*number\b', r'\bcontact\s*number\b', r'\btel\b'
            ],
            'address': [
                r'\baddress\b', r'\bstreet\b', r'\bhome\s*address\b',
                r'\bmailing\s*address\b', r'\bresidential\s*address\b'
            ],
            'city': [
                r'\bcity\b', r'\btown\b', r'\blocality\b'
            ],
            'state': [
                r'\bstate\b', r'\bprovince\b', r'\bregion\b'
            ],
            'zip': [
                r'\bzip\b', r'\bpostal\s*code\b', r'\bpostcode\b', r'\bzip\s*code\b'
            ],
            'country': [
                r'\bcountry\b', r'\bnation\b', r'\bnationality\b'
            ],
            'university': [
                r'\buniversity\b', r'\bcollege\b', r'\bschool\b', r'\binstitution\b',
                r'\beducation\b', r'\balma\s*mater\b'
            ],
            'degree': [
                r'\bdegree\b', r'\bqualification\b', r'\beducation\s*level\b',
                r'\bmajor\b', r'\bfield\s*of\s*study\b'
            ],
            'graduation_year': [
                r'\bgraduation\b', r'\byear\b', r'\bgrad\s*year\b',
                r'\bcompletion\s*year\b', r'\bgraduate\s*year\b'
            ],
            'gpa': [
                r'\bgpa\b', r'\bgrade\s*point\b', r'\baverage\b', r'\bgrading\b'
            ],
            'visa_status': [
                r'\bvisa\b', r'\bwork\s*authorization\b', r'\beligibility\b',
                r'\bstatus\b', r'\bsponsorship\b'
            ],
            'salary_expectation': [
                r'\bsalary\b', r'\bcompensation\b', r'\bexpectation\b',
                r'\bexpected\s*salary\b', r'\bpay\b', r'\bwage\b'
            ],
            'start_date': [
                r'\bstart\s*date\b', r'\bavailable\b', r'\bbegin\b',
                r'\bcommence\b', r'\bstart\s*work\b'
            ],
            'linkedin': [
                r'\blinkedin\b', r'\blinked\s*in\b', r'\bprofile\b'
            ],
            'website': [
                r'\bwebsite\b', r'\bportfolio\b', r'\burl\b', r'\bhomepage\b'
            ]
        }
    
    def match_fields(self, detected_fields: List, use_ai: bool = True) -> List[FieldMatch]:
        """Match detected form fields to personal data fields"""
        matches = []
        
        for field in detected_fields:
            if use_ai and self.anthropic and field.label:
                # Use AI for intelligent matching
                ai_match = self._ai_field_matching(field.label, field.field_type)
                if ai_match:
                    matches.append(ai_match)
                    continue
            
            # Fallback to pattern matching
            pattern_match = self._pattern_field_matching(field.label or '', field.field_type)
            if pattern_match:
                matches.append(pattern_match)
        
        return matches
    
    def _ai_field_matching(self, field_label: str, field_type: str) -> Optional[FieldMatch]:
        """Use AI to intelligently match form fields"""
        try:
            prompt = f"""
            Analyze this form field and determine what personal information it's asking for:
            
            Field Label: "{field_label}"
            Field Type: {field_type}
            
            Available data fields:
            - first_name, last_name, full_name
            - email, phone
            - address, city, state, zip, country
            - university, degree, graduation_year, gpa
            - visa_status, requires_sponsorship
            - salary_expectation, start_date
            - linkedin, website
            - resume, cover_letter, transcript (for file uploads)
            
            Return the most appropriate data field name, or "unknown" if no good match.
            Also provide a confidence score (0-1) and brief reasoning.
            
            Format: data_field|confidence|reasoning
            Example: email|0.95|Clear email field label
            """
            
            response = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip()
            parts = result.split('|')
            
            if len(parts) >= 3 and parts[0] != 'unknown':
                return FieldMatch(
                    field_name=field_label,
                    data_key=parts[0].strip(),
                    confidence=float(parts[1].strip()),
                    reasoning=parts[2].strip()
                )
        
        except Exception as e:
            print(f"AI matching error: {e}")
        
        return None
    
    def _pattern_field_matching(self, field_label: str, field_type: str) -> Optional[FieldMatch]:
        """Match fields using regex patterns"""
        if not field_label:
            return None
        
        field_label_lower = field_label.lower()
        best_match = None
        best_confidence = 0.0
        
        for data_key, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, field_label_lower):
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_pattern_confidence(pattern, field_label_lower)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = FieldMatch(
                            field_name=field_label,
                            data_key=data_key,
                            confidence=confidence,
                            reasoning=f"Pattern match: {pattern}"
                        )
        
        # Special handling for file uploads
        if field_type == 'file':
            file_keywords = {
                'resume': ['resume', 'cv', 'curriculum vitae'],
                'cover_letter': ['cover letter', 'covering letter', 'motivation'],
                'transcript': ['transcript', 'grades', 'academic record']
            }
            
            for file_type, keywords in file_keywords.items():
                if any(keyword in field_label_lower for keyword in keywords):
                    return FieldMatch(
                        field_name=field_label,
                        data_key=file_type,
                        confidence=0.8,
                        reasoning=f"File upload field for {file_type}"
                    )
        
        return best_match
    
    def _calculate_pattern_confidence(self, pattern: str, field_label: str) -> float:
        """Calculate confidence score for pattern matches"""
        # Base confidence
        confidence = 0.6
        
        # Boost for exact matches
        pattern_clean = pattern.strip(r'\b').replace(r'\s*', ' ')
        if pattern_clean in field_label:
            confidence += 0.3
        
        # Boost for shorter, more specific patterns
        if len(pattern_clean) < 10:
            confidence += 0.1
        
        # Reduce for very generic patterns
        generic_patterns = [r'\bname\b', r'\baddress\b']
        if pattern in generic_patterns:
            confidence -= 0.2
        
        return min(1.0, confidence)
    
    def get_suggested_mappings(self, detected_fields: List) -> Dict[str, str]:
        """Get suggested field mappings for user review"""
        matches = self.match_fields(detected_fields)
        
        mappings = {}
        for match in matches:
            if match.confidence > 0.5:  # Only include confident matches
                mappings[match.field_name] = match.data_key
        
        return mappings
    
    def validate_field_mapping(self, field_label: str, data_key: str) -> bool:
        """Validate if a field mapping makes sense"""
        if not field_label or not data_key:
            return False
        
        # Check if the data_key exists in our patterns
        if data_key not in self.field_patterns:
            return False
        
        # Check if the field label could reasonably match the data key
        field_label_lower = field_label.lower()
        patterns = self.field_patterns[data_key]
        
        return any(re.search(pattern, field_label_lower) for pattern in patterns)