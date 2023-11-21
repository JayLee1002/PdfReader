
import sys
import os
sys.path.append(r"F:\Documents\资料\year4-1\master\PdfReader")

from source.retrieval.similar_model import SimilarModel

os.system("nvidia-smi")
sm = SimilarModel(r"F:\Documents\资料\year4-1\master\PdfReader\source\retrieval\sbert")
sm.model = sm.model.cuda()
os.system("nvidia-smi")

ret = sm.crawler("attention is all you need")
print(ret)