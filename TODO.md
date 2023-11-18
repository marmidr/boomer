# Lista zadań

[x] PnP: obsługa xls/x
[x] czyścić podgląd jeszcze przed próbą wczytania pliku, na wypadek gdyby np. pliku nie znaleziono
[x] czyścić wszystkie podglądy przed otwarciem projektu, gdyby go nie było
[x] sortowanie elementów: C2, C3, C10, a nie C10, C2, C3
[x] przycisk Save Profile powinien zawierać jego nazwę
[x] obsługa .ods
[x] wybór kolumn - pola powinny mieć wpisane bieżące wybory
[x] wybór projektu powoduje automatyczne wczytanie BOM i PnP x2
[x] loging.debug -> info tam gdzie to odpowiednie
[x] wydzielić cross-checker, raport generator ma korzystać z klasy CrossCheckResult
[x] na podstawie CrossCheckResult pokolorować różnice w komentarzah elementów
[ ] xls/x/ods - komunikat jeśli plik zawiera kilka arkuszy, zapisywanie w projekcie nazwy/numeru arkusza
[ ] przy otwieraniu nowego projektu, pytać o profil lub pozwolić wybrać istniejący
[x] widget HTML: https://pypi.org/project/tkhtmlview/
[x] po dodaniu projektu (Browse) podglądy powinny być czyste
[x] przy zapisywaniu profilu, sprawdzać czy jest uzywany TYLKO w tym jednym projekcie, pytać czy nadpisać
[x] automatycznie zapisywać raport do pliku html
[x] przy wczytywaniu listy projektów, usuwać nieistniejące
[x] w raporcie poprawić liczenie czerokości kolumny Designator dla sekcji Comments mismatch
[x] kopiowanie do schowka jako html: działa tylko z Word/Write
    Niepoprawnie liczone pozycje bloku HTML
[x] unit testy kodu czytającego csv/xls/odt
[ ] unit testy komparatora
[x] klikniecie Porównaj przeładowuje pliki BOM i PnP
[x] porównywanie komentarzy biblioteką difflib: dodane/usunięte/zmienione/takie same
[x] wybór kolumn bez nagłówka - po indeksie
[x] sprawdzanie kolidujących współrzędnych
[x] xls/xlsx - komórki zawierające liczbę np 100, są czytane jako '100.0' -> usunąć część dziesiętną
[x] xls/xlsx - komórki zawierające kilka wierszy -> scalać do jednej linii
[x] sprawdzanie dystansów: powtórzenia  (C1 vs C2, C2 vs C1)
[ ] sprawdzanie dystansów: TOP vs TOP, BOTTOM vs BOTTOM
