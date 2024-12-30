https://chatgpt.com/c/676fb251-b950-8005-8776-c69cf9deed4d

1.
Erstelle mir ein Python ein Programm das ein großes PDF-Dokument seitenweise einliest und den Inhalt der Seite an eine api schickt

zb : 

api_key = 'YOUR_API_KEY'
city = 'Berlin'
url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'

response = requests.get(url)
data = response.json()

print(data['main']['temp'])


Es soll ein neues PDF-Dokument erstellt werden in das seitenweise die Antworten hinzugefügt werden



2.
Die Übersetzung der Sprache kann ich einstellen z.B de für Deutsch

3.
Um das PDF einzulesen wird im aktuellen Verzeichnis geschaut nach Dateien mit ."PDF"

4.
Dass das Dokument was erstellt wird hat den gleichen Namen wie das Dokument was eingelesen wird nur das zusätzlich vor dem. PDF das Sprachkürzel eingefügt wird


5.  

Der api key soll aus der Umgebungsvariable gelesen werden



