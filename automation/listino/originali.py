# -*- coding: utf-8 -*-
r"""STEP 3 (originali): python automation\listino\originali.py
Legge originali.json (chiave = pid della scheda; testi IT/EN e prompt foto NOSTRI, ispirati al best seller ma non identici)
e crea automation\prodotti\<pid_nuovo>.json con foto.originale (1 sola immagine Gemini, uguale IT/EN, senza testo).
Prezzo = comune.prezzo.vendita(acquisto Etsy dalla scheda). Scrive lotto_orig.json = [[pid_nuovo, listing], ...].
Prodotti nuovi: aggiungi una voce a originali.json (python originali.py --nuovi elenca le schede senza voce), poi rilancia.
Dopo: python automation\listino\lancia.py lotto_orig.json [N]"""
import json, os, re, sys
sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune')
from comune import prezzo
HERE = os.path.dirname(os.path.abspath(__file__)); PROD = os.path.join(HERE, '..', 'prodotti')
CAT = {
 'planner': dict(id='planner', it='Planner e agende stampabili', en='Printable planners and agendas', slug_en='planners', icona='\U0001F4C5'),
 'budget': dict(id='budget', it='Budget e finanze', en='Budget and finance', slug_en='budget-finance', icona='\U0001F4B6'),
 'bambini': dict(id='bambini', it='Giochi e attivita stampabili', en='Printable games and activities', slug_en='games-activities', icona='\U0001F9E9'),
 'pasti': dict(id='pasti', it='Meal planner e cucina', en='Meal planners and kitchen', slug_en='meal-planners', icona='\U0001F37D'),
 'uncinetto': dict(id='uncinetto', it='Schemi uncinetto PDF', en='Crochet patterns PDF', slug_en='crochet-patterns', icona='\U0001F9F6'),
 'cv': dict(id='cv', it='Curriculum e lavoro', en='Resume and career', slug_en='resume-career', icona='\U0001F4C4'),
 'matrimonio': dict(id='matrimonio', it='Matrimonio e inviti', en='Wedding and invitations', slug_en='wedding-invitations', icona='\U0001F48C'),
 'habit': dict(id='habit', it='Habit tracker e routine', en='Habit trackers and routines', slug_en='habit-trackers', icona='\u2705'),
}
O = json.load(open(os.path.join(HERE, 'originali.json'), encoding='utf-8'))
sched = {}
for f in os.listdir(os.path.join(HERE, 'schede')):
    if f.endswith('.json'):
        s = json.load(open(os.path.join(HERE, 'schede', f), encoding='utf-8')); sched[s['pid']] = s
if '--nuovi' in sys.argv:
    for k, s in sched.items():
        if k not in O: print(k, '|', s['titolo'][:70])
    sys.exit()
os.makedirs(PROD, exist_ok=True); lotto = []
for k, o in O.items():
    s = sched.get(k)
    if not s: print('scheda mancante', k); continue
    acq = float(re.search(r'[\d.,]+', s['prezzo_etsy']).group().replace('.', '').replace(',', '.'))
    c = CAT[o['cat']]; it, en = o['it'], o['en']
    d = dict(categoria=c, slug_en=o['slug_en'], prezzo_centesimi=int(prezzo.vendita(acq)) * 100, icona=c['icona'],
             it=dict(nome=it[0], descrizione=it[1], descrizione_completa=it[2]), en=dict(nome=en[0], descrizione=en[1], descrizione_completa=en[2]),
             foto=dict(cosa=en[0], originale=o['foto'], it='', en=''))
    json.dump(d, open(os.path.join(PROD, o['pid'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lotto.append([o['pid'], s['listing']]); print(o['pid'], d['prezzo_centesimi'])
json.dump(lotto, open(os.path.join(HERE, 'lotto_orig.json'), 'w'))
