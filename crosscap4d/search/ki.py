import csv, os, database_knotinfo, ast, snappy
p=os.path.dirname(database_knotinfo.__file__)+'/csv_data/'
ROWS={r['name']:r for r in list(csv.DictReader(open(p+'knotinfo_data_complete.csv',encoding='utf-8',errors='replace'),delimiter='|'))[1:]}
def link(name):
    return snappy.Link(ast.literal_eval(ROWS[name]['pd_notation']))
def circles(L,st):
    parent={}
    def f(x):
        while parent.setdefault(x,x)!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def u(a,b): parent[f(a)]=f(b)
    for (a,b,c,d) in L.PD_code():
        for x in (a,b,c,d): f(x)
        if st=='A': u(a,b);u(c,d)
        else: u(a,d);u(b,c)
    return len({f(x) for x in parent})
def turaev(L): return (2+len(L.crossings)-circles(L,'A')-circles(L,'B'))//2
