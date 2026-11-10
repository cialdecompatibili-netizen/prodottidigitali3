# -*- coding: utf-8 -*-
r"""STEP 2 listino: python automation\listino\genera_md.py -> legge grezzo.json (+ stato.json) e scrive LISTINO.md.
Ordine di lavoro = giro tra le categorie (prima i n.1 di ogni categoria, poi i n.2...), best seller Etsy per recensioni.
Esclusi: doppioni tra categorie, prodotti fisici (FISICO), non digitali (DIGITALE). stato.json = {listing_id: {stato, id}}; _visti.json = gia' usati."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(HERE, 'grezzo.json'), encoding='utf-8'))
sp = os.path.join(HERE, 'stato.json')
stato = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
visti = set(json.load(open(os.path.join(HERE, '..', 'prodotti', '_visti.json'), encoding='utf-8')))
lid = lambda l: (re.search(r'/listing/(\d+)', l) or [0, ''])[1]
FISICO = re.compile(r'acrilic|busta|buste|lamina|foderat|stampa acquerello|rilegat|cartaceo|libretto', re.I)
DIGITALE = re.compile(r'pdf|stampabil|printable|template|modell|schem|pattern|foglio di calcolo|spreadsheet|sheets|excel|canva|download|digital|planner|agenda|pacchetto|curriculum|resume', re.I)
ordine, gia, scartati = [], set(), []
for pos in range(15):
    for cid, c in g.items():
        if pos < len(c['prodotti']):
            p = c['prodotti'][pos]; i = lid(p['link'])
            if i in gia: continue
            gia.add(i)
            if FISICO.search(p['nome']) or not DIGITALE.search(p['nome']): scartati.append((cid, p)); continue
            ordine.append((cid, pos + 1, p))
R = ['# LISTINO prodotti digitali (best seller Etsy)', '',
 'Generato da `automation/listino/genera_md.py` da `grezzo.json`. Guida e step: `GUIDA.md`. Stato: `stato.json`.', '',
 '## Ordine di lavoro (giro tra categorie, dal piu\' venduto)', '', '| # | stato | categoria | pos | prodotto | prezzo Etsy | link |', '|---|---|---|---|---|---|---|']
for n, (cid, pos, p) in enumerate(ordine, 1):
    i = lid(p['link']); s = stato.get(i, {}).get('stato') or ('fatto' if i in visti else '-')
    R.append('| %d | %s | %s | %d | %s | %s | [%s](%s) |' % (n, s, cid, pos, p['nome'].replace('|', '/')[:90], p.get('prezzo') or '', i, p['link'].split('?')[0]))
R += ['', '## Scartati (fisici / non digitali / doppioni non mostrati)', '']
for cid, p in scartati: R.append('- %s: %s (%s)' % (cid, p['nome'][:80], lid(p['link'])))
R += ['', '## Per categoria', '']
for cid, c in g.items():
    R += ['### %s - %s / %s' % (cid, c['it'], c['en']), 'Query Etsy: `%s`' % c['query'], '']
    for k, p in enumerate(c['prodotti'], 1): R.append('%d. %s - %s - %s' % (k, p['nome'][:90], p.get('prezzo') or '', p['link'].split('?')[0]))
    R.append('')
open(os.path.join(HERE, 'LISTINO.md'), 'w', encoding='utf-8').write('\n'.join(R))
print('LISTINO.md', len(ordine), 'prodotti,', len(scartati), 'scartati')
