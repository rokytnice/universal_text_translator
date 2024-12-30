import google.generativeai as genai
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Frame, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import os

# API-Details
API_KEY = os.getenv('API_KEY')  # API-Schlüssel aus Umgebungsvariable lesen
LANGUAGE = 'de'  # Sprachkürzel für die Übersetzung

def configure_genai():
    """
    Konfiguriert das Generative AI-Modell.
    """
    if not API_KEY:
        print("[ERROR] API key not found in environment variables.")
        return None
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")

def get_translation_with_genai(model, content):
    """
    Verwendet das Generative AI-Modell, um Übersetzungen durchzuführen.
    Gibt die Übersetzung und die Anzahl der Zeichen in der Antwort zurück.
    """
    print("[INFO] Generating translation with Google Gemini API.")
    try:
        response = model.generate_content(f"Translate the following text to {LANGUAGE}: {content}")
        response_text = response.text
        print(f"[INFO] Translation response received: {response_text}")
        return response_text, len(content), len(response_text)
    except Exception as e:
        print(f"[ERROR] Error during translation: {e}")
        return "Error in translation.", len(content), 0

def create_pdf_with_response(page_content, response):
    """
    Erstellt eine neue PDF-Seite mit dem Originalseiteninhalt und der Übersetzung.
    Bewahrt die ursprüngliche Textformatierung basierend auf einem A4-Dokument.
    """
    print("[INFO] Creating PDF page with AI translation response.")
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    # Originalseiteninhalt schreiben
    frame = Frame(50, height - 300, width - 100, 100, showBoundary=0)
    original_paragraph = Paragraph("<b>Original Page Content:</b><br />" + page_content.replace("\n", "<br />"), normal_style)
    frame.addFromList([original_paragraph], c)

    # Übersetzung schreiben
    frame = Frame(50, height - 500, width - 100, 200, showBoundary=0)
    translated_paragraph = Paragraph("<b>Translated Content:</b><br />" + response.replace("\n", "<br />"), normal_style)
    frame.addFromList([translated_paragraph], c)

    c.save()
    buffer.seek(0)
    print("[INFO] PDF page created successfully.")
    return buffer

def process_pdf(input_path, output_path, model, start_page, end_page):
    """
    Liest das PDF seitenweise, übersetzt den Inhalt mit der API und erstellt ein neues PDF mit den Übersetzungen.
    Gibt Zeichenstatistiken im Log aus.
    """
    print(f"[INFO] Starting to process PDF: {input_path}")
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page_number, page in enumerate(reader.pages):
        if page_number < start_page - 1:
            continue
        if end_page is not None and page_number >= end_page:
            print(f"[INFO] Reached the end of the specified range ({end_page}). Stopping.")
            break

        print(f"[INFO] Processing page {page_number + 1}.")
        page_content = page.extract_text()

        # Übersetzungsanforderung
        print(f"[INFO] Sending page {page_number + 1} content to AI model.")
        ai_response, chars_sent, chars_received = get_translation_with_genai(model, page_content)

        print(f"[INFO] Page {page_number + 1}: Characters sent = {chars_sent}, Characters received = {chars_received}")

        # Neue Seite mit Übersetzung erstellen
        response_pdf = create_pdf_with_response(page_content, ai_response)

        # Neue Seite zur Ausgabe hinzufügen
        response_reader = PdfReader(response_pdf)
        writer.add_page(response_reader.pages[0])

    # Ausgabe speichern
    print(f"[INFO] Saving processed PDF to: {output_path}")
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

    print(f"[INFO] Output PDF saved to {output_path}")

def find_pdfs_in_directory():
    """
    Sucht im aktuellen Verzeichnis nach PDF-Dateien.
    """
    print("[INFO] Searching for PDF files in the current directory.")
    pdf_files = [file for file in os.listdir('.') if file.lower().endswith('.pdf')]
    print(f"[INFO] Found {len(pdf_files)} PDF file(s).")
    return pdf_files

if __name__ == "__main__":
    print("[INFO] Program started.")
    model = configure_genai()
    if not model:
        print("[ERROR] Could not configure AI model. Exiting.")
    else:
        pdf_files = find_pdfs_in_directory()
        if not pdf_files:
            print("[WARNING] No PDF files found in the current directory.")
        else:
            range_input = input("Enter the range of pages to process (e.g., '2-5' or leave blank for all): ").strip()
            if range_input:
                try:
                    start_page, end_page = (int(x) if x else None for x in range_input.split('-'))
                except ValueError:
                    print("[ERROR] Invalid range format. Please use 'start-end' or leave blank.")
                    start_page, end_page = 1, None
            else:
                start_page, end_page = 1, None

            for pdf_file in pdf_files:
                input_pdf_path = pdf_file
                output_pdf_path = pdf_file.replace('.pdf', f'_{LANGUAGE}.pdf')
                print(f"[INFO] Processing file: {input_pdf_path}")
                process_pdf(input_pdf_path, output_pdf_path, model, start_page, end_page)
    print("[INFO] Program finished.")
