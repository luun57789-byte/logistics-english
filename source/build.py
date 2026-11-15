import glob
s=open('src.html').read()
import subprocess,sys
subprocess.run([sys.executable,'gen_ipa.py'],check=True)
ipa={}
for l in open('ipa.tsv'):
  a=l.rstrip('\n').split('\t');ipa[a[0]]=a[1:]
lines=[l.rstrip('\n') for f in sorted(glob.glob('vocab/*.txt')) for l in open(f) if l.strip()]
raw="\n".join(l+'|'+'|'.join(ipa[l.split('|')[0]]) for l in lines)
assert "`" not in raw and "${" not in raw
import datetime
stamp=datetime.datetime.utcnow()+datetime.timedelta(hours=7)
open('app.html','w').write(s.replace("__VOCAB__",raw).replace('__BUILD__',stamp.strftime('%d/%m/%Y %H:%M')+' · '+str(len(lines))+' từ, có IPA UK/US'))
print("words",len(raw.split("\n")))
