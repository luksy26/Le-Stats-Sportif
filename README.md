Nume: Lăzăroiu Lucas
Grupă: 341C5

# Tema 1

Organizare
-
Scopul general al temei este implementarea unor endpoint-uri pentru a raspunde la cereri API catre
un server Flask. Aceste cereri sunt gestionate in mod paralel de catre un threadpool. Datele pe baza
carora se vor face cererile se extrag dintr-un fisier csv.

* Endpoint-urile au fost implementate in routes.py. Aproape toate se folosesc de un helper 'calculate' function, 
cu exceptia  endpointurile care nu sunt intens computationale, ci mai degraba se ocupa cu furnizarea de metadate 
despre job-urile curente/deja terminate, dar si cu gestionarea threadpool-ului (e.g. graceful_shutdown).
* Threadpool-ul are o metoda de shutdown, moment in care nu mai sunt acceptate noi request-uri catre server.
* Rezultatele job-urilor sunt stocate pe disc, in folderul results (creat/golit automat la pornirea serverului).
* Consider ca tema este foarte utila, deoarece incurajeaza o aprofundare a unor notiuni foarte relevante in SWE si se 
ramifica  si in alte contexte relevante: testare, infrastructura, scripting, baze de date (kind of, lucrul cu fisiere),
logging cu Rotating File Handler.
* Cred ca implementarea mea este destul de buna, atat din punct de vedere al eficientei, cat si al organizarii codului:
lizibilitate, modularitate, organizare logica si un flow usor de inteles, comentarii si docstring-uri pertinente.
As fi putut sa fac codul putin mai error-safe dar am considerat ca era mult prea mult volum de scris si nu acesta era
scopul principal al temei.

***In plus:***


* Am creat un queue listener pentru logger pentru cazurile in care thread-urile vor sa scrie in acelasi timp in fisier.
Nu am observat astfel de probleme dar am decis sa o fac ca un safety net.
* Tema rula in ~2s fara logger, acum dureaza ~20s


Implementare
-
* Tema a fost implementata in intregime: teste functionale, unittesting, logger + versionare pe git
* Au fost implementate si testate si endpointurile care nu sunt verificate de checker, dar exista in enunt.
Testele nu au fost foarte riguroase si au presupus modificarea checkerului + niste print-uri. Acest lucru
a fost facut doar in timpul realizarii temei, acum exista doar implementarea.
* In __init__.py se creeaza webserverul, threadpool-ul, se extrag datele, se creeaza folderul results si loggerul
* Functiile "ajutatoare", care fac calculul propriu zis pentru a raspunde la cereri sunt complet independente. Toate
argumentele sunt injectate: dictionarul cu date, intrebari, state, loggerul
*

**Dificultăți întâmpinate**

* Cand a fost facuta serializarea JSON a rezultatelor se putea intampla ca 1-2 teste sa pice din cauza unor erori de
json.load. Cand am inspectat cauzele (e.g error: expected ':' delimiter), am observat ca sunt false si fisierul JSON
era ok. Dupa ceva debugging in zadar am decis sa folosesk pickle (.pkl) pentru serializare si problema nu a mai aparut.
* Importarea e diferita atunci cand se ruleaza din venv. Problema a fost realizata repede dar totusi a fost putin
incomfortabil sa lucrez cu "found erorrs" in pycharm, mai ales daca voiam sa execut un cod mic implementat din GUI.
Din acelasi motiv, nu se facea autocomplete cand chemam metode din alte module.
* La un moment dat nu mai pornea serverul de flask (make run_server), tot o eroare de importuri. A trebuit sa clonez
din nou repo-ul (nu am schimbat absolut nimic in cod), iar apoi a functionat. S-ar putea sa fi crapat ceva cand rulam
unittestele dar in momentul de fata nu imi dau seama.
* Nu e prea dragut sa scrii unitteste atunci cand datele de intrare si referinta sunt dictionare mari. 

Resurse utilizate
-
* Laboratorul in care s-a introdus primitiva Event.
* Forumul temei pentru neclaritati/sugestii ce nu se gaseau in enunt.
* Alte surse pentru lucruri simplistice despre sintaxa python, diverse module si structuri de date. Consider ca pot fi
omise.

Git
-
1. https://github.com/luksy26/Le-Stats-Sportif - momentan este privat.
2. folderul .git se afla in arhiva si se pot gasi commit-urile.

Structura Arhivei
-

- root
  - app
    - \_\_init\_\_.py
    - data_ingestor.py
    - routes.py
    - task_runner.py
  - unittests
    - README_testing.md
    - small_dict.json
    - TestWebserver.py
  - \_\_init\_\_.py
  - README
  - git

    
