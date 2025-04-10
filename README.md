# master_ai_engineer
# Questa rubrica offre 6 opzioni 
  - Salvataggio contatti (crea un file in formato .json)
  - Creazione contatti (i campi nome , cognome , email obligatori mentre il campo telefono è opzionale)
  - Modifica contatti (chiede di inserire l'email che dovrebbe essere unica, dopo si dovrebbe inserire il nome del campo che si vuole modificare e il nuovo valore)
  - Eliminazione contatti (chiede di inserire l'email che dovrebbe essere unica dopo che fa una validazione dell'email chiede una conferma se si vuole eliminare il contatto oppure no)
  - Cerca contatto (basta inserire il nome o cognome del contatto che si vuole cercare)
  - Mostra contatti (mostra i contatti presenti nella rubbrica)


# Note
-  Il caricamento del file viene fatto appena di lancia l'applicazione ho deciso di inserirlo dentro della folder sample_data
   di conseguenza il salvataggio avviene sempre dentro la folder sample_data
   il file che ho creato per i miei test l'ho chiamato load_contacts.json

   Esempio del contenuto:
   
   [
    {
    "_id": 1,
    "_name": "angel",
    "_surname": "lau",
    "_email": "angel@gmail.com",
    "_phone": "333"
    }
  ]

   

    
 
