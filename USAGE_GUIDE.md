# Job Application Form Filler - Usage Guide

## 🎯 What You've Built

A complete job application automation system that can:
- Fill web forms automatically using Selenium
- Detect form fields intelligently
- Store your personal data securely
- Upload resume and documents automatically
- Show preview before submitting (safety first!)

## 🚀 Quick Start (5 Minutes)

### Step 1: Configure Your Data
1. Copy the demo data as a starting point:
   ```bash
   cp config/demo_data.json config/personal_data.json
   ```

2. Edit `config/personal_data.json` with your actual information:
   - Replace "John Doe" with your name
   - Update email, phone, address
   - Set your university and degree
   - Update file paths to your actual resume/documents

### Step 2: Install Dependencies
```bash
# Install using pip (user install)
pip install --user selenium webdriver-manager

# OR install using conda (if you prefer)
conda install selenium webdriver-manager
```

### Step 3: Test It Out
```bash
# Test with a demo site (safe to experiment)
python simple_demo.py --url "https://httpbin.org/forms/post"

# Or use interactive mode
python simple_demo.py
```

## 🎮 How to Use

### For Web Job Applications:
```bash
# Example with real job sites
python simple_demo.py --url "https://jobs.lever.co/company/apply"
python simple_demo.py --url "https://company.greenhouse.io/jobs/12345"
```

### The Process:
1. Script opens the job application page
2. Detects form fields (name, email, phone, etc.)
3. Fills them with your personal data
4. Shows you a preview
5. Lets you review and submit manually

## 🎨 Customization Options

### Advanced Features (Future Enhancements):
1. **AI Field Matching**: Add Anthropic API key for smarter field detection
2. **Screen Automation**: Add computer vision for any form on screen
3. **Site-Specific Mappings**: Create custom mappings for frequently used sites
4. **Batch Processing**: Apply to multiple jobs at once

### Add AI Field Matching:
1. Get API key from https://console.anthropic.com
2. Copy `.env.example` to `.env`
3. Add your key: `ANTHROPIC_API_KEY=your_key_here`
4. Use the full system: `python src/main.py --url "https://job-site.com"`

## 🔧 Technical Details

### What Each File Does:
- `simple_demo.py` - Basic working demo (recommended start)
- `src/main.py` - Full-featured version with AI
- `src/form_filler.py` - Core automation logic
- `src/data_manager.py` - Personal data management
- `config/personal_data.json` - Your information storage

### Supported Form Fields:
- ✅ First Name, Last Name
- ✅ Email Address
- ✅ Phone Number
- ✅ Address, City, State, ZIP
- ✅ University, Degree, Graduation Year
- ✅ File uploads (resume, cover letter)
- ✅ Dropdown selections
- ✅ Text areas
- ✅ Checkboxes and radio buttons

## 🛡️ Safety Features

1. **Always Shows Preview**: Never submits without your approval
2. **Local Data Storage**: Your info stays on your computer
3. **Manual Final Step**: You always click "Submit" yourself
4. **Graceful Failures**: Continues even if some fields can't be filled

## 🐛 Troubleshooting

### Common Issues:

**"ChromeDriver not found"**
```bash
# Install webdriver-manager
pip install --user webdriver-manager
```

**"Module not found"**
```bash
# Check your Python environment
python --version
pip list | grep selenium
```

**"No fields detected"**
- Some sites use complex JavaScript forms
- Try the manual approach first to understand the form structure
- Consider using the screen automation mode

### Browser Issues:
- Chrome must be installed
- If Chrome updates, webdriver-manager will auto-update
- Disable ad-blockers that might interfere

## 🎯 Job Application Strategy

### Best Practices:
1. **Start with simple forms** to test your configuration
2. **Review each application** before submitting
3. **Customize cover letters** manually for each role
4. **Keep your resume updated** and accessible
5. **Use different versions** of your resume for different roles

### Recommended Workflow:
1. Find job posting
2. Review requirements and customize your data if needed
3. Run the form filler
4. Review and customize the application
5. Add a personalized cover letter
6. Submit

## 📈 Next Steps

### To Make It Even Better:
1. **Add more field patterns** for specialized forms
2. **Create site-specific mappings** for your favorite job boards
3. **Integrate with job search APIs** for automated discovery
4. **Add application tracking** to manage your pipeline
5. **Build email templates** for follow-ups

### Career Automation Ideas:
- Auto-save job postings you're interested in
- Track application status and follow-up dates
- Generate cover letter templates
- Organize application materials by company

---

## 🎉 You're Ready!

Your job application automation system is now ready to save you hours of repetitive form filling. Start with the simple demo, then gradually add more advanced features as needed.

Remember: This tool handles the boring stuff so you can focus on what matters - finding the right opportunities and crafting compelling applications!

**Happy job hunting! 🚀**