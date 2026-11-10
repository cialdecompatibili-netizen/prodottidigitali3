# GUIDA listino prodotti digitali (prodottidigitali3)

Obiettivo: riempire lo shop con i best seller Etsy, dal piu' venduto in giu', a lotti (prova 1 = primi 10). Tutto a step, ogni step e' uno script.

## File
- `raccogli.py` -> `grezzo.json`: 8 categorie x 15 best seller Etsy (query in `CATEGORIE`, ordine = recensioni).
- `genera_md.py` -> `LISTINO.md`: ordine di lavoro (giro tra categorie: prima i n.1 di ognuna, poi i n.2...), senza doppioni, senza fisici.
- `prepara.py [N]` -> per i prossimi N non fatti: foto in `automation/base/<id>-orig.jpg` + scheda in `schede/<id>.json`.
- `stato.json`: {listing_id: {"stato": "fatto|saltato", "id": pid}} (aggiornalo a ogni prodotto, poi rilancia `genera_md.py`).
- `automation/prodotti/_visti.json`: ID Etsy gia' usati (esclusi dal listino).

## Step per ogni lotto
1. `python automation\listino\genera_md.py` (aggiorna LISTINO.md).
2. `python automation\listino\prepara.py 10` (foto + schede dei prossimi 10).
3. Per ogni scheda: scrivere `automation/prodotti/<id>.json` (copia `_esempio.json`): testi IT/EN SOLO da dati dell'annuncio, `prezzo_centesimi` = 3x acquisto Etsy arrotondato tondo (`comune.prezzo.vendita`), categoria, foto.cosa/it/en.
4. `python automation\nuovo_prodotto.py <id>` (categoria, catalogo, pagine IT/EN, foto IT+EN, commit+push).
5. Segnare in `stato.json`, rilanciare `genera_md.py`, passare al lotto dopo.

## Categorie sito (id -> nome)
planner, budget, habit, matrimonio, bambini, pasti, uncinetto, cv (nomi IT/EN in `raccogli.py`). Categoria dell'annuncio = quella del giro (puo' essere corretta nel JSON prodotto).

## Appunti utili
- Ricerche Etsy: `comune.etsy.cerca` apre un browser VISIBILE (mai headless), cache in `rivendita etsy\ricerche`; ~15 s a ricerca, un browser alla volta, poche richieste.
- Il listino puo' contenere varianti dello stesso prodotto con ID diversi: guardare titolo e foto prima di duplicare.
- Foto: fedeli all'originale (stesso prodotto, sfondo bianco, testi tradotti IT/EN). Planner/calendari con date: `render=True` in `foto_digitale.py`, mai Gemini per tabelle/numeri.
- Prezzi in `prezzo_centesimi`; prezzo vendita tondo (mai ,99).
- Mai riscrivere catalogo.json con PowerShell (BOM): solo Python json.
- Verifica online la fa Mirco dopo il push. Guardare la foto IT prima di dire fatto.
- Licenza: molti file Etsy sono "solo uso personale". Prima di vendere un prodotto controllare che l'annuncio non vieti la rivendita.
