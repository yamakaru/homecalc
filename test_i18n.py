"""Every language version must compute exactly the same numbers as the verified English calculator.
Runs all English test cases + edge cases on each /<lang>/ page and compares values row by row."""
import os,re,json,subprocess,sys
exec(open("test_formulas.py").read().split("fail=0")[0])
LANGS=[d for d in sorted(os.listdir("dist")) if re.fullmatch(r"[a-z]{2}",d)]
def runp(path,inp):
    h=open(f"dist/{path}/index.html").read()
    js=re.search(r"<script>(function U.*?)</script>",h,re.S).group(1).split("function run()")[0]
    stub="var V=%s;var document={getElementById:function(i){return {value:V[i]}}};"%json.dumps({k:str(v) for k,v in inp.items()})
    return json.loads(subprocess.run(["node","-e",stub+js+";console.log(JSON.stringify(c()))"],capture_output=True,text=True,check=True).stdout)
fail=0;n=0
slugs=sorted(s for s in os.listdir("dist") if s.endswith("-calculator"))
for L in LANGS:
    for slug in slugs:
        h=open(f"dist/{L}/{slug}/index.html").read()
        ids=re.findall(r'<input[^>]*id="(\w+)"[^>]*value="([^"]*)"',h) or re.findall(r"<input id='(\w+)'[^>]*value='([^']*)'",h)
        eids=re.findall(r"<input id='(\w+)'[^>]*value='([^']*)'",open(f"dist/{slug}/index.html").read())
        if sorted(ids)!=sorted(eids):print("INPUTS DIFFER",L,slug,ids,eids);fail+=1
        cases=[t[1] for t in T if t[0]==slug]+[dict(eids),{k:0 for k,_ in eids},{k:1e9 for k,_ in eids},{**dict(eids),eids[0][0]:-5},{**dict(eids),eids[0][0]:""}]
        for inp in cases:
            e=runp(slug,inp);l=runp(f"{L}/{slug}",inp);n+=1
            num=lambda r:[re.sub(r"[^\d.,—-]","",str(x[1])) if re.search(r"\d",str(x[1])) else ("TXT" if re.search(r"[^\W\d_]",str(x[1])) else str(x[1])) for x in r]
            if num(e)!=num(l) or len(e)!=len(l):print("MISMATCH",L,slug,inp,e,l);fail+=1
            if any(not str(x[0]).strip() for x in l):print("EMPTY LABEL",L,slug);fail+=1
print(f"{len(LANGS)} languages, {n} comparisons:","ALL PASS" if not fail else f"{fail} failures");sys.exit(1 if fail else 0)
