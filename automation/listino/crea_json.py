# -*- coding: utf-8 -*-
r"""STEP 4 listino (lotto 1, primi 10): crea automation\prodotti\<id>.json per ogni scheda con testi IT/EN scritti SOLO dai dati dell'annuncio.
Prezzo = comune.prezzo.vendita(acquisto Etsy) (3x tondo). Poi: python automation\listino\lancia.py (nuovo_prodotto.py per ognuno)."""
import json, os, sys
sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune')
from comune import prezzo
HERE = os.path.dirname(os.path.abspath(__file__))
CAT = {
 'planner': dict(id='planner', it='Planner e agende stampabili', en='Printable planners and agendas', slug_en='planners', icona='\U0001F4C5'),
 'budget': dict(id='budget', it='Budget e finanze', en='Budget and finance', slug_en='budget-finance', icona='\U0001F4B6'),
 'bambini': dict(id='bambini', it='Giochi e attivita stampabili', en='Printable games and activities', slug_en='games-activities', icona='\U0001F9E9'),
 'pasti': dict(id='pasti', it='Meal planner e cucina', en='Meal planners and kitchen', slug_en='meal-planners', icona='\U0001F37D'),
 'uncinetto': dict(id='uncinetto', it='Schemi uncinetto PDF', en='Crochet patterns PDF', slug_en='crochet-patterns', icona='\U0001F9F6'),
 'cv': dict(id='cv', it='Curriculum e lavoro', en='Resume and career', slug_en='resume-career', icona='\U0001F4C4'),
 'matrimonio': dict(id='matrimonio', it='Matrimonio e inviti', en='Wedding and invitations', slug_en='wedding-invitations', icona='\U0001F48C'),
}
FIT = 'Translate every visible text on the image into Italian (leave it as is if already Italian). Keep numbers, icons, layout, fonts and colours identical.'
FEN = 'Translate every visible text on the image into English (leave it as is if already English). Keep numbers, icons, layout, fonts and colours identical.'
P = [
 ('pacchetto-diario-2027-agenda-stampabile-bullet-2391', 'planner', 7.54, 'printable-journal-planner-2027-bundle',
  'Pacchetto diario e agenda 2027 stampabile PDF', 'Agenda e bullet journal 2027 in PDF A4 e A5, con tracker annuali per abitudini, umore, fitness e lettura.',
  'Pacchetto diario 2027 in PDF stampabile, formati A4 e A5: agenda e bullet journal in un unico download, con tracker annuali per abitudini, umore, fitness e lettura. Scarichi subito i file e li stampi a casa.',
  'Printable 2027 Journal and Planner Bundle PDF', '2027 planner and bullet journal in A4 and A5 PDF, with yearly habit, mood, fitness and reading trackers.',
  'Printable 2027 journal bundle in A4 and A5 PDF: planner and bullet journal in a single download, with yearly habit, mood, fitness and reading trackers. Download instantly and print at home.',
  'a printable 2027 journal and planner bundle: collage of bullet journal, habit, mood, fitness and reading tracker pages'),
 ('life-planner-google-sheets-dark-mode-1487', 'budget', 18.12, 'life-planner-google-sheets-dark-mode',
  'Life Planner Google Sheets in modalita scura', 'Organizer personale in foglio di calcolo con budget annuale, habit tracker e risparmi, in modalita scura.',
  'Life Planner in Google Sheets con tema scuro: budget annuale, monitoraggio di abitudini, risparmi e organizzazione personale in un unico file. Valido per il 2026-2027 e per tutti gli anni.',
  'Life Planner Google Sheets Dark Mode', 'Personal organizer spreadsheet with annual budget, habit tracker and savings, in dark mode.',
  'Life Planner for Google Sheets in dark mode: annual budget, habit tracking, savings and personal organization in one file. Works for 2026-2027 and every other year.',
  'a dark mode Life Planner spreadsheet dashboard for Google Sheets with budget tracker, habit tracker and savings tracker tabs'),
 ('raccoglitore-didattico-montessori-stampabile-per-bambini-0779', 'bambini', 12.34, 'printable-montessori-learning-binder',
  'Raccoglitore didattico Montessori stampabile', 'Raccoglitore Montessori stampabile per bambini piccoli: attivita prescolari e libro tranquillo.',
  'Raccoglitore didattico Montessori stampabile per bambini piccoli: libro interattivo con attivita prescolari da stampare a casa, ideale come libro tranquillo.',
  'Printable Montessori Learning Binder', 'Printable Montessori binder for toddlers: preschool activities and quiet book.',
  'Printable Montessori learning binder for toddlers: an interactive book of preschool activities to print at home, ideal as a quiet book.',
  'a printable Montessori learning binder for toddlers with preschool activity pages'),
 ('foglio-di-calcolo-per-la-pianificazione-5814', 'pasti', 9.13, 'weekly-meal-planner-spreadsheet',
  'Foglio di calcolo pianificatore settimanale dei pasti', 'Pianificatore settimanale dei pasti per la famiglia con organizzatore di ricette e inventario della cucina.',
  'Modello digitale per pianificare i pasti della settimana in famiglia: organizzatore di ricette, tracker dell inventario della cucina e lista della spesa. Si usa come foglio di calcolo oppure si stampano le linguette.',
  'Weekly Meal Planner Spreadsheet', 'Weekly family meal planner with recipe organizer and kitchen inventory tracker.',
  'Digital template to plan the family meals of the week: recipe organizer, kitchen inventory tracker and shopping list. Use it as a spreadsheet or print the tabs.',
  'a weekly meal planner spreadsheet template with recipe organizer and kitchen inventory tracker'),
 ('pacchetto-completo-di-modelli-all-uncinetto-3168', 'uncinetto', 3.66, 'complete-crochet-pattern-bundle-pdf',
  'Pacchetto completo di schemi uncinetto PDF', 'Collezione di schemi amigurumi e peluche all uncinetto in PDF, adatta ai principianti.',
  'Pacchetto completo di schemi all uncinetto in PDF: mega collezione di modelli amigurumi e peluche di animali, adatta anche ai principianti. Scarichi subito i file.',
  'Complete Crochet Pattern Bundle PDF', 'Amigurumi and plush crochet pattern collection in PDF, beginner friendly.',
  'Complete crochet pattern bundle in PDF: a mega collection of amigurumi and animal plush patterns, beginner friendly. Download the files instantly.',
  'a bundle of crochet amigurumi animal plush patterns in PDF, collage of finished crochet toys'),
 ('modello-di-curriculum-ats-compatibile-con-6425', 'cv', 9.08, 'ats-resume-template-word-docs-pages',
  'Modello di curriculum ATS compatibile', 'Curriculum minimalista compatibile ATS per Word, Pages e Google Docs.',
  'Modello di curriculum compatibile con i sistemi ATS, in stile minimalista, utilizzabile con Word, Pages e Google Docs.',
  'ATS Friendly Resume Template', 'Minimalist ATS compatible resume for Word, Pages and Google Docs.',
  'ATS compatible resume template with a minimalist style, usable with Word, Pages and Google Docs.',
  'a minimalist ATS friendly resume template page'),
 ('2027-printable-journal-bundle-600-digital-4701', 'planner', 9.76, 'printable-journal-600-inserts-2027',
  'Pacchetto journal 2027 con oltre 600 pagine stampabili', 'Oltre 600 pagine PDF A4 e A5: tracker di abitudini, finanze, fitness, pasti, letture e umore.',
  'Pacchetto journal 2027 stampabile con oltre 600 inserti in PDF, formati A4 e A5: tracker di abitudini, finanze, fitness, pasti, letture e umore. Il PDF e pronto da stampare e non e modificabile.',
  '2027 Printable Journal Bundle 600+ Inserts', '600+ printable A4 and A5 PDF pages: habit, finance, fitness, meal, reading and mood trackers.',
  '2027 printable journal bundle with 600+ inserts in A4 and A5 PDF: habit, finance, fitness, meal, reading and mood trackers. Ready-to-print PDF, not editable.',
  'a 2027 printable journal bundle with 600+ planner inserts: habit, finance, fitness, meal, reading and mood trackers'),
 ('pianificatore-di-bilancio-annuale-strumento-definitivo-2080', 'budget', 12.56, 'annual-budget-planner-paycheck',
  'Pianificatore di bilancio annuale', 'Strumento per monitorare il bilancio annuale e mensile in base allo stipendio.',
  'Pianificatore di bilancio annuale e strumento di monitoraggio del budget: modello con bilancio mensile in base allo stipendio, per gestire le finanze di casa.',
  'Annual Budget Planner', 'Annual budget tracker with a monthly budget based on your paycheck.',
  'Annual budget planner and tracking tool: a template with a monthly budget based on your paycheck, to manage your household finances.',
  'an annual budget planner template with monthly paycheck based budget pages'),
 ('pacchetto-di-9-set-di-inviti-4210', 'matrimonio', 18.30, 'wedding-invitation-bundle-9-canva-sets',
  'Pacchetto 9 set di inviti di nozze modificabili su Canva', '9 set completi di inviti di nozze modificabili su Canva: stili western, floreale e italiano.',
  'Pacchetto di 9 set completi di inviti di nozze, modificabili su Canva, con design colorati in stile western, floreale e italiano. Download immediato.',
  'Wedding Invitation Bundle 9 Canva Sets', '9 complete wedding invitation sets editable on Canva: western, floral and Italian styles.',
  'Bundle of 9 complete wedding invitation sets, editable on Canva, with colorful western, floral and Italian style designs. Instant download.',
  'a bundle of nine wedding invitation suite designs, western floral and Italian styles, editable Canva templates'),
 ('mystery-manor-printable-escape-room-ages-7676', 'bambini', 15.98, 'mystery-manor-printable-escape-room',
  'Escape room stampabile Mystery Manor (12+ anni)', 'Escape room da stampare per ragazzi dai 12 anni: 13 enigmi, 1-8 giocatori, 45-60 minuti.',
  'Escape room stampabile in PDF per ragazzi dai 12 anni, difficolta avanzata: 1-8 giocatori, 45-60 minuti di gioco, circa 15 minuti di preparazione e 13 enigmi. Non serve internet ne lucchetti fisici.',
  'Mystery Manor Printable Escape Room (Ages 12+)', 'Printable escape room for ages 12+: 13 challenges, 1-8 players, 45-60 minutes.',
  'Printable PDF escape room for ages 12+, advanced difficulty: 1-8 players, 45-60 minutes of play, about 15 minutes of setup and 13 challenges. No internet and no physical locks needed.',
  'a printable escape room game Mystery Manor for ages 12+ with puzzle pages and clues'),
]
os.makedirs(os.path.join(HERE, '..', 'prodotti'), exist_ok=True)
for pid, cid, acq, slug, itn, itd, itc, enn, end, enc, cosa in P:
    d = dict(categoria=CAT[cid], slug_en=slug, prezzo_centesimi=int(prezzo.vendita(acq)) * 100, icona=CAT[cid]['icona'],
             it=dict(nome=itn, descrizione=itd, descrizione_completa=itc), en=dict(nome=enn, descrizione=end, descrizione_completa=enc),
             foto=dict(cosa=cosa, it=FIT, en=FEN))
    json.dump(d, open(os.path.join(HERE, '..', 'prodotti', pid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(pid, d['prezzo_centesimi'])
json.dump([p[0] for p in P], open(os.path.join(HERE, 'lotto1.json'), 'w'))
