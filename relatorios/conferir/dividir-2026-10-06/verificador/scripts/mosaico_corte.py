"""Verificador 2.1: mosaico das folhas, recortado em volta do corte (azul = programa, vermelho = ScanTailor)."""
import json, cv2, numpy as np, sys
sys.path.insert(0,"trabalho/novo")
from core.pdf_io import abrir_pdf, pagina_para_array
livro, varre, nome, folhas = sys.argv[1], sys.argv[2], sys.argv[3], [int(v) for v in sys.argv[4].split(",")]
d={x["folha"]:x for x in json.load(open(varre))}
doc=abrir_pdf(livro); ims=[]
for f in folhas:
    x=d[f]; img=pagina_para_array(doc,f-1,dpi=150).copy(); h,w=img.shape[:2]
    xp=int(round(x["programa"]["pos"]*w)); xs=int(round(x["scantailor"]["pos"]*w))
    cv2.line(img,(xp,0),(xp,h),(255,0,0),2); cv2.line(img,(xs,0),(xs,h),(0,0,255),2)
    m=(xp+xs)//2; c=img[int(h*.25):int(h*.6), max(0,m-140):m+140]
    c=cv2.resize(c,(int(c.shape[1]*420/c.shape[0]),420))
    c=cv2.copyMakeBorder(c,22,0,0,6,cv2.BORDER_CONSTANT,value=(255,255,255)); cv2.putText(c,str(f),(3,16),0,0.5,(0,0,0),1)
    ims.append(c)
cv2.imwrite(nome,np.hstack(ims))
