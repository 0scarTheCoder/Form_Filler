# Job Application Form Filler

Automate the tedious process of filling out job application forms with your personal information. This tool uses computer vision and web automation to detect form fields and fill them with your pre-configured data.

## Features

- **Web Form Automation**: Fill forms on job sites using Selenium WebDriver
- **Screen Form Detection**: Use computer vision to detect and fill any form on screen
- **Intelligent Field Matching**: AI-powered field identification using Anthropic Claude
- **Secure Data Storage**: Encrypted storage of personal information
- **File Upload Automation**: Automatic upload of resume, cover letter, and transcripts
- **Safety First**: Always shows preview before submitting forms
- **Multi-Site Support**: Works with LinkedIn, Indeed, and other job sites

## Installation

1. Clone this repository:
```bash
git clone https://github.com/0scarTheCoder/Form_Filler.git
cd Form_Filler
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up configuration:
```bash
python src/main.py --setup
```

5. (Optional) For AI field matching, set up your Anthropic API key:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Quick Start

1. **Set up your personal data**:
```bash
python src/main.py --setup
```
This will create `config/personal_data.json` where you can enter your information.

2. **Fill a web form**:
```bash
python src/main.py --url "https://example.com/job-application"
```

3. **Fill any form on screen**:
```bash
python src/main.py --screen
```

## Usage

### Command Line Interface

```bash
# Interactive mode
python src/main.py

# Fill a specific URL
python src/main.py --url "https://jobs.company.com/apply"

# Screen form filling
python src/main.py --screen

# Create custom mapping for a site
python src/main.py --create-mapping "https://jobs.company.com"

# Use with AI field matching
python src/main.py --url "https://example.com" --anthropic-key "your-key"
```

### Configuration

Edit `config/personal_data.json` with your information:

```json
{
  "personal_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "(555) 123-4567",
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "country": "USA"
    }
  },
  "files": {
    "resume_path": "/path/to/your/resume.pdf",
    "cover_letter_path": "/path/to/your/cover_letter.pdf"
  }
}
```

## How It Works

1. **Web Forms**: Uses Selenium to detect form fields and their labels, then matches them to your personal data
2. **Screen Forms**: Captures screenshots, uses OCR to read field labels, and PyAutoGUI to fill fields
3. **Field Matching**: Combines regex patterns and AI analysis to determine what information each field needs
4. **Safety**: Always shows a preview of what will be filled before taking action

## Security & Privacy

- Personal data is stored locally in encrypted JSON files
- No data is sent to external services (except optional AI field matching)
- Always review forms before submission
- Supports headless mode for privacy

## Limitations

- Requires manual review before form submission (by design for safety)
- May not work with heavily JavaScript-dependent forms
- Screen mode requires good contrast and readable text
- Some sites may detect automation and block the tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Legal Notice

This tool is for personal use only. Always respect website terms of service and use responsibly. The authors are not responsible for any misuse of this software.

## License

MIT License - see LICENSE file for details.
