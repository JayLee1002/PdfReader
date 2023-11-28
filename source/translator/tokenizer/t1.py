import sentencepiece as spm

model_path = r'eng.model'
sp_chn = spm.SentencePieceProcessor()
sp_chn.Load(model_path)
