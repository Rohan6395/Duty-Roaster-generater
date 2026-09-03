# Development & Testing Guide

This guide is for developers working on the Duty Roster Generator locally.

## Local Development Setup

### 1. Initial Setup

```bash
# Clone repository (if not done)
git clone https://github.com/YOUR_USERNAME/duty-roster-generator.git
cd "Duty Roster Generator"

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Create `.streamlit/secrets.toml`:

```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

4. Edit `.streamlit/secrets.toml` and add your key:

```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
GEMINI_MODEL = "gemini-2.0-flash"
```

### 3. Run Locally

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

## Project Structure

```
app.py                      # Main Streamlit app
config/
  └── settings.py          # Configuration management
  
src/
  ├── ai/
  │   ├── gemini_client.py       # Gemini API wrapper
  │   └── roster_extractor.py    # Handwriting → JSON
  │
  ├── models/
  │   └── roster.py              # Pydantic data models
  │
  ├── pdf/
  │   ├── pdf_editor.py          # PDF manipulation
  │   ├── pdf_renderer.py        # PDF → Image preview
  │   ├── coordinate_mapper.py   # Template coordinates
  │   └── template_detector.py   # Auto-detect templates
  │
  ├── services/
  │   └── roster_service.py      # Business logic
  │
  ├── utils/
  │   ├── file_utils.py          # File I/O
  │   └── image_utils.py         # Image preprocessing
  │
  └── validation/
      ├── roster_validator.py    # Roster data validation
      └── calendar_validator.py  # Date/calendar validation

templates/
  ├── nursing_officer.yaml       # Nursing Officer template
  └── ward_boy_aya.yaml          # Ward Boy template

tests/
  ├── test_models.py
  ├── test_validation.py
  └── test_calendar.py

.streamlit/
  ├── config.toml               # Streamlit settings
  └── secrets.toml              # API keys (local only)

prompts/
  └── roster_extraction_prompt.txt  # Gemini system prompt
```

## Key Files to Understand

### `app.py` — Streamlit UI
- Main entry point
- Handles file uploads
- Manages UI flow
- Calls services for business logic

### `src/ai/roster_extractor.py` — Handwriting Extraction
- Loads images
- Calls Gemini Vision API
- Parses JSON response
- Returns RosterData

### `src/pdf/pdf_editor.py` — PDF Generation
- Loads reference PDF
- Clears table areas
- Fills with extracted data
- Uses template coordinates

### `config/settings.py` — Configuration
- Loads from environment
- Streamlit secrets integration
- All settings in one place

### `templates/*.yaml` — Template Definitions
- Table row positions
- Column coordinates
- Preserve vs. editable regions
- Auto-detection keywords

## Testing Locally

### Run Unit Tests

```bash
pytest tests/
pytest tests/test_models.py -v
pytest tests/test_validation.py -v
pytest tests/test_calendar.py -v
```

### Test Manually with UI

1. Run `streamlit run app.py`
2. Select template type
3. Upload a reference PDF (use `templates/` PDFs for testing)
4. Upload a roster photo
5. Watch extraction and PDF generation

### Test Data Extraction Only (No UI)

Create a test script:

```python
from pathlib import Path
from src.ai.roster_extractor import RosterExtractor
from config.settings import get_settings

# Load prompt
prompt = Path("prompts/roster_extraction_prompt.txt").read_text()

# Extract
extractor = RosterExtractor()
roster = extractor.extract(
    image_paths=[Path("test_image.jpg")],
    prompt_text=prompt
)

print(f"Month: {roster.month}")
print(f"Year: {roster.year}")
print(f"Staff: {len(roster.staff)}")
for staff in roster.staff:
    print(f"  - {staff.name} ({staff.post})")
```

### Test PDF Generation Only

```python
from pathlib import Path
from src.pdf.pdf_editor import PdfEditor
from src.models.roster import RosterData, StaffRoster

# Create test data
roster = RosterData(
    hospital_name="Test Hospital",
    roster_title="Nursing Officer",
    month=12,
    year=2024,
    total_days=31,
    staff=[
        StaffRoster(
            serial_number=1,
            name="JOHN DOE",
            post="SENIOR",
            duties={1: "M", 2: "E", 3: "N", 4: "D/O"}
        )
    ]
)

# Generate PDF
editor = PdfEditor()
output_pdf = Path("output.pdf")
result = editor.generate_roster_pdf(
    reference_pdf=Path("templates/sample.pdf"),
    roster_data=roster,
    template_id="nursing_officer",
    output_pdf=output_pdf
)

print(f"PDF generated: {result}")
```

## Debugging

### Enable Verbose Logging

In `.streamlit/secrets.toml`:
```toml
LOG_LEVEL = "DEBUG"
```

### Streamlit Debugging

Press `C` in terminal while app is running to see execution details.

### Gemini API Debugging

```python
import google.generativeai as genai
from config.settings import get_secret_or_env

key = get_secret_or_env("GEMINI_API_KEY")
genai.configure(api_key=key)

# Test API
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Hello!")
print(response.text)
```

### PDF Coordinate Debugging

To understand PDF coordinates:

```python
import fitz
from pathlib import Path

pdf_path = Path("your_pdf.pdf")
with fitz.open(pdf_path) as doc:
    page = doc[0]
    print(f"Page size: {page.rect}")  # (0, 0, width, height)
    text = page.get_text()
    print(text[:500])  # First 500 chars
```

Use this to calibrate template coordinates.

## Common Issues During Development

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"

Ensure `.streamlit/secrets.toml` exists with valid key:

```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# Edit and add real key
```

### "Template not found"

Check:
- Template file exists: `templates/nursing_officer.yaml`
- Template ID in code matches filename
- YAML syntax is valid

Validate YAML:
```python
import yaml
with open("templates/nursing_officer.yaml") as f:
    data = yaml.safe_load(f)
    print(data)
```

### "Image not preprocessed correctly"

Check `src/utils/image_utils.py`:
- EXIF rotation is being applied
- Image size is within MAX_IMAGE_SIDE

Test preprocessing:
```python
from src.utils.image_utils import preprocess_image_for_ai
from pathlib import Path

input_img = Path("test.jpg")
output_img = Path("test_preprocessed.jpg")
preprocess_image_for_ai(input_img, output_img)
```

### Pydantic Validation Errors

The RosterData model validates:
- Month: 1-12
- Year: 1900-2100
- Days: 28-31
- Duty codes: normalized (D/O → D/O)

If extraction fails validation, check:
- Gemini response format (must be valid JSON)
- Data types match (month must be int, not string)
- Range constraints are met

## Making Changes

### Add New Template

1. Copy `templates/nursing_officer.yaml`
2. Rename to `templates/new_template.yaml`
3. Update template_id, display_name, keywords
4. Adjust coordinates for your PDF layout
5. Restart app to see new template in dropdown

### Modify Gemini Prompt

Edit `prompts/roster_extraction_prompt.txt` and restart app.

### Add New Validation

Add methods to `src/validation/` classes and import in `src/models/roster.py`.

### Update PDF Editor Algorithm

Modify `src/pdf/pdf_editor.py` method `_edit_pdf_with_roster()`.

## Deployment Checklist

Before pushing to GitHub:

- [ ] `pytest tests/` passes
- [ ] `streamlit run app.py` works locally
- [ ] No hardcoded API keys (use secrets)
- [ ] `.gitignore` blocks `secrets.toml`, `tmp/`, `.venv/`
- [ ] README.md is complete
- [ ] No `*.pdf` or test images in repo
- [ ] All dependencies in `requirements.txt`
- [ ] Code is clean (no debug prints)

## Useful Commands

```bash
# Run app
streamlit run app.py

# Run tests
pytest tests/ -v

# Check Python version
python --version

# List installed packages
pip list

# Generate requirements
pip freeze > requirements.txt

# Clean temp files
rmdir /s tmp
find . -type d -name __pycache__ -exec rm -r {} +
```

## Performance Tips

- Use `@st.cache_data` for expensive operations
- Preprocess images before AI (already done)
- Consider rate limiting for API calls
- Optimize PDF coordinate calculations

## Security Checklist

- [ ] API keys never in code
- [ ] Secrets in `.streamlit/secrets.toml` (git-ignored)
- [ ] No user data stored
- [ ] Validation on all inputs
- [ ] No SQL injection risks (not using DB)
- [ ] CORS properly configured

## Next Steps

1. Test locally with real roster images
2. Fine-tune template coordinates
3. Add more templates
4. Deploy to Streamlit Cloud
5. Gather user feedback
6. Iterate on improvements

Happy developing! 🚀
