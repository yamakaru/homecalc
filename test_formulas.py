"""Run each built calculator's JS in node and compare with independent Python math.
Usage: python3 build.py && python3 test_formulas.py"""
import json,math,re,subprocess,sys
C=lambda x:math.ceil(round(x,6))
def run(slug,inp):
    js=re.search(r"<script>(function U.*?)</script>",open(f"dist/{slug}/index.html").read(),re.S).group(1)
    js=js.split("function run()")[0]
    stub="var V=%s;var document={getElementById:function(i){return {value:V[i]}}};"%json.dumps({k:str(v) for k,v in inp.items()})
    out=subprocess.run(["node","-e",stub+js+";console.log(JSON.stringify(c()))"],capture_output=True,text=True,check=True).stdout
    return {r[0]:r[1] for r in json.loads(out)}
def get(r,key): return next(v for k,v in r.items() if k.startswith(key))
T=[]
def case(slug,inp,exp):T.append((slug,inp,exp))
# concrete: 10x10x4 +10%: 33.333*1.1=36.667 cf, 1.358 cy; 80lb 0.6cf ->62
case("concrete-calculator",dict(L=10,W=10,T=4,X=10),{"Cubic yards":"1.36","80 lb":62,"60 lb":82,"40 lb":123})
case("concrete-calculator",dict(L=27,W=1,T=12,X=0),{"Cubic yards":"1.00","80 lb":45,"60 lb":60,"40 lb":90})
case("paint-calculator",dict(P=48,H=8,D=1,N=2,C=2,V=350),{"Paintable":"334","Buy":"2 gallon(s)"})
case("paint-calculator",dict(P=60,H=9,D=2,N=3,C=2,V=400),{"Paintable":"455","Buy":"3 gallon(s)"})
case("mulch-calculator",dict(A=108,T=3),{"Cubic yards":"1.00","2 cu ft":14,"3 cu ft":9})
case("gravel-calculator",dict(L=20,W=10,T=4,R=1.4),{"Cubic yards":"2.47","Tons":"3.46"})
case("tile-calculator",dict(L=12,W=10,A=12,B=12,X=10,S=15),{"Tiles":132,"Boxes":9})
case("tile-calculator",dict(L=10,W=10,A=12,B=24,X=15,S=16),{"Tiles":58,"Boxes":8})
case("drywall-calculator",dict(P=48,H=8,C=144,X=10),{"4×8":19,"4×12":13,"Joint compound":"5.8","4.5 gal":2,"Screws":581})
case("flooring-calculator",dict(L=15,W=12,X=10,S=20),{"Boxes":10})
case("roofing-calculator",dict(A=1500,R=6,X=10,B=3),{"Pitch":"1.118","Squares":"18.45","Bundles":56})
case("roofing-calculator",dict(A=1000,R=12,X=0,B=3),{"Pitch":"1.414","Bundles":43})
case("deck-board-calculator",dict(L=16,W=12,B=5.5,G=0.125,K=16,X=10),{"Rows":26,"Boards":29,"Screws":676})
case("fence-calculator",dict(F=100,S=8,R=3,P=5.5,G=0),{"Sections":13,"Posts":14,"Rails":39,"Pickets":219})
case("insulation-calculator",dict(A=1000,T=38,r=3.2,C=40),{"Required":"11.9","Bags":25})
case("wallpaper-calculator",dict(P=48,H=8,w=20.5,L=33,R=0),{"Strips needed":29,"Strips per roll":4,"Rolls":8})
case("grout-calculator",dict(A=100,L=12,W=12,J=0.125,D=0.375),{"Grout volume":"113"})
case("paver-calculator",dict(A=200,L=8,W=4,X=10,B=4,S=1),{"Pavers":990,"Base":"2.47","Bedding":"0.62"})
case("topsoil-calculator",dict(A=500,T=4,R=1.1,V=0.75),{"Cubic yards":"6.17","Bags":223})
case("sand-calculator",dict(L=10,W=10,T=2,R=1.35),{"Cubic yards":"0.62","Tons":"0.83","50 lb":34})
case("asphalt-calculator",dict(L=50,W=12,T=3,D=145),{"Cubic yards":"5.56","Tons":"10.88"})
case("baseboard-calculator",dict(P=48,D=1,O=3,K=12,X=10),{"Linear":"45.0","Pieces":5})
case("stair-calculator",dict(H=108,M=7.75,T=10),{"Number of risers":14,"Riser":"7.71","Number of treads":13,"Total run":"130.0"})
case("sod-grass-seed-calculator",dict(A=2000,X=5,Q=450,S=8),{"Sod pieces":210,"Sod pallets":5,"Grass seed":"16.0"})
fail=0;import os
for slug in sorted(os.listdir("dist")):
    if slug.endswith("-calculator"):
        f=[t for t in T if t[0]==slug]
        if not f: print("NO TEST",slug);fail+=1
        # edge cases on defaults: zeros, negative, huge
        js_inputs=re.findall(r"<input id='(\w+)'[^>]*value='([^']*)'",open(f"dist/{slug}/index.html").read())
        z=run(slug,{k:0 for k,_ in js_inputs});neg=run(slug,{**{k:v for k,v in js_inputs},js_inputs[0][0]:-5});big=run(slug,{k:1e9 for k,_ in js_inputs});blank=run(slug,{**{k:v for k,v in js_inputs},js_inputs[0][0]:""})
        for nm,r in [("zero",z),("neg",neg),("huge",big),("blank",blank)]:
            if any(re.search("NaN|Infinity|undefined",str(v)) for v in r.values()):print("EDGE FAIL",slug,nm,r);fail+=1
        if "Please" not in str(neg):print("NEG not rejected",slug);fail+=1
for slug,inp,exp in T:
    r=run(slug,inp)
    for k,v in exp.items():
        g=get(r,k)
        if str(g)!=str(v):print("FAIL",slug,inp,k,"got",g,"want",v);fail+=1
print("ALL PASS" if not fail else f"{fail} failures");sys.exit(1 if fail else 0)
