file: translator.py

https://chatgpt.com/c/677257fc-9b94-8005-8b65-22ba07c56b9f
 

Erstelle mir ein Python ein Programm das ein großes pdf-Dokument seitenweise einliest und den Inhalt der Seite an eine ai api zum überstzen schickt schickt
mit google.generativeai 

verwende english für den code

Das wird geschaut ob ein .pdf Dokument sich im aktuellen Verzeichnis befindet und dieses wird dann verarbeitet
Um das text einzulesen wird im aktuellen Verzeichnis geschaut nach Dateien mit ".pdf"

Es soll ein neues text - Dokument, das Zieldokument erstellt, in das seitenweise die Antworten hinzugefügt werden

Das Programm erledigt Folgendes:

Es liest das pdf seitenweise ein.
Sendet den inhalt jeder Seite an eine API.
Erstellt ein neues text dokument, das den übesetzten ihnalt für jede Seite enthält.
es fügt die überstzte seite - siete für seite in das zieldokument ein

Die Übersetzung der Sprache kann ich einstellen z.B de für Deutsch
Der Default für die Zielsprache ist immer deutsch

Dass das Dokument was erstellt wird hat den gleichen Namen wie das Dokument was eingelesen wird nur das zusätzlich vor dem .txt das Sprachkürzel eingefügt wird

Spracheinstellung: Die Sprache kann über das Sprachkürzel (z. B. de für Deutsch) angepasst werden.
text-Auswahl: Das Programm durchsucht das aktuelle Verzeichnis nach Dateien mit der Endung .txt
Dateiname des Ergebnisses: Der Name des erzeugten Dokuments enthält das Sprachkürzel vor der Endung .txt


 
Der api key soll aus der Umgebungsvariable gelesen werden
Der API-Schlüssel wird jetzt aus der Umgebungsvariable API_KEY gelesen. Falls der Schlüssel fehlt, wird ein entsprechender Fehler in der API-Antwort zurückgegeben. Lass mich wissen, falls weitere Anpassungen benötigt werden!


Erstelle für jeden Schritt ein log statement



Bei der Antwort soll ein entsprechende Ausgabe erfolgen die das Warten auf die Antwort visualisiert in dem punkte  Auf der Konsole als log-statement ausgegeben werden



Der Request und Response soll als log ausgegeben  werden



Ich möchte über einen zusätzlichen Parameter festlegen wie viel Seiten übersetzt werden sollen beginnend ab der ersten



Wenn keine Zahl übergeben wird dann soll das ganze Dokument also alle Seiten verwendet werden übersetzt werden
 

Ich möchte auch einen Range angeben können also von Seite bis Seite das bedeute ich übergebe dann zwei Zahlen dessen Range übersetzt werden soll
Wenn du eine Zahl für die range der Seiten angegeben wird, dann wird nur eine Seite übersetzt

Gib mir für jede übersetzte Seite an wie viel Zeichen gesendet worden sind und wie viel Zeichen empfangen worden sind das ganze soll dann im Log ausgegeben werden


Die Formatierung soll auch übernommen werden das heißt finde heraus nach wie viel Wörtern ein Zeilenumbruch gemacht wird und übernehme das für das generierte Dokument


Verwende für das text was generiert wird ein Template dass die typische Breite eines A4 Dokuments hat, um automatisch Zeilenumbrüche zu erhalten 


setze die seitenzahl im zieldokument passend zu der übersetzen seite

Arbeite mit streams beim einlesen und schreiben von Dateien und beim Lesen aus APIs