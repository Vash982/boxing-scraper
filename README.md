ITALIAN:
-COME FUNZIONA:
	questo web scraper prende dei filtri di ricerca in input,
  per compilare il form dinamico l'applicazione invia dei payload alle risorse php del sito che le prende come json,
  le risorse php restituiscono una lista di opzioni che l'utente deve scegliere, la lista cambia in base alle opzioni scelte in precedenza,
  una volta compilato il form preleva i dati dei pugili dal codice sorgente della pagina e li stampa in un file excel.
	
-COME USARE:
 	se si usa NixOS come sistema operativo principale è sufficiente usare il comando nix-shell per scaricare le dipendenze necessarie,
	altrimenti è necessaio installare le librerie elencate nel file shell.nix usando pip.
 	una volta installate le dipendenze non resta da fare altro che eseguire il main.py.
	NOTA: il programma è abbastanza lento all'avvio e nella scrittura del file excel
 	NOTA: esisono delle combinazioni di filtri che non portano nessun risultano, errore del sito web originale.

ENGLISH:
-HOW IT WORKS:
	this web scraper takes some filters in input,
  to fill the dynamic form the application sends payloads to the php resources of the site that takes them as json,
  the php resources return a list of options that the user has to choose, the list  changes based on the options chosen earlier,
  Once the form is filled in, he application takes the fighters’ data from the source code of the page and prints them in an excel file
-HOW TO USE:
 	if you use NixOS as your main operating system, you can simply use the nix-shell command to download the necessary dependencies,
	Otherwise you need to install the libraries listed in the shell.nix file using pip.
  Once the dependencies are installed, there is nothing left to do but run the main.py.
	NOTE: the program is quite slow to start and write excel file
 	NOTE: there are some combinations of filters that do not bring any result, error of the original website.
