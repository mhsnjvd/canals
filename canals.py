import matplotlib.pylab as plt
import numpy as np
import pandas as pd
print('Pandas version: ' + pd.__version__)
print('Numpy version: ' + np.__version__)
df = pd.read_csv('hakra_simple.csv')
df.index = pd.to_datetime(df['DateOfRecord'], infer_datetime_format=True)
df = df.drop('DateOfRecord', 1)
df.columns = ['name', 'discharge']
design_discharge = {
                'HR': 510,
                'HL': 23.06,
                '4R': 226,
                '1L': 83.48,
                'BS': 6,
                '1R': 19,
                '2R': 22,
                '3R': 353,
                '5R': 36.49,
                '2L': 19.11,
                '7R': 273,
                '3L': 9.68,
                '4L': 9.01,
                '8R': 31,
                'FC': 93,
                '6R': 546,
                '9R': 240
}
distributory_names = [key for key in design_discharge.keys()]
priorities = {
    'A': {'A1': ['HR', 'HL'], 'A2': ['4R', '1L']},
    'B': {'B1': ['BS', '1R', '2R', '3R'], 'B2': ['5R', '2L', '7R', '3L', '4L', '8R', 'FC']},
    'C': {'C1': ['6R'], 'C2': ['9R']}
    }

sf = pd.read_csv('schedule.csv')
# Khareef season start date\n",
start_date_str = '18-04-2014'
# Khareef season end date\n",
end_date_str = '18-10-2014'
sf['From'] = pd.to_datetime(sf['From'], infer_datetime_format=True)
sf['To'] = pd.to_datetime(sf['To'], infer_datetime_format=True)
sf = sf[(sf['From'] >= start_date_str) & (sf['To'] <= end_date_str)]
df = df[start_date_str:end_date_str]
# Example view of a tributory \n",
name = '3R'
df[df['name'] == name]['discharge'].plot()
plt.title(name)

days = sorted(list(set(df.index.map(lambda d: d.strftime('%D')))))

# Number of rows = number of days\n",
# Number of columns = number of distributories\n",


violation_matrix = -10*np.ones((len(days), len(distributory_names)))
discharge_threshold = .9
day_index = 0
for day in days:
    daily_data = df[day]
    day_dt = pd.to_datetime(day)
    temp = sf[day_dt >= sf['From']]
    daily_priority = temp[day_dt <= temp['To']]
    name_list = priorities[daily_priority['Group 1'].values[0]]
    temp = [name_list[k] for k in name_list.keys()]
    prioritised_distributory = [val for sub_list in temp for val in sub_list]
    for d in prioritised_distributory:
        d_data = daily_data[daily_data['name'] == d]
        if len(d_data) > 0:
            incidents = (1.0*sum(d_data['discharge'] <= discharge_threshold * design_discharge[d]))/len(d_data) * 100.0
            #print(incidents)
            violation_matrix[day_index, distributory_names.index(d)] = incidents
    day_index = day_index + 1



    vdf = pd.DataFrame(data=violation_matrix, index=days, columns=distributory_names)

n_figs = 5
n_rows = 2
n_cols = 2
fig_name_prefix = "hakra_figure_"
for fig in range(0, n_figs):
    # Want figure numbers starting from 1
    this_fig = plt.figure(fig+1) 
    for i in range(0, n_rows):
        for j in range(0, n_cols):
            idx = fig * n_rows * n_cols + n_cols*i+j
            if idx >= len(distributory_names):
                j = n_cols
                i = n_rows
                break
            name = distributory_names[idx]
            plt.subplot(n_rows, n_cols, n_cols*i + j + 1)
            plt.plot(vdf[name].values, 'b.--')
            plt.title(name + ', disch:' + str(design_discharge[name]))
            plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
            plt.ylim([-10, 100])
            plt.grid('on')
    this_fig.savefig( fig_name_prefix+ str(fig+1) + ".pdf")

from PyPDF2 import PdfFileMerger
from os import remove
pdfs = [fig_name_prefix + str(i+1) + ".pdf" for i in range(0, n_figs)]
merger = PdfFileMerger()
for pdf in pdfs:
    merger.append(pdf)
    remove(pdf)

merger.write("hakra_graphs.pdf")
plt.plot(vdf['9R'].values, '.')
r_9 = df[df['name']=='9R']
plt.plot(r_9['discharge'].values)
df['name'].value_counts().plot(kind='barh'), plt.grid(True)



print('Script finished')
