# -*- coding: utf-8 -*-
r"""STEP 5 listino: python automation\listino\lancia.py [lotto1.json]  -> nuovo_prodotto.py per ogni id del lotto (uno dopo l'altro), aggiorna stato.json e LISTINO.md.
Si ferma al primo errore. Rilanciabile: salta quelli gia' 'fatto' in stato.json."""
import json, os, subprocess, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(HERE))
lotto = json.load(open(os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'lotto1.json')))
sp = os.path.join(HERE, 'stato.json')
for pid in lotto:
    stato = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    scheda = json.load(open(os.path.join(HERE, 'schede', pid + '.json'), encoding='utf-8'))
    if stato.get(scheda['listing'], {}).get('stato') == 'fatto': continue
    r = subprocess.run([sys.executable, os.path.join(R, 'automation', 'nuovo_prodotto.py'), pid], cwd=R, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('==', pid, 'exit', r.returncode); print((r.stdout or '')[-500:]); print((r.stderr or '')[-400:], flush=True)
    ok = r.returncode == 0 and 'push ok' in (r.stdout or '') and 'KO' not in (r.stdout or '')
    stato[scheda['listing']] = dict(stato='fatto' if ok else 'errore', id=pid)
    json.dump(stato, open(sp, 'w', encoding='utf-8'), indent=1)
    if not ok: print('STOP'); break
subprocess.run([sys.executable, os.path.join(HERE, 'genera_md.py')], cwd=R)
