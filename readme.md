# Monte Planer
Jest w Krakowie takie liceum. O tym, czym różni się od innych szkół możnaby pisać książki, ale skupmy się na planie dnia. Nie ma tam znanego w pruskiej szkole rytmu naprzemiennych 45 lekcji i krótkich przerw. Większość zajęć trwa 30 minut, niektóre ponad godzinę, a w środku dnia w ogóle ich nie ma - uczniowie sami się uczą w ramach Pracy Własnej. Nie ma też klas profilowanych, każdy licealista wybiera właśnie takie rozszerzenia, jakie go pociągają. Miło jest być uczniem takiej szkoły, ale nauczycielem tworzący plan zajęć - już niekoniecznie.

W ramach pracy inżynierskiej tworzę program ułatwiający tą trudną, szlachetną pracę. Bierze pod uwagę:
- Sale oraz ich pojemność.
- Nauczycieli oraz ich dostępność każdego dnia.
- Klasy i podklasy, czyli każdego ucznia i to, na jakie lekcje chodzi.
- Przedmioty, czyli ile lekcji w tygodniu ma się odbyć i jakiej długości, czy muszą odbywać się w konkretnej sali, jakie nauczyciel je prowadzi. Mogą być podstawowe (dla jednej podklasy) albo roszerzone (dla wszystkich podklas w danej klasie)

Program pozwala na łatwe rysowanie i edytowanie planu, jednocześnie na bieżąco skanuje plan i sprawdza, czy nie ma w nim konfliktów (np. czy ktoś nie musi znajdować się w dwóch miejscach jednocześnie). Na koniec generuje spersonalizowany pdf dla każdej podklasy, ucznia, nauczyciela oraz sali.

W folderze release znajduje się pakiet .deb (może nie być w najnowszej wersji).

## Instrukcja obsługi
Zakładki z lewej strony korzystają z danych zakładek na prawo od nich, dlatego najlepiej zacząć wypełniać dane zaczynając od prawej.

### Pasek menu
Można tutaj znaleźć dwie funkcje - jedna pozwala na zrobienie kopii zapasowej, druga na wczytanie danych. Każde działanie jest zapisywane na bieżąco, więc nie ma potrzeby zapisywania

### Pomieszczenia
![Zakładka pomieszczenia](/readme_img/pomieszczenia.png)

Po wpisaniu nazwy pomieszczenia i wciśnięciu Enter zostaje dodane do listy. Można zmieniać pojemność sali (nie licząc nauczyciela) i usuwać sale.

### Nauczyciele
![Zakładka nauczyciele](/readme_img/nauczyciele.png)

Czerwony kolor oznacza, że nauczyciel jest dostępny w danej godzinie, biały, że nie. Aby zaznaczyć dostępność nauczyciela należy klinąć w wybranym miejscu i przesunąć mysz. Na różowo zastanie podświetlony prostokąt, a po ponownym kliknięciu zostanie on zatwierdzony. Żeby usunąć dostępność należy zacząć prostokąt w polu zaznaczonym na czerwono. Podwójne kliknięcie spowoduje zmianę koloru pojedynczego pola.

### Klasy
![Zakładka klasy](/readme_img/klasy.png)

Klasy mogą mieć dowolne nazwy, podklasy sa nazywane automatycznie alfabetycznie. Guzik 'Zmień kolejność' pozwala zmienić kolejność w jakiej klasy są wyświetlane na planie przez przeciąganie nazw na liście. Poniżej widać listę uczniów razem z ich przedmiotami. Kliknięcie prawym przyciskiem myszy na guzik z nazwą usuwa ucznia z listy tego przedmiotu. Guzik 'Usuń ucznia' i 'Dodaj przedmiot' działają na zaznaczonych uczniów. Gdy podklasa jest usunięta, pozostałe są automatycznie przemianowywane.

### Przedmioty
![Zakładka przedmioty](/readme_img/przedmioty.png)

To, że przedmiot jest rozszerzony oznacza, że mogą w nim brać udział uczniowie ze wszystkich podklas. Oznacza się to przez stworzenie go w odpowiednim miejscu. Nie ma potrzeby zaznaczać w nazwie - program zrobi to sam. Kolor i skrót są wyświetlane na planie.
Jeśli przedmiot odbywać się w konkretnej sali (np. informatyka) można to zaznaczyć. W przeciwnym razie trzeba zostawić to pole puste. 
Dodając lekcję można wybrać jej czas trwania z listy lub wpisać własny, byle była to liczba naturalna. Aby usunąć lekcję, trzeba na nią kliknąć. Jeśli w nawiasie nie ma podanej godziny, oznacza to, że lekcja nie została jeszcze umieszczona w planie.
Poniżej znajduje się lista uczniów połączona z tą z zakładki *Klasy*.
Gdy dodaje się przedmiot program sprawdza, czy isnieje już przedmiot o tej samej nazwie. Jeśli tak, kopiuje kolor, skrót i nauczyciela.

### Plan
![Zakładka plan](/readme_img/plan.png)

Na samej górze znajdują się filtry. Można wyświetlić plan dla wybranych klas, uczniów, nauczycieli i sal. Edytować plan można jednak tylko w widoku klas.
Poniżej znajdują guziki wyboru trybów. Aby wrócić do normalnego wystarczy ponownie kliknąć na guzik obecnie wybranego trybu. Dalej znajduje się suwak przybliżenia i przezroczytości (przydatny gdy bloki nachodzą na siebie).

#### Bloki zajęciowe
Aby go dodać należy wejść w tryb *Nowy blok zajęciowy*. Wcisnąć lewy przycisk myszy w odpowiednim miejscu (nad kurosorem wyświetla się godzina) i przeciągnąć, ciągle trzymająć wciśnięty przycisk. Mogą być przypisane do całej klasy lub jednej podklasy. Co do zasady, lepiej tworzyć bloki dla całej klasy, bo można do nich przypisać wszystkie przedmoty, a nie tylko podstawowe. Jeśli klasa ma tylko jedną podklasę, bloki są przypisywane do klasy, ułatwia to życie na wypadek, jakby dodało sie później kolejną podklasę. Można przesuwać bloki korzystając z trybu *Przesuwanie*. Może zdarzyć się, że bloki będą leżały jeden na drugim. Aby zmienić kolejność w jakiej są ułożone na sobie należy przejść do trybu normalnego i dwa razy kliknąć na blok, a zostanie on przeniesiony na spód. W wyeksportowanym planie nachodzące na siebie bloki zostaną zawężone i ustawione obok siebie. Po kliknięciu na blok prawy przyciskiem myszy pojawi się menu kontekstowe. 
Blok przybiera kolor jeśli wszystkie lekcje mają ten sam, w przeciwnym razie jest szary. Tekst jest generowany automatycznie - ma odpowiedni rozmiar, jest skracany jeśli trzeba i ma nadany odpowiednio kontrastujący kolor.

![Menu kontekstowe bloku lekcyjnego](/readme_img/lekcja%20menu.png)

Program nie pozwoli na dodanie lekcji, która spowodowałaby konflinkt (będą one wyszarzone). Po najechaniu kursorem na wyszarzony obiekt pojawi się podpowiedź, dlaczego spowodowałoby to konflikt. Jeśli konflikt powstanie i tak (np. przez zmianę rozszerzeń ucznia lub dostępności nauczyciela) bloki będą miały czerwoną obwódkę, a po najechaniu na nie kursorem pojawi się podpowiedź z konfliktami.
Ostatnia pozycja usuwa blok.

#### Własne bloki
Pozwalają one na dowolne rysowanie po planie. Mogą wykraczać pomiędzy klasy, o ile są obok siebie na planie (np. klasy 1b, 2 i 3a). Jeśli zmiana kolejności klas rozdzieliłaby blok na dwie części, zostaje on automatycznie usnięty. Po dodaniu bloku korzystając z trybu *Nowy blok* program zapyta o kolor i tekst. Aby wejść do nowej linii, trzeba wpisać "\<br>". Kolor i tekst można później zmienić korzystając z menu kontekstowego. Też można go przesuwać.

#### Eksport danych
Po kliknięciu na ten przycisk program wygeneruje osobisty plan dla każdej klasy, ucznia, nauczyciela i sali w formacie png oraz pdf, w rozmiarze poziomej kartki A4.