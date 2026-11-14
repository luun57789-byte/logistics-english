import glob
s=open('src.html').read()
raw="".join(open(f).read().rstrip("\n")+"\n" for f in sorted(glob.glob('vocab/*.txt'))).strip()
assert "`" not in raw and "${" not in raw
open('app.html','w').write(s.replace("__VOCAB__",raw))
print("words",len(raw.split("\n")))
