import csv
from pathlib import Path
p=Path('data/processed/Ames_Housing_Data.csv')
print('exists', p.exists(), 'size', p.stat().st_size if p.exists() else None)
with p.open('r', encoding='utf-8', errors='replace') as f:
    lines=[]
    for _ in range(10):
        try:
            lines.append(next(f))
        except StopIteration:
            break
print('--- RAW LINES ---')
for i,l in enumerate(lines):
    print(i+1, l.strip()[:200])
sample='\n'.join(lines)
try:
    dialect=csv.Sniffer().sniff(sample)
    print('detected delimiter:', repr(dialect.delimiter))
except Exception as e:
    print('sniffer failed:', e)
try:
    delim = dialect.delimiter
except:
    delim=','
print('Parsing with delimiter:', repr(delim))
reader=csv.reader(sample.splitlines(), delimiter=delim)
for i,row in enumerate(reader):
    print('row', i+1, len(row), row[:6])
    if i>=5:
        break
