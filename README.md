# Hospital Duty Roster Generator

Convert handwritten hospital duty rosters into clean, professional single-page PDFs using AI-powered handwriting recognition and template-aware PDF generation.

## Features

✅ **Handwriting Recognition** — Uses Google Gemini Vision API (free tier) to accurately read handwritten rosters  
✅ **Template-Based** — Supports multiple roster formats (Nursing Officer, Ward Boy/Aya, etc.)  
✅ **One-Click PDF** — Automatically fills in handwritten data into your reference PDF template  
✅ **Web Interface** — Simple Streamlit interface accessible on any browser (mobile-friendly)  
✅ **Free Deployment** — Deployed on Streamlit Community Cloud (completely free)  
✅ **Zero Manual Entry** — No copy-pasting or manual data entry required  

## Quick Start

### Local Development

```bash
# Clone or navigate to project
cd "Duty Roster Generator"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create secrets file
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# Edit .streamlit\secrets.toml and add your GEMINI_API_KEY

# Run app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Deploy to Streamlit Community Cloud

1. **Get a Gemini API Key** (Free)
   - Go to [Google AI Studio](https://aistudio.google.com/apikey)
   - Click "Create API Key"
   - Copy the key

2. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/duty-roster-generator.git
   git push -u origin main
   ```

3. **Deploy on Streamlit Community Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app" → Select your GitHub repo
   - Select `main` branch and `app.py` as the main file
   - Click "Deploy"

4. **Add Secrets in Streamlit Cloud**
   - Go to your app's settings (gear icon)
   - Click "Secrets"
   - Paste your secrets in TOML format:
     ```toml
     GEMINI_API_KEY = "your-api-key-here"
     GEMINI_MODEL = "gemini-2.0-flash"
     ```
   - Save and your app will auto-reload

## Usage

Your father (or any user) simply:

1. **Choose Template** — Select "Nursing Officer" or "Ward Boy / Aya" (or auto-detect)
2. **Upload Reference PDF** — Select a blank/template PDF from your roster system
3. **Upload Photo** — Take a clear photo of the handwritten roster
4. **Extract** — Click "Extract Roster Data" and watch the magic happen
5. **Preview** — Review the extracted data in the preview table
6. **Generate** — Click "Generate PDF" to create the final output
7. **Download** — One-click download of the finished PDF

## How It Works

```
Handwritten Photo
       ↓
   Gemini Vision API
   (Free Tier)
       ↓
Extracted Roster Data
(JSON with staff, dates, duties)
       ↓
PDF Template
Matching
       ↓
PyMuPDF (fitz) fills
reference PDF with
new data
       ↓
Clean Single-Page PDF
```

## Project Structure

```
.streamlit/          # Streamlit configuration
  config.toml       # UI theme and settings
  secrets.toml      # API keys (local only, not in git)
  
config/
  settings.py       # App configuration & settings management
  
prompts/
  roster_extraction_prompt.txt  # Gemini AI system prompt
  
src/
  ai/
    gemini_client.py          # Gemini API wrapper
    roster_extractor.py       # Handwriting extraction logic
    
  models/
    roster.py                 # Data models for roster, staff, duties
    
  pdf/
    pdf_editor.py            # PDF manipulation & filling
    pdf_renderer.py          # PDF preview rendering
    coordinate_mapper.py     # Template coordinate utilities
    template_detector.py     # Template auto-detection
    
  services/
    roster_service.py        # Business logic orchestration
    
  utils/
    file_utils.py           # File I/O helpers
    image_utils.py          # Image preprocessing
    
  validation/
    roster_validator.py     # Data validation
    calendar_validator.py   # Date/calendar validation
    
templates/                   # Template definitions
  nursing_officer.yaml
  ward_boy_aya.yaml
  
tests/                       # Unit tests
  test_calendar.py
  test_models.py
  test_validation.py

app.py                       # Main Streamlit app
requirements.txt            # Python dependencies
```

## Configuration

### Environment Variables

These can be set locally in `.streamlit/secrets.toml` or in Streamlit Cloud secrets:

```toml
GEMINI_API_KEY = "your-api-key"           # Required: Gemini API key from Google AI Studio
GEMINI_MODEL = "gemini-2.0-flash"         # Optional: Model name (default: gemini-2.0-flash)
LOG_LEVEL = "INFO"                        # Optional: Logging level
MAX_IMAGE_SIDE = 2200                     # Optional: Max image dimension for preprocessing
MIN_FONT_SIZE = 6                         # Optional: Minimum font size in PDF
PREFERRED_FONT_SIZE = 10                  # Optional: Default font size in PDF
```

### Template Configuration

Each template YAML file defines:
- Template ID and display name
- Table structure (row positions, column widths)
- Editable regions (staff table, dates)
- Preserved regions (signatures, important notes)

Example: `templates/nursing_officer.yaml`

```yaml
template_id: nursing_officer
display_name: Nursing Officer
match_keywords:
  - NURSING OFFICER
  - DUTY ROSTER

table:
  row_start_y: 170        # Y position of first staff row
  row_height: 22          # Height of each row
  max_staff_rows: 20      # Maximum staff rows to process
  columns:
    serial: {x0: 28, x1: 58}
    name: {x0: 58, x1: 198}
    post: {x0: 198, x1: 250}
    first_day_x: 250      # X start for days
    day_col_width: 12     # Width of each day column

regions:
  preserve:
    - name: signature_area
      x0: 360
      y0: 640
      x1: 570
      y1: 820
```

## Data Model

The extracted roster is a structured JSON:

```json
{
  "hospital_name": "Central Hospital",
  "roster_title": "Nursing Officer",
  "month": 12,
  "year": 2024,
  "total_days": 31,
  "staff": [
    {
      "serial_number": 1,
      "name": "RAJESH KUMAR",
      "post": "SENIOR",
      "duties": {
        "1": "M",
        "2": "E",
        "3": "N",
        "4": "D/O",
        ...
      }
    }
  ],
  "uncertain_cells": [
    {
      "staff_name": "RAJESH KUMAR",
      "day": 5,
      "detected_value": "M?",
      "reason": "handwriting unclear",
      "confidence": 0.45
    }
  ]
}
```

Common duty codes:
- `M` — Morning shift
- `E` — Evening shift
- `N` — Night shift
- `D/O` — Day off
- `N/O` — Night off
- `L` — Leave
- Empty string `""` — No entry

## Free Tier Limits

### Gemini API (Free)
- 15 requests per minute
- 1.5 million tokens per day
- Supports image input
- Perfect for a few rosters per month

### Streamlit Community Cloud (Free)
- Deploy unlimited apps
- 1 GB storage
- Runs 24/7
- No credit card required
- Shareable web URL

## Troubleshooting

### "Gemini API key not configured"
- Check that `GEMINI_API_KEY` is set in Streamlit secrets
- Local: Edit `.streamlit/secrets.toml`
- Cloud: Go to app settings → Secrets

### "Template not detected"
- Ensure PDF contains text matching template keywords
- Manually select the correct template
- Check that template YAML file exists in `templates/` folder

### "Extraction failed" or "Could not read handwritten roster"
- Ensure image is clear and well-lit
- Avoid shadows, glare, or extreme angles
- Use straight-on photos for best results
- Handwriting should be legible (not too faint)

### PDF appears blank
- Verify reference PDF is a single-page roster format
- Check template coordinates match your PDF layout
- Review console logs for coordinate mapping issues

## Next Steps & Improvements

- [ ] Support for multi-page rosters
- [ ] Edit extracted data before PDF generation (if-needed)
- [ ] Batch processing for multiple months
- [ ] Historical archive of rosters
- [ ] Email PDF delivery option
- [ ] OCR confidence filtering
- [ ] Support for more template variants

## Deployment Checklist

Before deploying to Streamlit Cloud:

- [ ] GitHub repository created and pushed
- [ ] `requirements.txt` contains all dependencies
- [ ] `.gitignore` includes `.env`, `.venv/`, `tmp/`, `__pycache__/`
- [ ] `.streamlit/secrets.toml.example` created (without actual keys)
- [ ] Gemini API key obtained from Google AI Studio
- [ ] README updated with deployment instructions
- [ ] App tested locally with `streamlit run app.py`

## Architecture & Technologies

- **Frontend**: [Streamlit](https://streamlit.io) — Python web framework for data apps
- **Handwriting AI**: [Google Gemini Vision API](https://ai.google.dev) — Free-tier multimodal AI
- **PDF Processing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io) — PDF reading and manipulation
- **Data Validation**: [Pydantic](https://pydantic-ai.jinja2.org) — Type-safe data models
- **Deployment**: [Streamlit Community Cloud](https://streamlit.io/cloud) — Free Python app hosting

## License

MIT License — Feel free to use, modify, and distribute.

## Support

For issues, questions, or feature requests:
1. Check the Troubleshooting section above
2. Review app console logs (visible in Streamlit)
3. Ensure Gemini API key is valid and has quota remaining
4. Test with a different roster image
5. Verify template coordinates match your PDF format

