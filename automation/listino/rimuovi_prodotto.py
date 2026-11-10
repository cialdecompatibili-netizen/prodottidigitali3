# -*- coding: utf-8 -*-
r"""python automation\listino\rimuovi_prodotto.py <id>  -> toglie catalogo, pagine IT/EN e foto di un prodotto (niente git: lo fa chi chiama)."""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pid = sys.argv[1]
cp = os.path.join(R, '_data', 'catalogo.json'); raw = open(cp, encoding='utf-8').read(); c = json.loads(raw)
c['prodotti'] = [x for x in c['prodotti'] if x['id'] != pid]
open(cp, 'w', encoding='utf-8', newline='\n').write(json.dumps(c, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
for rel in ('_negozio/%s.md' % pid, 'en/negozio/%s.md' % pid, 'assets/images/prodotti/%s.webp' % pid, 'assets/images/prodotti/%s-en.webp' % pid):
    if os.path.exists(os.path.join(R, rel)): os.remove(os.path.join(R, rel)); print('rimosso', rel)
