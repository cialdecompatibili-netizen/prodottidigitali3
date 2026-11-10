# -*- coding: utf-8 -*-
r"""STEP 3 listino: python automation\listino\prepara.py [N]  -> per i prossimi N prodotti NON fatti del LISTINO (ordine di lavoro):
scarica la foto Etsy in automation\base\<id>-orig.jpg e salva automation\listino\schede\<id>.json (titolo, prezzo Etsy, link, categoria, dettaglio annuncio).
Poi si scrive automation\prodotti\<id>.json (testi IT/EN, prezzo = prezzo.vendita(acquisto)) e si lancia nuovo_prodotto.py <id>."""
import json, os, re, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune'); sys.path.insert(0, r'C:\Users\mirco\Desktop\rivendita etsy')
import genera_md as L
from comune import etsy
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
SCH = os.path.join(HERE, 'schede'); os.makedirs(SCH, exist_ok=True)
lid = L.lid
fatti = 0
for cid, pos, p in L.ordine:
    i = lid(p['link'])
    if i in L.visti or L.stato.get(i, {}).get('stato') in ('fatto', 'saltato'): continue
    if fatti >= N: break
    pid = re.sub(r'\W+', '-', p['nome'].lower().encode('ascii', 'ignore').decode()).strip('-')
    pid = '-'.join(pid.split('-')[:6]) + '-' + i[-4:]
    sf = os.path.join(SCH, pid + '.json')
    if os.path.exists(sf): fatti += 1; continue
    dest = os.path.join(HERE, '..', 'base', pid + '-orig.jpg')
    for u in (p['foto_url'].replace('il_794xN', 'il_1588xN'), p['foto_url']):
        try: urllib.request.urlretrieve(u, dest); break
        except Exception: pass
    try: d = etsy.dettaglio(p['link'])
    except Exception as e: d = {'errore': str(e)}
    json.dump(dict(pid=pid, listing=i, categoria=cid, pos=pos, titolo=p['nome'], prezzo_etsy=p.get('prezzo'), link=p['link'].split('?')[0],
                   foto=os.path.exists(dest), dettaglio=str(d)[:2500]), open(sf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(pid, cid, p.get('prezzo'), flush=True); fatti += 1
