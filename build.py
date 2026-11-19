# Inlines skills.js into app.html -> index.html. Run after editing either file, and bump VERSION in sw.js.
h=open('app.html').read();open('index.html','w').write(h.replace('/*__SKILLS__*/',open('skills.js').read()))
