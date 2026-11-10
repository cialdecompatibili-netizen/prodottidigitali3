# -*- coding: utf-8 -*-
r"""STEP 5 listino: python automation\listino\lancia.py [lotto.json] [N]  -> nuovo_prodotto.py per ogni voce (uno dopo l'altro), aggiorna stato.json e LISTINO.md.
Voci del lotto: "pid" (scheda con lo stesso pid) oppure ["pid_nuovo", "listing_etsy"] (prodotti originali, vedi originali.py).
N = al massimo N prodotti da fare ora. Si ferma al primo errore. Rilanciabile: salta quelli gia' 'fatto' in stato.json."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(HERE))
lotto = json.load(open(os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'lotto1.json')))
maxn = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
sp = os.path.join(HERE, 'stato.json'); fatti = 0
for v in lotto:
    if fatti >= maxn: break
    pid, listing = (v if isinstance(v, list) else (v, json.load(open(os.path.join(HERE, 'schede', v + '.json'), encoding='utf-8'))['listing']))
    stato = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    if stato.get(listing, {}).get('stato') == 'fatto': continue
    r = subprocess.run([sys.executable, os.path.join(R, 'automation', 'nuovo_prodotto.py'), pid], cwd=R, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('==', pid, 'exit', r.returncode); print((r.stdout or '')[-500:]); print((r.stderr or '')[-400:], flush=True)
    ok = r.returncode == 0 and 'push ok' in (r.stdout or '') and 'KO' not in (r.stdout or '')
    stato[listing] = dict(stato='fatto' if ok else 'errore', id=pid)
    json.dump(stato, open(sp, 'w', encoding='utf-8'), indent=1)
    if not ok: print('STOP'); break
    fatti += 1
subprocess.run([sys.executable, os.path.join(HERE, 'genera_md.py')], cwd=R)
