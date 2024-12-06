import pandas as pd
import json

df = pd.read_excel('Neukunden.xlsx')

# Replace NaN with empty strings
df = df.fillna('')

# Replace all occurrences of '_x000d_' (and possibly the trailing newline) in all string columns
#df = df.replace(r'_x000d_', '', regex=True)

# If you also have \n that you want to handle or if the pattern slightly differs, you can chain replacements:
df = df.replace(r'_x000d_\n', '\n', regex=True)

json_records = df.to_dict(orient='records')

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(json_records, f, ensure_ascii=False, indent=4)
