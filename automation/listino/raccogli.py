# -*- coding: utf-8 -*-
"""STEP 1 listino: python automation\listino\raccogli.py  -> cerca best seller Etsy per ogni categoria (CATEGORIE) e salva automation\listino\grezzo.json.
Usa comune.etsy.cerca (cache: non riapre il browser se la ricerca esiste gia'). Poche richieste, browser visibile."""
import json, os, sys
sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune')
from comune import etsy
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'grezzo.json')
# id categoria -> (nome IT, nome EN, query Etsy)
CATEGORIE = {
 'planner': ('Planner e agende stampabili', 'Printable planners and agendas', 'printable planner 2027'),
 'budget': ('Budget e finanze (foglio di calcolo)', 'Budget and finance spreadsheets', 'budget spreadsheet template'),
 'habit': ('Habit tracker e journaling', 'Habit trackers and journaling', 'habit tracker printable'),
 'matrimonio': ('Matrimonio e inviti', 'Wedding and invitations', 'wedding invitation template'),
 'bambini': ('Attivita per bambini stampabili', 'Printable kids activities', 'kids activity printable'),
 'pasti': ('Meal planner e ricette', 'Meal planners and recipes', 'meal planner printable'),
 'uncinetto': ('Schemi uncinetto PDF', 'Crochet patterns PDF', 'crochet pattern pdf'),
 'cv': ('Curriculum e lavoro', 'Resume and career templates', 'resume template'),
}
dati = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
for cid, (it, en, q) in CATEGORIE.items():
    if cid in dati and dati[cid].get('prodotti'): continue
    try:
        r = etsy.cerca(q, n=15)
    except Exception as e:
        print('ERRORE', cid, e); continue
    dati[cid] = dict(it=it, en=en, query=q, prodotti=[{k: x.get(k) for k in ('pos', 'nome', 'prezzo', 'link', 'foto_url', 'foto')} for x in r])
    json.dump(dati, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(cid, len(r), flush=True)
