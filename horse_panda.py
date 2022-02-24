import pandas as pd
df = pd.read_csv('eggs.csv')
print(df.groupby(['Class']))
