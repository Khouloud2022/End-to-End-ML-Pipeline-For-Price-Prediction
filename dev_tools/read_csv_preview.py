import pandas as pd
from pathlib import Path

p=Path('data/processed/Ames_Housing_Data.csv')
print('reading',p)
df=pd.read_csv(p)
print('shape', df.shape)
print('columns:', df.columns[:10].tolist())
print(df.head(2).to_string())
