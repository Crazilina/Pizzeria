from flask import Flask, render_template, redirect, url_for, jsonify, request
from connessione import connect

app = Flask(__name__)

# Classe Pizza
class Pizza:
    def __init__(self, nome, prezzo, ingredienti, foto):
        self.nome = nome
        self.prezzo = prezzo
        self.ingredienti = ingredienti
        self.foto = foto

    def getPizza(self):
        """Restituisce la descrizione della pizza con gli ingredienti."""
        ingredienti_str = "\n".join(f"{n}. {i}" for n, i in enumerate(self.ingredienti, start=1))
        return f"La Pizza {self.nome} costa €{self.prezzo}\nIngredienti:\n{ingredienti_str}"

# Funzione per ottenere la lista delle pizze dal database
def get_pizze():
    conn = connect()  # Connessione al database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pizze")  # Query per ottenere tutte le pizze
    pizze_db = cursor.fetchall()

    pizze = []
    for pizza in pizze_db:
        # Ottenere gli ingredienti per ogni pizza
        cursor.execute("""
            SELECT Ingrediente.nome 
            FROM Ingrediente 
            JOIN IngredientePizza ON Ingrediente.id = IngredientePizza.ID_Ingrediente
            WHERE IngredientePizza.ID_Pizza = %s
        """, (pizza[0],))
        ingredienti = [row[0] for row in cursor.fetchall()]
        
        # Aggiungere l'oggetto Pizza alla lista
        pizze.append(Pizza(pizza[1], float(pizza[2]), ingredienti, pizza[3]))

    conn.close()  # Chiudere la connessione
    return pizze

# Carrello
carrello = []

@app.errorhandler(404)
def not_found(e):
    """Gestione dell'errore 404."""
    return render_template("404.html"), 404

@app.route("/")
def index():
    """Pagina principale."""
    return render_template("index.html")

@app.route("/prodotti")
def lista_prodotti():
    """Elenco di tutti i prodotti."""
    pizze = get_pizze()  # Ottiene la lista delle pizze
    return render_template("prodotti.html", prodotti=pizze)

@app.route("/prodotti/<nome>")
def dettaglio_prodotto(nome):
    """Dettagli del prodotto."""
    pizze = get_pizze()  # Ottiene la lista delle pizze
    prodotto = next((p for p in pizze if p.nome == nome), None)  # Cerca il prodotto per nome
    if prodotto:
        return render_template("prodotto.html", prodotto=prodotto)
    return render_template("404.html"), 404

@app.route("/aggiungi/<nome>/ajax", methods=["POST"])
def aggiungi_ajax(nome):
    """Aggiungi un prodotto al carrello tramite AJAX."""
    pizze = get_pizze()  # Ottiene la lista delle pizze
    prodotto = next((p for p in pizze if p.nome == nome), None)  # Cerca il prodotto per nome
    if prodotto:
        carrello.append(prodotto)  # Aggiunge il prodotto al carrello
        return jsonify({"success": True, "cart_count": len(carrello)})
    return jsonify({"success": False, "message": "Prodotto non trovato"}), 404

@app.route("/carrello")
def mostra_carrello():
    """Mostra il contenuto del carrello."""
    totale = sum(p.prezzo for p in carrello)  # Calcola il totale
    return render_template("carrello.html", carrello=carrello, totale=totale)

@app.route("/rimuovi/<nome>")
def rimuovi_dal_carrello(nome):
    """Rimuovi un prodotto dal carrello."""
    for prodotto in carrello:
        if prodotto.nome == nome:  # Cerca il prodotto nel carrello
            carrello.remove(prodotto)  # Rimuove il prodotto
            break
    return redirect(url_for("mostra_carrello"))

@app.route("/svuota_carrello")
def svuota_carrello():
    """Svuota completamente il carrello."""
    carrello.clear()  # Svuota il carrello
    return redirect(url_for("mostra_carrello"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Effettua il checkout."""
    totale = sum(p.prezzo for p in carrello)  # Calcola il totale
    if request.method == "POST" and totale > 0:  # Controlla se ci sono prodotti nel carrello
        carrello.clear()  # Svuota il carrello dopo il pagamento
        return redirect(url_for("successo"))
    return render_template("checkout.html", totale=totale)

@app.route("/successo")
def successo():
    """Pagina di conferma del pagamento."""
    return render_template("successo.html")


@app.route("/inserisci", methods=["GET", "POST"])
def inserisci():
    """Pagina per aggiungere una nuova pizza."""
    if request.method == "POST":
        try:
            # Ricezione dati dal form
            nome = request.form['nome']
            prezzo = request.form['prezzo']
            foto = request.form['foto']
            ingredienti_str = request.form['ingredienti']  # Stringa di ingredienti separati da virgola
            ingredienti = [i.strip() for i in ingredienti_str.split(",")]  # Converti in lista e rimuovi spazi extra
            print(ingredienti)

            # Connessione al database
            conn = connect()
            cursor = conn.cursor()

            # Inserire la pizza nella tabella Pizze
            cursor.execute("INSERT INTO Pizze (nome, prezzo, foto) VALUES (%s, %s, %s) RETURNING id",
                           (nome, prezzo, foto))
            id_pizza = cursor.fetchone()[0]  # Ottieni l'ID della nuova pizza

            # Inserire gli ingredienti nella tabella Ingrediente e IngredientePizza
            for ingrediente in ingredienti:
                # Controlla se l'ingrediente esiste già
                cursor.execute("SELECT id FROM Ingrediente WHERE nome = %s", (ingrediente,))
                result = cursor.fetchone()
                if result:
                    id_ingrediente = result[0]  # L'ingrediente esiste già, usa l'ID esistente
                else:
                    # Se non esiste, aggiungilo e ottieni il nuovo ID
                    cursor.execute("INSERT INTO Ingrediente (nome) VALUES (%s) RETURNING id", (ingrediente,))
                    id_ingrediente = cursor.fetchone()[0]

                # Aggiungi la relazione tra pizza e ingrediente
                cursor.execute("INSERT INTO IngredientePizza (ID_Pizza, ID_Ingrediente) VALUES (%s, %s)",
                               (id_pizza, id_ingrediente))

            # Conferma modifiche
            conn.commit()

            # Chiudi connessione
            conn.close()

            # Reindirizza alla lista dei prodotti
            return redirect(url_for("lista_prodotti"))

        except Exception as e:
            # Gestione errori
            conn.rollback()  # Annulla le modifiche in caso di errore
            conn.close()
            return f"Errore durante l'inserimento della pizza: {e}", 500

    # Mostra la pagina con il form per inserire una nuova pizza
    return render_template("inserisci.html")




if __name__ == "__main__":
    app.run(debug=True)
