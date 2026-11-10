# -*- coding: utf-8 -*-
r"""MOTORE listino prodotti digitali ORIGINALI (ispirati ai best seller Etsy, mai copie).
    python automation\listino\auto.py [N]      -> pubblica N prodotti (default 5): riprende prima il lotto manuale in sospeso (lotto_orig.json),
                                                   poi prende i prossimi dal LISTINO (ordine = best seller a giro tra le categorie).
Per ogni prodotto, tutto in Python e senza browser Etsy:
  1. bozza testi IT/EN + prompt foto da categoria/formato/anno del titolo (nostri, mai copiati)  [se esiste una voce curata in originali.json vince quella]
  2. prezzo = comune.prezzo.vendita(acquisto Etsy)  (3x tondo)
  3. nuovo_prodotto.py (1 sola immagine Gemini, uguale IT/EN, senza testo) con TIMEOUT e 1 riprova (se Gemini si blocca il processo viene ucciso)
  4. stato.json + LISTINO.md + ULTIMO_LOTTO.md (link IT/EN) + anteprima.png (foto del lotto in un'unica immagine da guardare)
Si ferma dopo 3 errori di fila. Rilanciabile in qualsiasi momento: salta i prodotti gia' 'fatto'.
Per migliorare un testo: aggiungi/modifica la voce in originali.json (vedi originali.py) e rilancia.
Per aggiungere categorie/prodotti: raccogli.py (grezzo.json) e poi di nuovo auto.py."""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, r'C:\Users\mirco\Desktop\libreria_comune')
from comune import prezzo
import genera_md as L
PROD = os.path.join(R, 'automation', 'prodotti'); SP = os.path.join(HERE, 'stato.json')
SITO = 'https://cialdecompatibili-netizen.github.io/prodottidigitali3/'
TIMEOUT = 480  # secondi per prodotto (pagine + 1 foto Gemini)
CAT = {
 'planner': dict(id='planner', it='Planner e agende stampabili', en='Printable planners and agendas', slug_en='planners', icona='\U0001F4C5'),
 'budget': dict(id='budget', it='Budget e finanze', en='Budget and finance', slug_en='budget-finance', icona='\U0001F4B6'),
 'bambini': dict(id='bambini', it='Prodotti digitali per bambini', en='Digital printables for kids', slug_en='games-activities', icona='\U0001F9F8'),
 'pasti': dict(id='pasti', it='Meal planner e cucina', en='Meal planners and kitchen', slug_en='meal-planners', icona='\U0001F37D'),
 'uncinetto': dict(id='uncinetto', it='Schemi uncinetto PDF', en='Crochet patterns PDF', slug_en='crochet-patterns', icona='\U0001F9F6'),
 'cv': dict(id='cv', it='Curriculum e lavoro', en='Resume and career', slug_en='resume-career', icona='\U0001F4C4'),
 'matrimonio': dict(id='matrimonio', it='Matrimonio e inviti', en='Wedding and invitations', slug_en='wedding-invitations', icona='\U0001F48C'),
 'habit': dict(id='habit', it='Habit tracker e routine', en='Habit trackers and routines', slug_en='habit-trackers', icona='\u2705'),
}
# --- BOZZA TESTI (variano per categoria, formato, anno e una variante stabile ricavata dall'ID) ---
BASE = {  # cid: (nome IT, nome EN, descrizione IT, descrizione EN, cosa IT, cosa EN, soggetto digitale, soggetto stampato)
 'planner': ('Planner e agenda', 'Planner and Agenda', 'calendari, pagine settimanali e spazi per gli obiettivi', 'calendars, weekly pages and goal spaces',
             'a clean digital planner with monthly calendar and weekly pages', 'printed planner pages (monthly calendar and weekly spread) with a pen'),
 'budget': ('Budget planner', 'Budget Planner', 'entrate, spese e risparmi sempre sotto controllo', 'income, expenses and savings under control',
            'a budget dashboard with charts and expense tables', 'printed budget planner pages with tables, a calculator and a pen'),
 'habit': ('Habit tracker', 'Habit Tracker', 'abitudini quotidiane, serie di giorni e obiettivi mensili', 'daily habits, streaks and monthly goals',
           'a habit tracker grid with colored check marks', 'printed habit tracker sheets with colored pencils'),
 'matrimonio': ('Set inviti di nozze', 'Wedding Invitation Set', 'invito, RSVP e coordinato per il grande giorno', 'invitation, RSVP and matching stationery for the big day',
                'an elegant wedding invitation design', 'an elegant wedding invitation suite (card, RSVP card, envelope) with leaves'),
 'bambini': ('Giochi e attivita per bambini', 'Printable Kids Activities', 'giochi, enigmi e attivita da fare insieme', 'games, puzzles and activities to enjoy together',
             'a colorful kids activity page', 'printed colorful kids activity pages with crayons and scissors'),
 'pasti': ('Menu settimanale e lista della spesa', 'Weekly Menu and Grocery List', 'pasti della settimana, ricette e spesa organizzati', 'weekly meals, recipes and groceries organized',
           'a weekly meal planner grid with a grocery list', 'a printed weekly meal planner and grocery list with fresh vegetables'),
 'uncinetto': ('Schemi uncinetto', 'Crochet Patterns', 'istruzioni passo passo adatte anche a chi inizia', 'step-by-step instructions suited to beginners',
               'a crochet pattern document next to a finished crochet toy', 'finished handmade crochet toys with yarn balls and a crochet hook'),
 'cv': ('Modello di curriculum', 'Resume Template', 'layout pulito, facile da personalizzare', 'clean layout, easy to customize',
        'a clean modern resume layout', 'two clean modern resume pages with placeholder lines on a desk with a pen'),
}
FMT = [  # (regex titolo, IT, EN, uso IT, uso EN, tipo)
 (r'canva', 'modificabile su Canva', 'Editable on Canva', 'Si modifica su Canva: cambi testi e colori e scarichi i file.', 'Edit it on Canva: change texts and colors and download your files.', 'dig'),
 (r'google sheets|fogli google|google fogli', 'per Google Sheets', 'for Google Sheets', 'Lo copi nel tuo Drive e lo personalizzi come preferisci.', 'Copy it to your Drive and make it your own.', 'dig'),
 (r'excel|spreadsheet|foglio di calcolo', 'in foglio di calcolo', 'Spreadsheet', 'Funziona su Google Sheets ed Excel.', 'Works on Google Sheets and Excel.', 'dig'),
 (r'word|docs|pages', 'per Word e Google Docs', 'for Word and Google Docs', 'Modificabile in Word e Google Docs.', 'Editable in Word and Google Docs.', 'dig'),
]
ADJ = [('essenziale', 'Minimal'), ('colorato', 'Colorful'), ('elegante', 'Elegant')]
SCENA = ['on a white desk, soft natural shadow, bright airy palette', 'on a light wooden table with a small green plant, warm natural light', 'on a pastel linen background, muted palette, soft shadow']
NOTXT = ', no readable text, no letters, no logos'
slug = lambda s: re.sub(r'\W+', '-', s.lower().encode('ascii', 'ignore').decode()).strip('-')

_cf = os.path.join(HERE, 'curati.json')
CUR = json.load(open(_cf, encoding='utf-8')) if os.path.exists(_cf) else {}  # {listing_etsy: {cat, pid, slug_en, it:[nome,desc,full], en:[...], foto}} testi curati a mano: vincono sulla bozza

def bozza(cid, nome, listing, acq):
    o = CUR.get(listing)
    if o:
        c = CAT[o['cat']]; it, en = o['it'], o['en']
        return o['pid'], dict(categoria=c, slug_en=o['slug_en'], prezzo_centesimi=int(prezzo.vendita(acq)) * 100, icona=c['icona'],
            it=dict(nome=it[0], descrizione=it[1], descrizione_completa=it[2]), en=dict(nome=en[0], descrizione=en[1], descrizione_completa=en[2]),
            foto=dict(cosa=en[0], originale=o['foto'], it='', en=''))
    t = nome.lower(); h = int(listing[-3:]) % 3
    b = BASE[cid]; ai, ae = ADJ[h]
    f = next((x for x in FMT if re.search(x[0], t)), None)
    fi, fe, ui, ue, tipo = (f[1], f[2], f[3], f[4], f[5]) if f else ('in PDF stampabile', 'Printable PDF', 'Si stampa a casa in formato A4 o A5.', 'Print it at home on A4 or A5.', 'pdf')
    m = re.search(r'20(2[5-9])', t); anno = (' 20' + m.group(1)) if m else ''
    itn = '%s %s %s%s' % (b[0], ai, fi, anno); enn = '%s %s %s%s' % (ae, b[1], fe, anno)
    it_d = '%s: %s.' % (b[0], b[2]); en_d = '%s: %s.' % (b[1], b[3])
    sogg = ('a laptop and a tablet showing ' + b[4]) if tipo == 'dig' else b[5]
    foto = ('flat lay product mockup of %s %s' % (sogg, SCENA[h])) + NOTXT
    c = CAT[cid]; pid = slug(itn)[:60].strip('-') + '-' + listing[-4:]
    return pid, dict(categoria=c, slug_en=slug(enn)[:60].strip('-') + '-' + listing[-4:], prezzo_centesimi=int(prezzo.vendita(acq)) * 100, icona=c['icona'],
        it=dict(nome=itn, descrizione=it_d, descrizione_completa='%s %s Scarichi subito i file.' % (it_d, ui)),
        en=dict(nome=enn, descrizione=en_d, descrizione_completa='%s %s Download your files instantly.' % (en_d, ue)),
        foto=dict(cosa=enn, originale=foto, it='', en=''), bozza=True)

def leggi_stato(): return json.load(open(SP, encoding='utf-8')) if os.path.exists(SP) else {}
def salva_stato(s): json.dump(s, open(SP, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

def esegui(pid):
    """nuovo_prodotto.py con timeout; se si blocca (Gemini) uccide tutto l'albero di processi. True se push ok."""
    p = subprocess.Popen([sys.executable, os.path.join(R, 'automation', 'nuovo_prodotto.py'), pid], cwd=R, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    try: out = p.communicate(timeout=TIMEOUT)[0] or ''
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], capture_output=True); out = (p.communicate()[0] or '') + '\nTIMEOUT'
    print('==', pid, 'exit', p.returncode); print(out[-300:], flush=True)
    return p.returncode == 0 and 'push ok' in out and 'KO' not in out and 'TIMEOUT' not in out

def lancia(lotto, maxn=10 ** 6):
    """lotto = [[pid, listing], ...]; ritorna i pid pubblicati."""
    fatti, errori = [], 0
    for pid, listing in lotto:
        if len(fatti) >= maxn: break
        if leggi_stato().get(listing, {}).get('stato') == 'fatto': continue
        ok = esegui(pid) or esegui(pid)
        st = leggi_stato(); st[listing] = dict(stato='fatto' if ok else 'errore', id=pid); salva_stato(st)
        if ok: fatti.append(pid); errori = 0
        else:
            errori += 1
            if errori >= 3: print('STOP: 3 errori di fila (Gemini bloccato o senza crediti?). Rilancia piu\' tardi.'); break
    return fatti

def anteprima(pids):
    try:
        from PIL import Image
        ims = [Image.open(os.path.join(R, 'assets', 'images', 'prodotti', p + '.webp')).convert('RGB').resize((300, 300)) for p in pids]
        cols = min(4, len(ims)); righe = (len(ims) + cols - 1) // cols
        S = Image.new('RGB', (cols * 300, righe * 300), 'white')
        for i, im in enumerate(ims): S.paste(im, ((i % cols) * 300, (i // cols) * 300))
        out = os.path.join(HERE, 'anteprima.png'); S.save(out); return out
    except Exception as e: print('anteprima KO', e)

def main(n, forza=None):
    fatti = []
    pend = os.path.join(HERE, 'lotto_orig.json')
    if os.path.exists(pend) and not forza: fatti += lancia(json.load(open(pend)), n)       # 1) lotto manuale in sospeso (testi curati in originali.json)
    if len(fatti) < n:                                                       # 2) prossimi dal listino (bozze automatiche)
        st = leggi_stato(); cand = []
        for cid, pos, p in L.ordine:
            i = L.lid(p['link'])
            if forza and i != forza: continue
            if i in L.visti or st.get(i, {}).get('stato') in ('fatto', 'saltato') or cid not in BASE: continue
            m = re.search(r'[\d.,]+', p.get('prezzo') or '')
            if not m: continue
            acq = float(m.group().replace('.', '').replace(',', '.'))
            pid, d = bozza(cid, p['nome'], i, acq)
            pf = os.path.join(PROD, pid + '.json')
            if not os.path.exists(pf): json.dump(d, open(pf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            cand.append([pid, i])
            if len(cand) >= (n - len(fatti)) + 3: break
        fatti += lancia(cand, n - len(fatti))
    subprocess.run([sys.executable, os.path.join(HERE, 'genera_md.py')], cwd=R, capture_output=True)
    righe = ['# Ultimo lotto (%s)' % time.strftime('%d/%m/%Y %H:%M'), ''] + ['- %s\n  - IT %snegozio/%s/' % (p, SITO, p) for p in fatti]
    open(os.path.join(HERE, 'ULTIMO_LOTTO.md'), 'w', encoding='utf-8').write('\n'.join(righe))
    if fatti: print('anteprima:', anteprima(fatti))
    subprocess.run(['git', 'add', 'automation'], cwd=R, capture_output=True); subprocess.run(['git', 'commit', '-m', 'Listino: stato lotto e LISTINO.md'], cwd=R, capture_output=True); subprocess.run(['git', 'push'], cwd=R, capture_output=True)
    print('PUBBLICATI %d:' % len(fatti)); [print(' ', SITO + 'negozio/' + p + '/') for p in fatti]

if __name__ == '__main__':
    # python auto.py [N]   |   python auto.py --listing <id_etsy>  (un prodotto preciso del listino, usa curati.json se c'e' la voce)
    if '--listing' in sys.argv: main(1, sys.argv[sys.argv.index('--listing') + 1])
    else: main(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5)
