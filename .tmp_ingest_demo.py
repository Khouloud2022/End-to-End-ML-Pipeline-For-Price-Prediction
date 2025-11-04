import traceback
from src.ingest_data import ZipDataIngestor

p = 'data/raw/archive.zip'
print('ingesting', p)
try:
	ing = ZipDataIngestor()
	df = ing.ingest(p)
	print('shape:', df.shape)
	print(df.head().to_string())
except Exception:
	print('ingest failed:')
	traceback.print_exc()
