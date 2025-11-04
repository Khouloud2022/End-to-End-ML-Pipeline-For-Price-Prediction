from pathlib import Path
import pandas as pd

src = Path('data/processed/Ames_Housing_Data.tsv')
dst = Path('data/processed/Ames_Housing_Data.csv')

if not src.exists():
    print('Source TSV not found:', src)
else:
    print('Reading', src)
    df = pd.read_csv(src, sep='\t', encoding='utf-8', low_memory=False)
    print('Rows, cols:', df.shape)
    df.to_csv(dst, index=False)
    print('Wrote CSV to', dst)
