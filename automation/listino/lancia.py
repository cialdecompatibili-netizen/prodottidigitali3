# -*- coding: utf-8 -*-
"""Compatibilita': python automation\listino\lancia.py [lotto.json] [N]  -> usa il motore di auto.py (timeout, riprova, stato). Per il flusso completo: auto.py [N]."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import auto
lotto = json.load(open(os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'lotto_orig.json')))
print(auto.lancia(lotto, int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6))
