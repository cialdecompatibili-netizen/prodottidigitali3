# -*- coding: utf-8 -*-
"""
Foto prodotti DIGITALI fedeli all'annuncio: foto originale Etsy -> Gemini (sfondo bianco + traduzione dei testi, stesso prodotto) -> IT + EN.
Uso: python automation/foto_digitale.py <id> [--solo it|en] [--no-push]
Serve: automation/base/<id>-orig.jpg (foto originale dell'annuncio) e una voce in PRODOTTI qui sotto.
Regola: il prodotto mostrato NON si ridisegna (stessa griglia, mesi, date, colonne): Gemini cambia solo sfondo e lingua dei testi.
Altro prodotto = aggiungere una voce in PRODOTTI (cosa e' il prodotto + testi da tradurre). Altra lingua = voce in LINGUE.
"""
import json, os, subprocess, sys
sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune')
from comune import gemini_foto as G
from PIL import Image, ImageChops, ImageDraw, ImageFont

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINGUE = {'it': ('Italian', ''), 'en': ('English', '-en')}
PRODOTTI = {
 'bullet-journal-bundle-2027': dict(
  cosa='collage of printable bullet journal pages', overlay=dict(it=dict(
   riga2='BULLET JOURNAL COMPLETO', sotto='• PDF stampabile • 3 formati: US Letter, A4 e A5 • Inizio domenica e lunedì •',
   bollino1='500+', bollino2='planner e', bollino3='modelli',
   barra='Cura di sé • Pulizie • Stile di vita • Finanze • Viaggi • Produttività • Salute • Fitness'))
 ),
 'planner-annuale-2027-stampabile': dict(
  cosa='a printable 2027 year planner / wall calendar sheet (12 month rows x 31 day columns, each cell with day number and weekday initial, weekend cells shaded)',
  it='Translate every text into Italian exactly like this: "PRINTABLE & DIGITAL" -> "STAMPABILE E DIGITALE"; "2027 YEAR PLANNER" (both the headline and the title on the sheet) -> "PLANNER ANNUALE 2027"; '
     'month names JANUARY..DECEMBER -> GENNAIO, FEBBRAIO, MARZO, APRILE, MAGGIO, GIUGNO, LUGLIO, AGOSTO, SETTEMBRE, OTTOBRE, NOVEMBRE, DICEMBRE; '
     'weekday initials (M T W T F S S) -> Italian initials (L M M G V S D) keeping each day number on the SAME weekday as in the original; '
     '"MULTIPLE SIZES: A0, A1, A2, A3, A4, LETTER SIZE" -> "PIU FORMATI: A0, A1, A2, A3, A4, LETTER".',
  en='Keep all text in English exactly as in the original.',
  render=True,
  testi=dict(
   it=dict(top='STAMPABILE E DIGITALE', titolo='PLANNER ANNUALE 2027', formati='PIU FORMATI: A0, A1, A2, A3, A4, LETTER',
           mesi=['GENNAIO','FEBBRAIO','MARZO','APRILE','MAGGIO','GIUGNO','LUGLIO','AGOSTO','SETTEMBRE','OTTOBRE','NOVEMBRE','DICEMBRE'], gg='LMMGVSD'),
   en=dict(top='PRINTABLE & DIGITAL', titolo='2027 YEAR PLANNER', formati='MULTIPLE SIZES: A0, A1, A2, A3, A4, LETTER SIZE',
           mesi=['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER'], gg='MTWTFSS'))
 )
}

def prompt(p, lingua):
    return ('Edit this product listing photo. KEEP THE PRODUCT EXACTLY AS IT IS: ' + p['cosa'] + '. Same layout, same number of rows and columns, '
     'same months, same dates, same cells, same shading, same fonts and colours. Do NOT redraw, simplify, shorten, remove or invent any part of it. '
     'Only two changes: (1) replace the textured cream background with a plain pure white #FFFFFF background (keep the soft shadow under the sheet); '
     '(2) ' + p[lingua] + ' Keep the headline lines and the sizes line with the same style and positions. '
     'Square 1:1 image, everything centred with comfortable white margins. No extra objects, no watermark, no logo.')

def _font(nome, h_max, w_max, testo):
    # sceglie il corpo piu' grande che sta in larghezza w_max e altezza h_max (cosi' i testi tradotti, piu' lunghi, non escono dal riquadro)
    for sz in range(120, 8, -1):
        f = ImageFont.truetype('C:/Windows/Fonts/' + nome, sz)
        b = f.getbbox(testo)
        if b[2] - b[0] <= w_max and b[3] - b[1] <= h_max: return f
    return f

def render_overlay(p, l, orig):
    """Foto originale INTATTA (collage di pagine); si ricoprono solo i testi (titolo, sottotitolo, bollino, barra) e si riscrivono nella lingua. Per l'EN resta l'originale."""
    im = Image.open(orig).convert('RGB')
    if l not in p['overlay']: return im
    d = ImageDraw.Draw(im); s = im.width / 900.0; o = p['overlay'][l]
    def box(x0, y0, x1, y1): return [int(x0 * s), int(y0 * s), int(x1 * s), int(y1 * s)]
    def testo(t, cx, cy, wmax, hmax, font, col):
        f = _font(font, hmax * s, wmax * s, t); d.text((cx * s, cy * s), t, font=f, fill=col, anchor='mm')
    bianco, nero = (255, 255, 255), (0, 0, 0)
    for k, (b, cx, cy, wm, hm, font) in dict(riga2=((128, 74, 772, 120), 450, 97, 640, 44, 'seguibl.ttf'), sotto=((122, 124, 782, 150), 452, 137, 655, 20, 'segoeuib.ttf')).items():
        d.rectangle(box(*b), fill=bianco); testo(o[k], cx, cy, wm, hm, font, nero)
    rosso = im.getpixel((int(348 * s), int(461 * s)))            # bollino: colore campionato dall'originale
    # bollino: cerchio individuato dai pixel rossi dell'originale (centro e raggio reali), cosi' il vecchio testo viene coperto tutto
    x0, y0, x1, y1 = box(260, 430, 440, 590); reg = im.crop((x0, y0, x1, y1)).convert('RGB')
    bb = Image.eval(reg, lambda v: v).point(lambda v: v)  # copia
    px = reg.load(); xs = []; ys = []
    for yy in range(reg.height):
        for xx in range(reg.width):
            q = px[xx, yy]
            if abs(q[0] - rosso[0]) + abs(q[1] - rosso[1]) + abs(q[2] - rosso[2]) < 60: xs.append(xx); ys.append(yy)
    bx = (x0 + min(xs) / 1.0, y0 + min(ys) / 1.0, x0 + max(xs), y0 + max(ys)); bcx = (bx[0] + bx[2]) / 2 / s; bcy = (bx[1] + bx[3]) / 2 / s; br = ((bx[2] - bx[0]) + (bx[3] - bx[1])) / 4 / s - 1
    d.ellipse(box(bcx - br, bcy - br, bcx + br, bcy + br), fill=rosso)
    testo(o['bollino1'], bcx, bcy - 18, 1.55 * br, 32, 'seguibl.ttf', bianco); testo(o['bollino2'], bcx, bcy + 12, 1.5 * br, 15, 'segoeuib.ttf', bianco); testo(o['bollino3'], bcx, bcy + 30, 1.5 * br, 15, 'segoeuib.ttf', bianco)
    barra = im.getpixel((int(12 * s), int(711 * s)))              # barra in basso: colore campionato
    d.rectangle(box(20, 694, 880, 728), fill=barra); testo(o['barra'], 450, 711, 840, 24, 'segoeuib.ttf', bianco)
    return im

def finale(src, dest):
    im = Image.open(src).convert('RGB')
    bb = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 10 else 0).getbbox()
    im = im.crop(bb); k = 900 / max(im.size); im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    c = Image.new('RGB', (1000, 1000), (255, 255, 255)); c.paste(im, ((1000 - im.width) // 2, (1000 - im.height) // 2)); c.save(dest, 'WEBP', quality=90)

def render_planner(p, l, anno=2027):
    """Planner annuale ricostruito 1:1 come l'originale (12 mesi x 31 giorni, 'giorno + iniziale', weekend ombreggiati) con date vere e testi nella lingua."""
    import calendar, datetime
    from PIL import ImageDraw, ImageFont, ImageFilter
    t = p['testi'][l]; W = 2000; FD = r'C:\Windows\Fonts'
    F = lambda n, s: ImageFont.truetype(os.path.join(FD, n), s)
    im = Image.new('RGB', (W, W), (255, 255, 255)); d = ImageDraw.Draw(im)
    def sp(y, s, f, fill=(20, 20, 20), gap=0):  # testo centrato con spaziatura tra lettere
        w = sum(d.textlength(c, font=f) + gap for c in s) - gap; x = (W - w) / 2
        for c in s: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + gap
    sp(120, t['top'], F('segoeuil.ttf', 62), gap=14); sp(250, t['titolo'], F('segoeuisl.ttf', 112), gap=8)
    sx, sy, sw, sh = 80, 470, 1840, 1280
    ombra = Image.new('L', (W, W), 0); ImageDraw.Draw(ombra).rectangle([sx + 14, sy + 22, sx + sw + 14, sy + sh + 22], fill=120)
    ombra = ombra.filter(ImageFilter.GaussianBlur(22)); im.paste(Image.new('RGB', (W, W), (150, 150, 150)), mask=ombra)
    d = ImageDraw.Draw(im); d.rectangle([sx, sy, sx + sw, sy + sh], fill=(255, 255, 255))
    ft = F('segoeuil.ttf', 66); w = d.textlength(t['titolo'], font=ft)
    d.text((sx + (sw - w) / 2, sy + 28), t['titolo'], font=ft, fill=(30, 30, 30))
    gx, gy, lab, ch = sx + 40, sy + 150, 150, 83; cw = (sw - 80 - lab) / 31
    fc, fm = F('segoeuil.ttf', 19), F('segoeuil.ttf', 20); GR = (120, 120, 120)
    for m in range(12):
        y = gy + m * ch; d.rectangle([gx, y, gx + lab, y + ch], outline=GR, width=2)
        d.text((gx + 12, y + ch / 2 - 12), t['mesi'][m], font=fm, fill=(60, 60, 60))
        for g in range(1, calendar.monthrange(anno, m + 1)[1] + 1):
            x = gx + lab + (g - 1) * cw; wd = datetime.date(anno, m + 1, g).weekday()
            if wd >= 5:
                d.rectangle([x, y, x + cw, y + ch], fill=(228, 228, 228))
                for k in range(-int(ch), int(cw), 9): d.line([x + max(k, 0), y + max(-k, 0), x + min(k + ch, cw), y + min(ch, cw - k)], fill=(205, 205, 205), width=1)
            d.rectangle([x, y, x + cw, y + ch], outline=GR, width=2)
            d.text((x + 5, y + 8), str(g) + t['gg'][wd], font=fc, fill=(70, 70, 70))
    sp(1850, t['formati'], F('segoeuil.ttf', 64), gap=4)
    return im.resize((1200, 1200), Image.LANCZOS)

def main(pid, solo=None, push=True):
    p = PRODOTTI[pid]; orig = os.path.join(R, 'automation', 'base', pid + '-orig.jpg'); out = os.path.join(R, 'assets', 'images', 'prodotti')
    for l, (nome, suf) in LINGUE.items():
        if solo and l != solo: continue
        if p.get('overlay'):
            tmp = os.path.join(R, 'automation', 'base', pid + '-' + l + '.png'); render_overlay(p, l, orig).save(tmp)
            finale(tmp, os.path.join(out, pid + suf + '.webp')); print('ok overlay', l); continue
        if p.get('render'):
            render_planner(p, l).save(os.path.join(out, pid + suf + '.webp'), 'WEBP', quality=92); print('ok render', l); continue
        G.PROMPT['digitale'] = prompt(p, l); G.SUFFISSO['digitale'] = '_digitale'
        png = os.path.join(R, 'automation', 'base', pid + '-' + l + '.png')
        r = G.modifica(orig, 'digitale', out=png, forza=True)
        if not r: print('Gemini KO', l); return
        finale(r, os.path.join(out, pid + suf + '.webp')); print('ok', l)
    cp = os.path.join(R, '_data', 'catalogo.json'); raw = open(cp, encoding='utf-8').read(); c = json.loads(raw)
    x = [q for q in c['prodotti'] if q['id'] == pid][0]
    v = int(x.get('immagine', '?v=0').split('?v=')[-1] or 0) + 1
    x['immagine'] = 'assets/images/prodotti/%s.webp?v=%d' % (pid, v)
    x.setdefault('tr', {}).setdefault('en', {})['immagine'] = 'assets/images/prodotti/%s-en.webp?v=%d' % (pid, v)
    open(cp, 'w', encoding='utf-8', newline='\n').write(json.dumps(c, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
    if push:
        g = lambda *a: print(subprocess.run(['git', '-C', R, *a], capture_output=True, text=True, encoding='utf-8').stdout.strip())
        g('add', '_data/catalogo.json', 'assets/images/prodotti', 'automation'); g('commit', '-m', 'Foto %s: originale Etsy, sfondo bianco e testi tradotti IT/EN' % pid)
        g('pull', '--rebase'); g('push'); print('push ok')

if __name__ == '__main__':
    a = sys.argv[1:]; main(a[0], a[a.index('--solo') + 1] if '--solo' in a else None, '--no-push' not in a)
