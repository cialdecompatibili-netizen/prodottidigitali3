# -*- coding: utf-8 -*-
"""
UN SOLO COMANDO per un nuovo prodotto digitale: python automation\nuovo_prodotto.py <id> [--no-push]
Legge automation/prodotti/<id>.json (vedi automation/prodotti/_esempio.json) e fa TUTTO:
categoria (se nuova: catalogo + pagine IT/EN) -> voce catalogo -> pagine prodotto IT/EN -> foto IT/EN (foto_digitale) -> 1 commit + push.
Serve solo: automation/base/<id>-orig.jpg (foto originale Etsy). Idempotente: rilanciabile.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import foto_digitale as F

R = F.R
def w(rel, txt):
    p = os.path.join(R, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write(txt)
def fm(**k):
    return '---\n' + ''.join('%s: %s\n' % (a, json.dumps(b, ensure_ascii=False) if isinstance(b, str) and a in ('title', 'description') else b) for a, b in k.items()) + '---\n'

def main(pid, push=True):
    s = json.load(open(os.path.join(R, 'automation', 'prodotti', pid + '.json'), encoding='utf-8'))
    it, en, cat = s['it'], s['en'], s['categoria']
    cp = os.path.join(R, '_data', 'catalogo.json'); raw = open(cp, encoding='utf-8').read(); c = json.loads(raw)
    # categoria nuova -> catalogo (il menu la mostra da solo) + pagine IT/EN
    if not [x for x in c['categorie'] if x['id'] == cat['id']]:
        c['categorie'].append(dict(nome=cat['it'], id=cat['id'], icona=cat.get('icona', '\U0001F4E6'), tr=dict(en=dict(nome=cat['en']))))
        w('_negozio/categoria-%s.md' % cat['id'], fm(layout='negozio-categoria', title=cat['it'], cid=cat['id'], permalink='/negozio/categoria/%s/' % cat['id'], ref='shop-cat-' + cat['id']))
        w('en/negozio/categoria/%s.md' % cat['slug_en'], fm(layout='negozio-categoria', title=cat['en'], cid=cat['id'], permalink='/en/shop/category/%s/' % cat['slug_en'],
          description=cat['en'], lang='en', locale='en', tr='tradotto', ref='shop-cat-' + cat['id']))
    # voce catalogo (non tocca l'immagine: la mette foto_digitale)
    e = [x for x in c['prodotti'] if x['id'] == pid]
    old = e[0] if e else {}
    new = dict(tipo='digitale', id=pid, nome=it['nome'], categoria=cat['id'], prezzo_centesimi=s['prezzo_centesimi'], descrizione=it['descrizione'],
               descrizione_completa=it['descrizione_completa'], immagine=old.get('immagine', 'assets/images/prodotti/%s.webp?v=0' % pid), icona=s.get('icona', cat.get('icona', '\U0001F4E6')),
               visibile=True, tr=dict(en=dict(nome=en['nome'], descrizione=en['descrizione'], descrizione_completa=en['descrizione_completa'],
               immagine=old.get('tr', {}).get('en', {}).get('immagine', 'assets/images/prodotti/%s-en.webp?v=0' % pid))))
    if e: c['prodotti'][c['prodotti'].index(old)] = new
    else: c['prodotti'].append(new)
    open(cp, 'w', encoding='utf-8', newline='\n').write(json.dumps(c, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
    # pagine prodotto
    w('_negozio/%s.md' % pid, fm(layout='negozio-prodotto', title=it['nome'], pid=pid, permalink='/negozio/%s/' % pid, description=it['descrizione'], ref='shop-prod-' + pid))
    w('en/negozio/%s.md' % pid, fm(layout='negozio-prodotto', title=en['nome'], pid=pid, permalink='/en/shop/%s/' % s['slug_en'], description=en['descrizione'],
      lang='en', locale='en', tr='tradotto', ref='shop-prod-' + pid))
    # foto (scrive anche ?v= nel catalogo)
    F.PRODOTTI[pid] = s['foto']; F.main(pid, push=False)
    if push:
        g = lambda *a: print(subprocess.run(['git', '-C', R, *a], capture_output=True, text=True, encoding='utf-8').stdout.strip())
        g('add', '_data/catalogo.json', '_negozio', 'en/negozio', 'assets/images/prodotti', 'automation')
        g('commit', '-q', '-m', 'Prodotto %s: catalogo, pagine IT/EN e foto' % pid); g('pull', '-q', '--rebase'); g('push', '-q'); print('push ok')
    b = 'https://cialdecompatibili-netizen.github.io/prodottidigitali3'
    print('IT %s/negozio/%s/\nEN %s/en/shop/%s/' % (b, pid, b, s['slug_en']))

if __name__ == '__main__':
    main(sys.argv[1], '--no-push' not in sys.argv)
