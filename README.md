# PDF Translator

A Python tool to translate PDF and EPUB documents page by page or chapter by chapter. Translation is performed via the Google Gemini API (`google-generativeai`). The result is saved as a text file.

## Features
- Reads PDF or EPUB files from the current directory
- Translates each page (PDF) or chapter (EPUB) into the desired language
- Saves the translation in a new text file with the same base name as the original
- Language and model are configurable (default: German, `gemini-1.5-flash-lite-preview-06-17`)
- Extensive logging for each processing step
- API key is read from the `API_KEY` environment variable
- Supports range translation (e.g., only specific pages)
- Shows the number of characters sent and received per page

## Requirements
- Python 3.8+
- Virtual environment recommended
- Install dependencies from `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## API Key
Set your Google Gemini API key as an environment variable:

```bash
export API_KEY=YOUR_API_KEY
```

## Usage
The main script is `translator.py`.

```bash
python3 translator.py
```

You will be prompted for language and page range if needed.

### Example: Language and Range
- Language: `de` (default) or e.g. `en` for English
- Page range: `3-7` for pages 3 to 7, leave blank for all pages

## Logging and Error Handling
All steps are logged. Errors are displayed clearly.

## Notes
- The result file gets the same name as the original, with the language code before the extension (e.g., `myfile_de.txt`).
- The model can be overridden via the `GOOGLE_LLM` environment variable.
- The script also supports EPUB files.

## License
MIT

---

For feedback or feature requests, please get in touch.