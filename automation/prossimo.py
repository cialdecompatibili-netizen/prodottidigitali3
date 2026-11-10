# -*- coding: utf-8 -*-
"""python automation\prossimo.py "<query etsy>" [n]  -> cerca su Etsy, salta i prodotti gia' usati (_visti.json),
scarica la foto in automation\base\<id>-orig.jpg e stampa id/titolo/prezzo/link/descrizione per compilare il JSON.
Poi: python automation\nuovo_prodotto.py <id>"""
import json, os, re, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune')
sys.path.insert(0, r'C:\Users\mirco\Desktop\rivendita etsy')
from comune import etsy
VISTI = os.path.join(HERE, 'prodotti', '_visti.json')
visti = json.load(open(VISTI, encoding='utf-8')) if os.path.exists(VISTI) else ['4307530578', '4306147635', '4523902579', '1871622641']
lid = lambda l: (re.search(r'/listing/(\d+)', l) or [0, l])[1]
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
for r in etsy.cerca(q, n=n):
    if lid(r['link']) in visti: continue
    pid = re.sub(r'\W+', '-', r['nome'].lower().encode('ascii', 'ignore').decode()).strip('-')
    pid = '-'.join(pid.split('-')[:6]) + '-' + lid(r['link'])[-4:]
    dest = os.path.join(HERE, 'base', pid + '-orig.jpg')
    for u in (r['foto_url'].replace('il_794xN', 'il_1588xN'), r['foto_url']):
        try:
            urllib.request.urlretrieve(u, dest); break
        except Exception: pass
    try: d = etsy.dettaglio(r['link'])
    except Exception as e: d = {}
    visti.append(lid(r['link'])); json.dump(visti, open(VISTI, 'w', encoding='utf-8'))
    print(json.dumps(dict(id=pid, etsy_titolo=r['nome'], prezzo=r['prezzo'], link=r['link'], foto=os.path.exists(dest), dettaglio=str(d)[:1200]), ensure_ascii=False, indent=1))
    break
else:
    print('NESSUN NUOVO RISULTATO per', q)
