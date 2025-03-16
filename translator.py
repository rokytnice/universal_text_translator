import os
import pdfplumber
import textwrap
import time
import logging
from google.generativeai import GenerativeModel, configure

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up API key and language
API_KEY = os.getenv("API_KEY")
LANGUAGE = "de"

def configure_genai():
    """
    Configures the Generative AI model.
    """
    if not API_KEY:
        logging.error("API key not found in environment variables.")
        return None
    configure(api_key=API_KEY)
    return GenerativeModel("gemini-1.5-flash")

def get_translation_with_genai(model, content):
    """
    Uses the Generative AI model to perform translations.
    Returns the translation and the character counts for input and output.
    """
    logging.info("Generating translation with Google Gemini API.")
    try:
        response = model.generate_content(f"Translate the following text to {LANGUAGE}: {content}")
        response_text = response.text
        logging.info("Translation received: %s", response_text)
        return response_text, len(content), len(response_text)
    except Exception as e:
        logging.error("Error during translation: %s", e)
        return "Error in translation.", len(content), 0

def find_files(pattern):
    """Finds files in the current directory that match the given pattern."""
    logging.info("Searching for files matching pattern: %s", pattern)
    return [file for file in os.listdir('.') if file.endswith(pattern)]

def read_pdf_pages(pdf_file, start_page=1, end_page=None):
    """Reads pages from a PDF file and returns the text of each page using pdfplumber."""
    logging.info("Opening PDF file: %s", pdf_file)
    with pdfplumber.open(pdf_file) as pdf:
        total_pages = len(pdf.pages)
        end_page = end_page or total_pages
        if start_page > end_page:
            logging.warning("Invalid range: Start page %d is greater than end page %d", start_page, end_page)
            return
        for index in range(start_page - 1, min(end_page, total_pages)):
            logging.info("Reading page %d", index + 1)
            text = pdf.pages[index].extract_text() or ""
            if not text:
                logging.warning("Page %d contains no extractable text. Skipping...", index + 1)
                continue
            yield index + 1, text

def create_target_document_stream(source_file, language):
    """Creates a target text document using a write stream and writes pages incrementally."""
    target_file = source_file.replace('.pdf', f'_{language}.txt')
    logging.info("Creating target document: %s", target_file)
    return open(target_file, 'a', encoding='utf-8')

def write_page_to_document(file_stream, page_number, translated_text):
    """Writes a single page's translated text to the target document."""
    file_stream.write(f"--- Page {page_number} ---\n")
    for line in textwrap.wrap(translated_text, width=80):
        file_stream.write(line + "\n")
    file_stream.write("\n")

def throttle_request(last_request_time, min_interval=6):
    """Ensures a minimum interval between requests."""
    elapsed_time = time.time() - last_request_time
    if elapsed_time < min_interval:
        sleep_time = min_interval - elapsed_time
        logging.info("Throttling request for %.2f seconds.", sleep_time)
        time.sleep(sleep_time)

if __name__ == "__main__":
    language = input("Enter the target language (e.g., 'de' for German, default: 'de'): ") or "de"
    LANGUAGE = language
    range_input = input("Enter the page range (e.g., '1-3', '2', or leave blank for all pages): ")

    if "-" in range_input:
        start_page, end_page = map(int, range_input.split("-"))
    elif range_input.isdigit():
        start_page, end_page = int(range_input), int(range_input)
    else:
        start_page, end_page = 1, None

    pdf_files = find_files('.pdf')

    if not pdf_files:
        logging.warning("No PDF files found in the current directory.")
    else:
        model = configure_genai()
        if not model:
            exit(1)

        last_request_time = 0
        for pdf_file in pdf_files:
            logging.info("Processing file: %s", pdf_file)

            with create_target_document_stream(pdf_file, language) as target_stream:
                for page_number, page_text in read_pdf_pages(pdf_file, start_page, end_page):
                    throttle_request(last_request_time)
                    last_request_time = time.time()

                    translated_text, original_chars, translated_chars = get_translation_with_genai(model, page_text)
                    logging.info(
                        "Page %d: Original characters: %d, Translated characters: %d",
                        page_number, original_chars, translated_chars
                    )
                    write_page_to_document(target_stream, page_number, translated_text)

            logging.info("Translation completed. Incremental results saved in: %s", pdf_file.replace('.pdf', f'_{language}.txt'))
