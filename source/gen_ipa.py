# Generates ipa.tsv (term \t UK IPA \t US IPA) for every vocab term using espeak-ng (pip: phonemizer espeakng-loader).
import glob,re,os
import espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path())
os.environ['ESPEAK_DATA_PATH']=espeakng_loader.get_data_path()
from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
WORDISH={'FIFO','FEFO','ISO','ECUS','REX','Incoterms','NVOCC'}
NUM={'20':'twenty','40':'forty','3':'three','5':'five','24':'twenty four','11':'eleven'}
LET_UK={'A':'eɪ','B':'biː','C':'siː','D':'diː','E':'iː','F':'ɛf','G':'dʒiː','H':'eɪtʃ','I':'aɪ','J':'dʒeɪ','K':'keɪ','L':'ɛl','M':'ɛm','N':'ɛn','O':'əʊ','P':'piː','Q':'kjuː','R':'ɑː','S':'ɛs','T':'tiː','U':'juː','V':'viː','W':'dʌbəljuː','X':'ɛks','Y':'waɪ','Z':'zɛd'}
LET_US=dict(LET_UK,O='oʊ',R='ɑːr',Z='ziː')
def letters(acr,us):
  L=LET_US if us else LET_UK
  names=[L[c] for c in acr]
  if len(names)==1: return 'ˈ'+names[0]
  return 'ˌ'+' '.join(names[:-1])+' ˈ'+names[-1]
def runs(term):
  """Return list of alternatives; each is a list of ('w',text) / ('a',LETTERS) runs."""
  t=re.sub(r'\s*\(.*?\)','',term).strip()
  alts=[]
  for p in re.split(r'\s+/\s+',t):
    p=re.sub(r'(?<=\w)/(?=\w)',' ',p)
    p=re.sub(r'(\d+)(?=[A-Za-z])',lambda m:NUM.get(m.group(1),m.group(1))+' ',p)
    p=p.replace('-',' ')
    rs=[]
    for w in p.split():
      core=w.strip(',.')
      if core in WORDISH and core!='NVOCC': word=core.lower() if core!='Incoterms' else core; rs.append(('w',word)); continue
      m=re.fullmatch(r'([A-Z]{2,6})(s?)',core)
      if core=='NVOCC' or m or core=='cc' or (len(core)==1 and core.isalpha() and core not in ('A','I','a')):
        acr='NVOCC' if core=='NVOCC' else (m.group(1) if m else core.upper())
        rs.append(('a',acr+('§S' if m and m.group(2) else ''))); continue
      if core=='x': rs.append(('w','by')); continue
      rs.append(('w',core))
    # merge consecutive word runs
    merged=[]
    for k,v in rs:
      if merged and k=='w' and merged[-1][0]=='w': merged[-1]=('w',merged[-1][1]+' '+v)
      elif merged and k=='a' and merged[-1][0]=='a' and '§' not in merged[-1][1] and '§' not in v: merged[-1]=('a',merged[-1][1]+v)
      else: merged.append((k,v))
    alts.append(merged)
  return alts
VOW=set('aeiouæɑɒɔəɛɜɪʊʌɐᵻɚɝiy')
ONSET2={'pl','pr','bl','br','tr','dr','kl','kr','gl','gr','fl','fr','θr','ʃr','sp','st','sk','sm','sn','sl','sw','tw','kw','dw','pj','bj','tj','dj','kj','mj','nj','fj','vj','hj','lj','sj'}
ONSET3={'spr','str','skr','spl','skw','stj','spj','skj'}
def tidy(ipa):
  ipa=ipa.replace('ɹ','r').replace('ᵻ','ɪ').replace('ɾ','t').replace('ɚ','ər').replace('ɐ','ə').replace('ɬ','l').replace('ʔ','t')
  ipa=ipa.replace('ˌ','§').replace('ˈ','¶')
  out=[]
  for word in ipa.split(' '):
    w=list(word)
    i=0
    while i<len(w):
      if w[i] in '§¶':
        mark=w.pop(i)
        # collect consonants immediately to the left
        j=i
        cons=[]
        while j>0 and w[j-1] not in VOW and w[j-1] not in 'ː§¶' :
          j-=1; cons.insert(0,w[j])
        s=''.join(cons)
        # treat dʒ/tʃ as single unit
        take=0
        if s.endswith('dʒ') or s.endswith('tʃ'): take=2
        elif len(s)>=3 and s[-3:] in ONSET3: take=3
        elif len(s)>=2 and s[-2:] in ONSET2: take=2
        elif len(s)>=1: take=1
        if j==0 and len(cons)==len(s): take=len(s)  # word-initial: whole cluster
        w.insert(i-take,mark); i+=1
      i+=1
    out.append(''.join(w))
  r=' '.join(out).replace('§','ˌ').replace('¶','ˈ')
  r=r.replace('ˈwɪtθ','ˈwɪdθ').replace('rr','r')
  return r
def accent(x,us):
  x=re.sub(r'r([ˈˌ])r',r'\1r',x)
  if us:
    x=re.sub(r'ɜː(?!r)','ɜːr',x)
  else:
    x=re.sub(r'a(?![ɪʊ])','æ',x)
    x=re.sub(r'r(?=\s|$)','',x)
  return x
def main():
  terms=[]
  for f in sorted(glob.glob('vocab/*.txt')):
    for l in open(f):
      if l.strip(): terms.append(l.split('|')[0])
  old={}
  if os.path.exists('ipa.tsv'):
    for l in open('ipa.tsv'):
      a=l.rstrip('\n').split('\t')
      if len(a)==3: old[a[0]]=a[1:]
  todo=[t for t in terms if t not in old]
  if todo:
    backs={l:EspeakBackend(l,with_stress=True,language_switch='remove-flags') for l in ('en-gb','en-us')}
    texts=sorted({v for t in todo for alt in runs(t) for k,v in alt if k=='w'})
    ph={}
    for l,b in backs.items():
      out=b.phonemize(texts,strip=True,separator=Separator(word=' ',phone=''))
      ph[l]=dict(zip(texts,out))
    for t in todo:
      row=[]
      for l in ('en-gb','en-us'):
        us=l=='en-us';alts=[]
        for alt in runs(t):
          bits=[]
          for k,v in alt:
            if k=='w': bits.append(accent(tidy(ph[l][v]),us))
            else:
              acr,_,plural=v.partition('§');bits.append(letters(acr,us)+('z' if plural else ''))
          alts.append('/'+' '.join(bits)+'/')
        row.append(', '.join(alts))
      old[t]=row
  with open('ipa.tsv','w') as f:
    for t in terms: f.write(t+'\t'+old[t][0]+'\t'+old[t][1]+'\n')
  print('ipa',len(terms),'new',len(todo))
if __name__=='__main__': main()
