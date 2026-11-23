"""Generate FHCP report tables and figures from accepted experiment records."""
from pathlib import Path
import csv, json, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/latex';DATA=ROOT/'experiments/results/team-evaluation-consolidated-20261117'
def csvrows(name):return list(csv.DictReader((DATA/name).open(encoding='utf-8')))
def tex(s):
 return str(s).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def num(n):return f'{int(n):,}'.replace(',',r'\,')
def save(name,body): (OUT/'tables'/name).write_text(body+'\n',encoding='utf-8')
def table(headers,rows,widths):
 return r'\begin{tabularx}{\linewidth}{'+widths+'}\n'+r'\toprule'+'\n'+' & '.join(headers)+r' \\ \midrule'+'\n'+'\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n'+r'\bottomrule\end{tabularx}'
for name in ('tables','figures'): (OUT/name).mkdir(parents=True,exist_ok=True)
summary=json.loads((DATA/'totals.json').read_text());graphs=csvrows('by-graph.csv');algs=csvrows('by-algorithm.csv');attempts=csvrows('attempts.csv');members=csvrows('by-member.csv')
assert len(attempts)==summary['attempted'] and sum(r['certified_success']=='True' for r in attempts)==summary['successes']
complete=[r for r in algs if r['member']=='ALL' and r['scope']=='complete_graphs_only'];assert all(int(r['attempted'])==summary['coverage']['complete']*10 for r in complete)
labels={'Arturo2430':'Arturo','ZapataFrame':'Zapata','cesar-upv':'César','KirbyStone69':'Eder','ELIASDEJESUSZUNIGADELEON':'Elías'}
macros={'TotalAttempts':num(summary['attempted']),'TotalSuccesses':num(summary['successes']),'SolvedGraphs':summary['solved_graphs'],'TotalErrors':summary['errors'],'TotalExhausted':num(summary['exhausted']),'PendingAttempts':num(summary['pending']),'SuccessRate':f"{100*summary['success_rate_attempted']:.2f}",'CompleteGraphs':summary['coverage']['complete'],'StartedGraphs':summary['coverage']['complete']+summary['coverage']['partial'], 'PartialGraphs':summary['coverage']['partial'], 'UnstartedGraphs':summary['coverage']['not_started'], 'AttemptsPerFamily':num(summary['coverage']['complete']*10)}
save('metrics.tex','\n'.join('\\newcommand{\\'+k+'}{'+str(v)+'}' for k,v in macros.items()))
save('algorithms.tex',table(['Familia','Éxitos/intentos','Tasa (\\%)','Grafos HC','Media (s)','Incid.'],[[r['algorithm'].upper(),f"{r['successes']}/{r['attempted']}",f"{100*float(r['success_rate_attempted']):.2f}",r['solved_graphs'],f"{float(r['mean_process_seconds']):.3f}",r['errors']] for r in complete],'lYrrrr'))
save('members.tex',table(['Equipo','Intentos','Completos','Parciales','HC','Éxitos'],[[labels[r['member']],num(r['attempted']),r['complete_graphs'],r['partial_graphs'],r['solved_graphs'],r['successes']] for r in members],'Yrrrrr'))
solved=[r for r in graphs if int(r['solved_graphs'])];assert len(solved)==summary['solved_graphs']
save('solved.tex',table(['Grafo','Vértices','Aristas','Éxitos/60','Equipo'],[[r['instance'].replace('graph',''),num(r['vertices']),num(r['edges']),f"{r['successes']}/60",labels[r['member']]] for r in solved],'lrrrY'))
partial=[r for r in graphs if r['coverage']=='partial']
save('partial.tex',table(['Grafo','Equipo','Intentos','Pendientes','Incidencias'],[[r['instance'].replace('graph',''),labels[r['member']],r['attempted'],r['pending'],r['errors']] for r in partial],'lYrrr'))
plan=json.loads((ROOT/'experiments/configs/distributed-fhcp-10x60.json').read_text())
rows=[]
for solver in plan['solvers']:
 text='; '.join(tex(k)+'='+tex(v) for k,v in solver['parameters'].items());rows.append([solver['algorithm'].upper(),r'\ttfamily\footnotesize '+text])
save('parameters.tex',table(['Familia','Parámetros efectivos'],rows,'lY'))
bygraph=r'\small\begin{longtable}{llrrrrr}'+'\n'+r'\caption{Cobertura de cada grafo iniciado. Los pendientes no son fallos.}\label{tab:allgraphs}\\'+'\n'+r'\toprule Grafo & Equipo & $n$ & Intentos & Éxitos & Incid. & Pend. \\ \midrule\endfirsthead'+'\n'+r'\toprule Grafo & Equipo & $n$ & Intentos & Éxitos & Incid. & Pend. \\ \midrule\endhead'+'\n'+r'\midrule\multicolumn{7}{r}{Continúa en la página siguiente}\endfoot\bottomrule\endlastfoot'+'\n'
for r in graphs:
 if int(r['attempted']):bygraph+=' & '.join([r['instance'].replace('graph',''),labels[r['member']],num(r['vertices']),r['attempted'],r['successes'],r['errors'],r['pending']])+r' \\'+'\n'
save('all-graphs.tex',bygraph+r'\end{longtable}')
# Historical evaluation/scale: medians by family and instance; retain original budgets.
old=list(csv.DictReader((ROOT/'docs/research/evidence/m6/campaign-cells.csv').open()));final=[r for r in old if r['phase'] in ('evaluation','scale')]
assert sum(int(r['expected_primary']) for r in final)==900
save('historical.tex',table(['Familia','Éxitos/150','Plazos','Eval. límite','Sin candidato'],[[a.upper(),'0/150',sum(int(r['cooperative_timeouts']) for r in final if r['algorithm']==a),150-sum(int(r['cooperative_timeouts']) for r in final if r['algorithm']==a),sum(int(r['without_candidate_primary']) for r in final if r['algorithm']==a)] for a in ['ga','sa','as','abc','de','pso']],'Yrrrr'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#25343B','text.color':'#25343B','axes.titleweight':'bold','svg.hashsalt':'fhcp-report'})
colors=['#164F46','#367B70','#78A69A','#D8AD48','#8C5363','#52655D'];names=[r['algorithm'].upper() for r in complete]
fig,axs=plt.subplots(1,2,figsize=(10.3,3.6),layout='constrained')
rates=[100*float(r['success_rate_attempted']) for r in complete];means=[float(r['mean_process_seconds']) for r in complete]
for ax,values,ylabel in [(axs[0],rates,'Éxitos certificados / intentos (%)'),(axs[1],means,'Media de tiempo de proceso (s)')]:
 bars=ax.bar(names,values,color=colors,width=.65);ax.set_ylabel(ylabel);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
 for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+.02*max(values),f'{value:.2f}',ha='center',fontsize=9)
 ax.set_ylim(0,max(values)*1.18)
axs[0].set_title('Éxito por familia');axs[1].set_title('Tiempo con procesos censurados')
fig.savefig(OUT/'figures/performance.pdf',metadata={'CreationDate':None});plt.close(fig)
# Seed success on certified graphs: no extrapolation to the challenge.
mat=np.zeros((len(solved),6));algidx={a:i for i,a in enumerate(['ga','sa','as','abc','de','pso'])};gidx={r['instance']:i for i,r in enumerate(solved)}
for r in attempts:
 if r['instance'] in gidx and r['certified_success']=='True':mat[gidx[r['instance']],algidx[r['algorithm']]]+=1
fig,ax=plt.subplots(figsize=(7.6,5.4),layout='constrained');im=ax.imshow(mat,cmap='YlGn',vmin=0,vmax=10,aspect='auto');ax.set_xticks(range(6),names);ax.set_yticks(range(len(solved)),[r['instance'] for r in solved]);ax.set_title('Éxitos certificados de diez semillas por familia')
for (i,j),v in np.ndenumerate(mat):ax.text(j,i,str(int(v)),ha='center',va='center',color='white' if v>6 else '#25343B',fontsize=9)
fig.colorbar(im,ax=ax,label='Intentos con ciclo certificado',shrink=.8);fig.savefig(OUT/'figures/success-heatmap.pdf',metadata={'CreationDate':None});plt.close(fig)
fig,ax=plt.subplots(figsize=(8.6,3.7),layout='constrained')
for certified,color,label in [(False,'#52655D','Sin ciclo certificado'),(True,'#367B70','Con ciclo certificado')]:
 selected=[r for r in graphs if int(r['attempted']) and bool(int(r['solved_graphs']))==certified];ax.scatter([int(r['vertices']) for r in selected],[float(r['best_cost'])/int(r['vertices']) for r in selected],c=color,label=label,alpha=.8,s=27)
ax.set_xscale('log');ax.set_xlabel('Número de vértices (escala logarítmica)');ax.set_ylabel('Menor costo / número de vértices');ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=9);ax.set_title('Mejor candidato observado por grafo iniciado')
fig.savefig(OUT/'figures/normalized-cost.pdf',metadata={'CreationDate':None});plt.close(fig)
# Distributions use complete graphs and retain execution mode and missing values.
mode_rows=csvrows('execution-modes.csv')
mode_by_key={(r['member'],r['instance'],r['algorithm'],r['seed']):r['execution_mode'] for r in mode_rows}
assert len(mode_by_key)==len(attempts)
complete_ids={r['instance'] for r in graphs if r['coverage']=='complete'}
box_rows=[r for r in attempts if r['instance'] in complete_ids]
for r in box_rows:
 r['execution_mode']=mode_by_key[(r['member'],r['instance'],r['algorithm'],r['seed'])]
size_by_graph={r['instance']:int(r['vertices']) for r in graphs}
box_stats=[]
def draw_boxes(ax, mode, field, success_only=False):
 groups=[]; counts=[]
 for algorithm in ['ga','sa','as','abc','de','pso']:
  selected=[r for r in box_rows if r['algorithm']==algorithm and r['execution_mode']==mode and (not success_only or r['certified_success']=='True') and r[field] not in ('','None')]
  values=np.asarray([float(r[field])/(size_by_graph[r['instance']] if field=='best_cost' else 1) for r in selected])
  count=len(values);counts.append(count)
  if count:
   q1,median,q3=np.percentile(values,[25,50,75]);iqr=q3-q1
   lower=float(min(values[values>=q1-1.5*iqr]));upper=float(max(values[values<=q3+1.5*iqr]))
   fliers=values[(values<lower)|(values>upper)].tolist()
  else:q1=median=q3=lower=upper=float('nan');fliers=[]
  groups.append(dict(q1=q1,med=median,q3=q3,whislo=lower,whishi=upper,fliers=fliers))
  box_stats.append(dict(metric='cost_per_vertex' if field=='best_cost' else 'process_seconds',execution_mode=mode,scope='certified_successes' if success_only else 'all_available',algorithm=algorithm,n=count,q1=float(q1) if count else None,median=float(median) if count else None,q3=float(q3) if count else None,lower_whisker=lower if count else None,upper_whisker=upper if count else None,outliers=len(fliers)))
 artists=ax.bxp(groups,patch_artist=True,showfliers=True,medianprops={'color':'#123D3B','linewidth':1.6},flierprops={'marker':'.','markersize':3,'alpha':.3,'markeredgecolor':'#52655D'})
 for box,color in zip(artists['boxes'],colors):box.set_facecolor(color);box.set_alpha(.55)
 ax.set_xticks(range(1,7),[f'{a}\nn={n}' for a,n in zip(names,counts)])
 # Empty groups remain empty rather than being represented as zero time.
 for i,count in enumerate(counts,1):
  if not count:ax.text(i,.08,'Sin datos',transform=ax.get_xaxis_transform(),ha='center',fontsize=8,rotation=90)
 ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
 return counts
fig,axs=plt.subplots(2,2,figsize=(10.3,7.5),layout='constrained')
for column,(mode,title) in enumerate([('serial','Ejecución serial'),('parallel_up_to_4','Ejecución paralela')]):
 for row,success_only in enumerate([False,True]):
  draw_boxes(axs[row,column],mode,'process_seconds',success_only)
  axs[row,column].set_title(title+(' · todos los intentos' if not success_only else ' · éxitos certificados'),fontsize=10)
  axs[row,column].set_ylabel('Tiempo de proceso (s)');axs[row,column].set_ylim(bottom=0)
fig.savefig(OUT/'figures/runtime-boxplots.pdf',metadata={'CreationDate':None});plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10.3,3.9),layout='constrained')
for ax,(mode,title) in zip(axs,[('serial','Ejecución serial'),('parallel_up_to_4','Ejecución paralela')]):
 draw_boxes(ax,mode,'best_cost');ax.set_title(title);ax.set_ylabel('Costo final / número de vértices');ax.set_ylim(bottom=-.003)
fig.savefig(OUT/'figures/cost-boxplots.pdf',metadata={'CreationDate':None});plt.close(fig)
with (OUT/'tables/boxplot-statistics.csv').open('w',newline='') as stream:
 writer=csv.DictWriter(stream,fieldnames=list(box_stats[0]));writer.writeheader();writer.writerows(box_stats)
inputs=[DATA/n for n in ['totals.json','by-algorithm.csv','by-graph.csv','by-member.csv','attempts.csv','execution-modes.csv']]+[ROOT/'docs/research/evidence/m6/campaign-cells.csv',ROOT/'experiments/configs/distributed-fhcp-10x60.json']
(OUT/'asset-manifest.json').write_text(json.dumps({'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'outputs':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for directory in ['tables','figures'] for p in sorted((OUT/directory).glob('*')) if p.name!='.gitkeep'}},indent=2)+'\n')
print(f"Report assets: {summary['solved_graphs']} certified graphs; {summary['attempted']} attempts; {summary['coverage']['complete']} complete graphs; historical 900 primary attempts.")
from build_exploratory_report_assets import build as build_closed_explorations
build_closed_explorations()
