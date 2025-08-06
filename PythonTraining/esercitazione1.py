#this is a simple number guessing game in Python
#it allows the user to choose a difficulty level and provides feedback on their guesses
#the game keeps track of the best score and allows for multiple rounds
#however the game is in italian
#it was just a simple exercise to practice Python basics
import random
haStartato = False
difficoltaScelta = False
maxNumeroDaIndovinare = 100
maxTentativi = 10
def leggi_miglior_punteggio(path="scoreboard.txt"):
    try:
        with open(path) as f:
            scores = [int(line) for line in f if line.strip().isdigit()]
        return max(scores) if scores else 0
    except FileNotFoundError:
        return 0
    
while True:
    best = leggi_miglior_punteggio()
    if not haStartato:
        print("Ciao! prova ad indovinare il numero, puoi scegliere tra 3 difficlotà:\n1) Facile (1-50)\n2) Medio (1-100)\n3) Difficile (1-500)")
        print(f"Hai {maxTentativi} tentativi per indovinare il numero.")
        print(f"Il miglior punteggio di sempre è: {best}\n")
        print("Scegli la difficoltà (1, 2 o 3):")
    if haStartato:
        print("\nScegli la difficoltà (1, 2 o 3):")
        print(f"Il miglior punteggio di sempre è: {best}\n")
    Difficolta = input().strip()
    if Difficolta == "1":
        maxNumeroDaIndovinare = 50
        difficoltaScelta = True
    elif Difficolta == "2":
        maxNumeroDaIndovinare = 100
        difficoltaScelta = True
    elif Difficolta == "3":
        maxNumeroDaIndovinare = 500
        difficoltaScelta = True
    else:
        print("Difficoltà non valida, scrivi un numero tra 1 e 3 per scegliere la difficoltà.")
    maxTentativi = 10
    numeroDaIndovinare = random.randint(1, maxNumeroDaIndovinare)
    if difficoltaScelta:
        while True:
            try:
                numeroUtente = int(input("\nInserisci il numero: "))
            except ValueError:
                print("Per favore, inserisci un numero valido.")
                continue
            haStartato = True
            if maxTentativi <= 0:
                print("Hai esaurito i tentativi! Il numero era:", numeroDaIndovinare)
                break
            if numeroUtente < 0 or numeroUtente > maxNumeroDaIndovinare:
                print("\n \nIl numero deve essere compreso tra 1 e 100, riprova!")
            elif numeroUtente < numeroDaIndovinare:
                print("Il numero da indovinare è maggiore, riprova!")
                maxTentativi -= 1
            elif numeroUtente > numeroDaIndovinare:
                print ("Il numero da indovinare è minore, riprova!")
                maxTentativi -= 1
            else:
                print("Complimenti! Hai indovinato il numero!")
                break
    print("Grazie per aver giocato!")
    punteggio = maxTentativi * numeroDaIndovinare
    print("\nComplimenti, ti sono rimasti:", maxTentativi, "tentativi,\n\nquindi il tuo punteggio è:", punteggio)
    print("\nSe vuoi fare un altra partita basta dire ''gioca'': ")
    if input().lower() != "gioca":
        break
