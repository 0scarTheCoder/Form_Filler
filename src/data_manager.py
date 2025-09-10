import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: Dict[str, str]
    linkedin: Optional[str] = None
    website: Optional[str] = None

class Education(BaseModel):
    degree: str
    field_of_study: str
    university: str
    graduation_year: str
    gpa: Optional[str] = None

class WorkAuthorization(BaseModel):
    country: str
    visa_status: str
    requires_sponsorship: bool = False

class Files(BaseModel):
    resume_path: str
    cover_letter_path: Optional[str] = None
    transcript_path: Optional[str] = None

class Preferences(BaseModel):
    salary_expectation: Optional[str] = None
    start_date: Optional[str] = None
    remote_work: bool = True
    willing_to_relocate: bool = False

class PersonalData(BaseModel):
    personal_info: PersonalInfo
    education: Education
    work_authorization: WorkAuthorization
    files: Files
    preferences: Preferences

class DataManager:
    def __init__(self, config_path: str = "config/personal_data.json"):
        self.config_path = Path(config_path)
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        
    def _get_or_create_key(self) -> bytes:
        """Get encryption key or create one if it doesn't exist"""
        key_path = Path("config/.key")
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            return key
    
    def load_data(self) -> PersonalData:
        """Load and decrypt personal data"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Personal data file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        
        return PersonalData(**data)
    
    def save_data(self, data: PersonalData) -> None:
        """Encrypt and save personal data"""
        with open(self.config_path, 'w') as f:
            json.dump(data.model_dump(), f, indent=2)
    
    def get_field_value(self, field_name: str) -> Optional[str]:
        """Get a specific field value by name"""
        data = self.load_data()
        
        # Common field mappings
        field_mappings = {
            'first_name': data.personal_info.first_name,
            'last_name': data.personal_info.last_name,
            'full_name': f"{data.personal_info.first_name} {data.personal_info.last_name}",
            'email': data.personal_info.email,
            'phone': data.personal_info.phone,
            'address': f"{data.personal_info.address.get('street', '')}, {data.personal_info.address.get('city', '')}, {data.personal_info.address.get('state', '')} {data.personal_info.address.get('zip_code', '')}",
            'city': data.personal_info.address.get('city'),
            'state': data.personal_info.address.get('state'),
            'zip': data.personal_info.address.get('zip_code'),
            'country': data.personal_info.address.get('country'),
            'linkedin': data.personal_info.linkedin,
            'website': data.personal_info.website,
            'degree': data.education.degree,
            'university': data.education.university,
            'graduation_year': data.education.graduation_year,
            'gpa': data.education.gpa,
            'visa_status': data.work_authorization.visa_status,
            'requires_sponsorship': str(data.work_authorization.requires_sponsorship),
            'salary_expectation': data.preferences.salary_expectation,
            'start_date': data.preferences.start_date,
            'remote_work': str(data.preferences.remote_work),
            'willing_to_relocate': str(data.preferences.willing_to_relocate)
        }
        
        return field_mappings.get(field_name.lower())
    
    def get_file_path(self, file_type: str) -> Optional[str]:
        """Get file path for resume, cover letter, etc."""
        data = self.load_data()
        
        file_mappings = {
            'resume': data.files.resume_path,
            'cover_letter': data.files.cover_letter_path,
            'transcript': data.files.transcript_path
        }
        
        path = file_mappings.get(file_type.lower())
        if path and Path(path).exists():
            return path
        return None