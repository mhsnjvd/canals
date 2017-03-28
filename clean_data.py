import pandas as pd
print('Pandas version: ' + pd.__version__)

df = pd.read_csv('hakra_data.csv')
df = df.dropna()
dates = pd.to_datetime(df['DateOfRecord'], infer_datetime_format=True)
df.index = dates
df = df[df.columns[[2, 8]]]

# Write selected data to a new file
#df.to_csv('hakra_simple.csv')
print('Script finished')
