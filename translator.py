import os
import pdfplumber
import textwrap
import time
import logging
from google.generativeai import GenerativeModel, configure
from ebooklib import epub, ITEM_DOCUMENT  # Added for EPUB
from bs4 import BeautifulSoup  # Added for parsing EPUB HTML content

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up API key and language (default)
API_KEY = os.getenv("API_KEY")
LANGUAGE = "de"  # Default language, can be overridden by user input


def configure_genai():
    """
    Configures the Generative AI model.
    """
    if not API_KEY:
        logging.error("API key not found in environment variables.")
        return None
    configure(api_key=API_KEY)

    # Use the model from the GEMINI_LLM env var, or the specified default
    default_model = "gemini-1.5-flash-lite-preview-06-17"
    model_name = os.getenv("GEMINI_LLM", default_model)

    logging.info(f"Using Generative AI model: {model_name}")

    return GenerativeModel(model_name)


def get_translation_with_genai(model, content):
    """
    Uses the Generative AI model to perform translations.
    Returns the translation and the character counts for input and output.
    """
    logging.info("Generating translation with Google Gemini API.")
    try:
        # Use the global LANGUAGE variable, which is updated by user input
        response = model.generate_content(f"Translate the following text to {LANGUAGE}: {content}")
        response_text = response.text
        logging.info("Translation received: %s", response_text)
        return response_text, len(content), len(response_text)
    except Exception as e:
        logging.error("Error during translation: %s", e)
        return "Error in translation.", len(content), 0


def find_files(extensions, root_dir='.'):
    """Finds files recursively in the given directory that match any of the given extensions."""
    if isinstance(extensions, str):
        extensions = [extensions]
    logging.info(f"Recursively searching for files in '{root_dir}' matching extensions: {extensions}")
    found_files = []
    for root, _, files in os.walk(root_dir):
        for file_name in files:
            if any(file_name.lower().endswith(ext.lower()) for ext in extensions):
                full_path = os.path.join(root, file_name)
                found_files.append(full_path)
    return found_files

def read_pdf_pages(pdf_file, start_page=1, end_page=None):
    """Reads pages from a PDF file and returns the text of each page using pdfplumber."""
    logging.info("Opening PDF file: %s", pdf_file)
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            # Adjust end_page: if None, use total_pages; ensure it's not less than start_page
            end_page = end_page if end_page is not None else total_pages

            if start_page < 1:
                logging.warning("Start page must be 1 or greater. Adjusting to 1.")
                start_page = 1

            if start_page > end_page and end_page is not None:  # end_page could be 0 if total_pages is 0
                logging.warning(
                    "Invalid page range for PDF: Start page %d is greater than end page %d (Total pages: %d). No pages will be processed.",
                    start_page, end_page, total_pages
                )
                return

            if start_page > total_pages and total_pages > 0:
                logging.warning(
                    "Start page %d is greater than total pages %d. No pages will be processed.",
                    start_page, total_pages
                )
                return

            if total_pages == 0:
                logging.warning("PDF file %s has 0 pages.", pdf_file)
                return

            # Iterate from start_page-1 up to min(end_page, total_pages)
            for index in range(start_page - 1, min(end_page, total_pages)):
                logging.info("Reading page %d from PDF", index + 1)
                page = pdf.pages[index]
                text = page.extract_text(x_tolerance=1, y_tolerance=1) or ""  # Added tolerance for better extraction
                if not text.strip():
                    logging.warning("Page %d (PDF) contains no extractable text. Skipping...", index + 1)
                    continue
                yield index + 1, text
    except Exception as e:
        logging.error(f"Error reading PDF file {pdf_file}: {e}")
        return


def read_epub_pages(epub_file, start_item=1, end_item=None):
    """Reads content documents (items) from an EPUB file and returns the text of each item."""
    logging.info("Opening EPUB file: %s", epub_file)
    try:
        book = epub.read_epub(epub_file)
    except Exception as e:
        logging.error(f"Error opening or parsing EPUB file {epub_file}: {e}")
        return

    # Get all content documents (typically chapters or sections)
    content_items = [item for item in book.get_items_of_type(ITEM_DOCUMENT)]
    total_items = len(content_items)

    if total_items == 0:
        logging.warning("EPUB file %s contains no content documents.", epub_file)
        return

    # Adjust end_item: if None, use total_items
    end_item = end_item if end_item is not None else total_items

    if start_item < 1:
        logging.warning("Start item must be 1 or greater. Adjusting to 1.")
        start_item = 1

    if start_item > end_item:
        logging.warning(
            "Invalid item range for EPUB: Start item %d is greater than end item %d (Total items: %d). No items will be processed.",
            start_item, end_item, total_items
        )
        return

    if start_item > total_items:
        logging.warning(
            "Start item %d is greater than total items %d in EPUB. No items will be processed.",
            start_item, total_items
        )
        return

    # Iterate from start_item-1 up to min(end_item, total_items)
    # The user provides 1-based input, so adjust for 0-based indexing
    for index in range(start_item - 1, min(end_item, total_items)):
        item = content_items[index]
        item_number_for_user = index + 1  # This is the 1-based "page" number for output
        logging.info("Reading item %d from EPUB (content: %s)", item_number_for_user, item.get_name())
        try:
            # Decode content if it's bytes (common for EPUB items)
            html_content = item.get_content()
            if isinstance(html_content, bytes):
                html_content = html_content.decode('utf-8', errors='ignore')

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract text, joining paragraphs with newlines
            paragraphs = [p.get_text(strip=True) for p in
                          soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])]
            text = "\n".join(filter(None, paragraphs)) or ""  # Filter out empty strings

            if not text.strip():  # Check if text is empty after stripping whitespace
                logging.warning("Item %d (EPUB: %s) contains no extractable text. Skipping...", item_number_for_user,
                                item.get_name())
                continue
            yield item_number_for_user, text
        except Exception as e:
            logging.error(
                f"Error extracting text from item {item_number_for_user} ({item.get_name()}) in {epub_file}: {e}")
            continue


def create_target_document_stream(source_file, target_language):
    """Creates a target text document using a write stream and writes pages incrementally."""
    base, _ = os.path.splitext(source_file)  # Get filename without extension
    target_file = f"{base}_{target_language}.txt"
    logging.info("Creating target document: %s", target_file)
    # Use 'w' to overwrite if exists, or 'a' to append. 'w' is safer for new runs.
    # If appending is desired for partial runs, change to 'a'.
    # For this script, 'w' makes more sense to avoid duplicate content on re-runs.
    # However, the original used 'a', so let's stick to that for incremental writes per file.
    # If processing multiple files, each gets its own new/appended file.
    return open(target_file, 'a', encoding='utf-8')


def write_page_to_document(file_stream, item_number, translated_text):
    """Writes a single item's (page/EPUB section) translated text to the target document."""
    file_stream.write(f"--- Item {item_number} ---\n")  # Changed "Page" to "Item" for generality
    for line in textwrap.wrap(translated_text, width=80):
        file_stream.write(line + "\n")
    file_stream.write("\n")


def throttle_request(last_request_time, min_interval=6):  # 6 seconds for ~10 RPM (Gemini Flash free tier limit)
    """Ensures a minimum interval between requests."""
    elapsed_time = time.time() - last_request_time
    if elapsed_time < min_interval:
        sleep_time = min_interval - elapsed_time
        logging.info("Throttling request for %.2f seconds.", sleep_time)
        time.sleep(sleep_time)


if __name__ == "__main__":
    # User input for language
    user_lang_input = input(f"Enter the target language (e.g., 'de' for German, default: '{LANGUAGE}'): ")
    if user_lang_input.strip():
        LANGUAGE = user_lang_input.strip().lower()
    logging.info(f"Target language set to: {LANGUAGE}")

    # User input for page/item range
    range_input_str = input("Enter the page/item range (e.g., '1-3', '5', or leave blank for all): ")
    start_processing_item, end_processing_item = 1, None  # Default: process all

    if "-" in range_input_str:
        try:
            start_str, end_str = range_input_str.split("-")
            start_processing_item = int(start_str)
            end_processing_item = int(end_str)
        except ValueError:
            logging.warning("Invalid range format. Defaulting to all pages/items.")
    elif range_input_str.isdigit():
        try:
            start_processing_item = int(range_input_str)
            end_processing_item = int(range_input_str)  # Process a single page/item
        except ValueError:
            logging.warning("Invalid page/item number. Defaulting to all pages/items.")

    logging.info(
        f"Processing range: Start item {start_processing_item}, End item {'All' if end_processing_item is None else end_processing_item}")

    supported_extensions = ['.pdf', '.epub']
    source_files = find_files(supported_extensions)

    if not source_files:
        logging.warning(f"No PDF or EPUB files found in the current directory with extensions: {supported_extensions}")
    else:
        model = configure_genai()
        if not model:
            exit(1)  # API key or model configuration failed

        total_files = len(source_files)
        logging.info(f"Found {total_files} file(s) to process: {source_files}")

        for i, source_file in enumerate(source_files):
            logging.info(f"Processing file {i + 1}/{total_files}: {source_file}")

            # Determine target filename for logging completion
            base_name, _ = os.path.splitext(source_file)
            target_output_filename = f"{base_name}_{LANGUAGE}.txt"

            # Check if target file already exists and ask user if they want to overwrite or skip
            if os.path.exists(target_output_filename):
                overwrite_choice = input(
                    f"Target file '{target_output_filename}' already exists. Overwrite? (y/n/s to skip this file) [n]: ").lower()
                if overwrite_choice == 's':
                    logging.info(f"Skipping already processed file: {source_file}")
                    continue
                elif overwrite_choice == 'y':
                    logging.info(f"Overwriting existing target file: {target_output_filename}")
                    # Delete or truncate the file before opening in append mode if we want a fresh start
                    # For simplicity, if 'a' is used in create_target_document_stream, new content will be added.
                    # If 'w' was used, it would be overwritten anyway.
                    # To truly overwrite with 'a' mode, we'd os.remove() it first.
                    # Let's ensure a clean slate if overwriting
                    try:
                        os.remove(target_output_filename)
                        logging.info(f"Removed existing file: {target_output_filename} for overwrite.")
                    except OSError as e:
                        logging.error(
                            f"Could not remove existing file {target_output_filename}: {e}. Appending might occur.")
                # else (n or default): proceed, will append to existing if 'a' mode is kept

            last_request_time = 0  # Reset for each file or keep global? Per file seems fine.

            with create_target_document_stream(source_file, LANGUAGE) as target_stream:
                page_iterator = None
                file_type_processed = ""

                if source_file.lower().endswith('.pdf'):
                    page_iterator = read_pdf_pages(source_file, start_processing_item, end_processing_item)
                    file_type_processed = "PDF"
                elif source_file.lower().endswith('.epub'):
                    page_iterator = read_epub_pages(source_file, start_processing_item, end_processing_item)
                    file_type_processed = "EPUB"

                if not page_iterator:
                    logging.warning(f"Could not create a page/item iterator for {source_file}. Skipping.")
                    continue

                logging.info(f"Starting translation for {file_type_processed} file: {source_file}")
                processed_item_count = 0
                for item_number, item_text in page_iterator:
                    if not item_text.strip():  # Double check if iterator yielded empty text
                        logging.warning(
                            f"Item {item_number} from {source_file} has empty text after iterator. Skipping.")
                        continue

                    throttle_request(last_request_time)
                    last_request_time = time.time()

                    translated_text, original_chars, translated_chars = get_translation_with_genai(model, item_text)

                    if "Error in translation." in translated_text and translated_chars == 0:
                        logging.error(f"Failed to translate item {item_number} from {source_file}.")
                    else:
                        logging.info(
                            "Item %d (%s): Original characters: %d, Translated characters: %d",
                            item_number, file_type_processed, original_chars, translated_chars
                        )
                        write_page_to_document(target_stream, item_number, translated_text)
                        processed_item_count += 1

                if processed_item_count == 0:
                    logging.warning(
                        f"No items were processed for {source_file} within the specified range or due to empty content.")

            logging.info(
                f"Translation processing completed for {source_file}. Results saved in: {target_output_filename}")

        logging.info("All files processed.")