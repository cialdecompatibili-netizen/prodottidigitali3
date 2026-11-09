# -*- coding: utf-8 -*-
"""
Foto prodotto IT + EN da una base Gemini SENZA testo + titolo scritto con Pillow (testo vero, lingua giusta).
Uso: python automation/foto_lingue.py [id]      (default: planner-annuale-2027-stampabile)
Fa tutto: ritaglia la base (automation/base/<id>-base.webp), scrive assets/images/prodotti/<id>.webp (IT) e <id>-en.webp (EN),
collega catalogo.json (immagine + tr.en.immagine, cache ?v=n), commit e push.
Base nuova: python C:\\Users\\mirco\\Desktop\\gemini_auto\\img.py "<oggetto vuoto>" --profilo prodotto --nome <id>-base --out automation\\base --extra "ABSOLUTELY NO TEXT..."
Nuovo prodotto = aggiungere una voce in TESTI. Altra lingua = aggiungere una chiave (es. 'de') e una riga in LINGUE.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = r'C:\Windows\Fonts'
INK, GOLD, SAGE = (45, 55, 72), (184, 154, 90), (110, 120, 135)
TESTI = {
 'planner-annuale-2027-stampabile': {
  'it': dict(t1='Planner annuale', t2='2027', sub='Agenda e calendario da parete', fmt='PDF  ·  Lettera  ·  A0  ·  A1  ·  A2  ·  A3  ·  A4'),
  'en': dict(t1='Annual Planner', t2='2027', sub='Agenda and wall calendar', fmt='PDF  ·  Letter  ·  A0  ·  A1  ·  A2  ·  A3  ·  A4')},
}
LINGUE = {'it': '', 'en': '-en'}

def F(n, s): return ImageFont.truetype(os.path.join(FD, n), s)

def centra(d, y, t, f, fill, W=2000):
    d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=fill)

def base(pid):
    im = Image.open(os.path.join(R, 'automation', 'base', pid + '-base.webp')).convert('RGB')
    bb = ImageChops.invert(ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 6 else 0)).getbbox()
    bb = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 6 else 0).getbbox()
    return im.crop(bb)

def disegna(pid, t, b):
    W = 2000
    im = Image.new('RGB', (W, W), (255, 255, 255)); d = ImageDraw.Draw(im)
    centra(d, 150, t['t1'], F('georgiab.ttf', 150), INK)
    centra(d, 330, t['t2'], F('georgiab.ttf', 190), GOLD)
    centra(d, 560, t['sub'], F('georgiai.ttf', 62), SAGE)
    k = 1700 / b.width; b2 = b.resize((1700, int(b.height * k)), Image.LANCZOS)
    im.paste(b2, ((W - 1700) // 2, 800))
    centra(d, 800 + b2.height + 90, t['fmt'], F('georgia.ttf', 58), INK)
    return im.resize((1000, 1000), Image.LANCZOS)

def main(pid):
    out = os.path.join(R, 'assets', 'images', 'prodotti'); b = base(pid)
    for l, suf in LINGUE.items():
        disegna(pid, TESTI[pid][l], b).save(os.path.join(out, pid + suf + '.webp'), 'WEBP', quality=90)
    p = os.path.join(R, '_data', 'catalogo.json'); raw = open(p, encoding='utf-8').read(); c = json.loads(raw)
    x = [q for q in c['prodotti'] if q['id'] == pid][0]
    v = int(x.get('immagine', '?v=0').split('?v=')[-1] or 0) + 1 if '?v=' in x.get('immagine', '') else 1
    x['immagine'] = 'assets/images/prodotti/%s.webp?v=%d' % (pid, v)
    x.setdefault('tr', {}).setdefault('en', {})['immagine'] = 'assets/images/prodotti/%s-en.webp?v=%d' % (pid, v)
    open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(c, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
    g = lambda *a: print(subprocess.run(['git', '-C', R, *a], capture_output=True, text=True, encoding='utf-8').stdout.strip())
    g('add', '_data/catalogo.json', 'assets/images/prodotti', 'automation'); g('commit', '-m', 'Foto %s: versione IT e EN (base Gemini + testo Pillow)' % pid)
    g('pull', '--rebase'); g('push'); print('ok', pid)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'planner-annuale-2027-stampabile')
