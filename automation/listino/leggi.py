import json,glob,re,html
for f in sorted(glob.glob('schede/*.json')):
    d=json.load(open(f,encoding='utf-8'))
    m=re.search(r'"description":"(.*?)","', d['dettaglio'])
    t=m.group(1) if m else d['dettaglio'][:600]
    try: t=json.loads('"'+t+'"')
    except Exception: pass
    t=html.unescape(t).replace('\\n',' ').replace('\n',' ')
    print('##',d['pid'],d['categoria'],d['prezzo_etsy']); print(d['titolo'][:130]); print(t[:560]); print()
