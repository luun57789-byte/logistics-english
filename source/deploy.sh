#!/bin/bash
# Rebuild everything and push web version + project copy. Usage: ./deploy.sh "commit message"
set -e
cd /home/user/upd
python3 build.py 2>&1 | grep words
python3 -c "import re;s=open('app.html').read();open('/tmp/claude-0/chk.js','w').write('\n'.join(re.findall(r'<script>(.*?)</script>',s,re.S)))"
node --check /tmp/claude-0/chk.js
python3 make_pdf.py | tail -1
python3 make_standalone.py | tail -1
cp app.html tu-vung-logistics.pdf /home/user/logistics-english/
cd /home/user/le-repo && git pull -q origin main
cp /home/user/upd/dist/* /home/user/upd/dist/.nojekyll .
cp /home/user/upd/{build.py,gen_ipa.py,ipa.tsv,make_pdf.py,make_standalone.py,src.html,deploy.sh} source/
cp /home/user/upd/vocab/*.txt source/vocab/
git add -A
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01QqNgYpKLVkBJALKZ4yeMWJ"
git -c push.negotiate=true push -q origin main
D=/mnt/project-files/logistics-english; cd /home/user/upd
cp build.py gen_ipa.py ipa.tsv make_pdf.py make_standalone.py src.html app.html tu-vung-logistics.pdf deploy.sh $D/
mkdir -p $D/vocab $D/web && cp vocab/*.txt $D/vocab/ && rm -rf $D/web/* && cp -r dist/. $D/web/
(cd dist && rm -f $D/logistics-english-app.zip && zip -qr $D/logistics-english-app.zip .)
echo DEPLOYED
