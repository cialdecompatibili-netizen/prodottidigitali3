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

## Flusso automatico (usare questo)
- `python automation\listino\auto.py N` fa tutto (vedi docstring in auto.py). Niente browser Etsy: nome/prezzo/categoria vengono da grezzo.json.
- Per rinfrescare le best seller: raccogli.py. Voci curate a mano: originali.json (+ originali.py).

## Stato al 10/11/2026 (sera) - APPUNTI PER RIPARTIRE
**Online: 12 prodotti** (3 planner storici + lotto originali). Fatti dal listino: agenda-2027-minimal-journal, organizer-finanze-abitudini-google-sheets-scuro, quaderno-attivita-prescolari-stampabile, menu-settimanale-lista-spesa-sheets, raccolta-schemi-uncinetto-animali, curriculum-moderno-ats-word-docs, kit-tracker-2027-stampabile, budget-planner-mensile-stampabile, inviti-nozze-botanici-modificabili-canva, escape-room-stampabile-biblioteca-misteriosa, bingo-di-natale-stampabile-per-bambini, schede-didattiche-scuola-infanzia-stampabili. Restano circa 90 nel listino.
Sito: https://cialdecompatibili-netizen.github.io/prodottidigitali3/ (pagina prodotto: /negozio/<id>/ ; categoria bambini: /negozio/categoria/bambini/).

### Regole decise
- Prodotti ORIGINALI ispirati ai best seller Etsy, mai copie: testi nostri, foto nostra (Gemini da zero, senza testo, uguale IT/EN). Niente foto/firma di altri venditori.
- Prezzo = 3x acquisto Etsy, tondo (comune.prezzo.vendita). Mai ,99.
- Categoria bambini rinominata "Prodotti digitali per bambini" / "Digital printables for kids" (id bambini, slug_en games-activities, icona 🧸).
- Licenza: molti file Etsy sono "solo uso personale". Le descrizioni promettono contenuti: il file consegnato al cliente deve corrispondere (DA VERIFICARE, non ancora controllato).

### Comandi (tutto in Python, un solo comando)
- `python automation\listino\auto.py N` -> pubblica N prodotti: prima il lotto manuale in sospeso (lotto_orig.json), poi i prossimi del listino con testi in bozza automatica (bozza:true, generici ma corretti).
- `python automation\listino\auto.py --listing <ID_etsy>` -> un prodotto preciso; se c'e' la voce in `curati.json` (chiave = ID listing) usa i testi curati a mano.
- Lanciare in background con log (Start-Process + RedirectStandardOutput su auto.log) per non bloccare il tool; leggere auto.log dopo ~2 min per prodotto.
- Alla fine: stato.json, LISTINO.md, ULTIMO_LOTTO.md (link), anteprima.png (foto del lotto: guardarla prima di dire fatto), push automatico.
- Protezioni: timeout 8 min per prodotto (uccide l'albero di processi se Gemini si blocca) + 1 riprova, stop dopo 3 errori di fila. Rilanciabile, salta i 'fatto'.
- File: auto.py (motore), curati.json (testi a mano per listing), originali.json/originali.py (vecchio lotto manuale), lancia.py (wrapper), rimuovi_prodotto.py (toglie un prodotto sbagliato), stato.json.

### Costi / crediti Gemini
- 1 foto per prodotto (prima 2-3). Finestra crediti 5 ore: conviene lotti da 10-15. Stato: `python C:\Users\mirco\Desktop\gemini_auto\img.py --crediti` o CREDITI.md.
- Se Gemini si blocca: il processo img.py resta appeso (successo con il curriculum); ora il timeout lo gestisce.

### Idee non ancora fatte (ottimizzazioni)
- Una sola sessione Gemini per tutto il lotto (foto generate in un'unica chiamata img.py --lista, poi nuovo_prodotto salta la generazione se il webp esiste): circa -30% tempo sui lotti da 10+.
- Un solo push a fine lotto invece di uno per prodotto.
- Bambini: restano nel listino pacchetto educativo PLR (da evitare: licenza), attivita bibliche (nicchia), giochi del Ringraziamento (USA, poco utile in Italia).

### Prossimo passo
Attendere indicazioni di Mirco su quale lotto lanciare (es. `auto.py 10` a giro tra le categorie, oppure una categoria sola).

### REGOLA TITOLI (11/11/2026)
- Il titolo DEVE descrivere lo specifico prodotto (soggetto + formato, es. 'Schema uncinetto orsacchiotto amigurumi in PDF'), mai aggettivi generici tipo essenziale/elegante/colorato. Mai nomi di autori/venditori.
- Prima di lanciare auto.py su un listing va SEMPRE creata la voce in curati.json (titolo, descrizioni, prompt foto del soggetto reale). La bozza automatica generica non va usata per pubblicare.
