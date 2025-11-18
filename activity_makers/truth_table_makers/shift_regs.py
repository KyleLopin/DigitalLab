# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


import matplotlib.pyplot as plt

columns = ['S1','S0','RST',
           'Q3','Q2','Q1','Q0','Qout']

rows = ["" for _ in range(8)]  # make 8 blank rows

fig, ax = plt.subplots(figsize=(10, 2.5))
ax.axis('off')

table = ax.table(
    cellText=[[""] * len(columns) for _ in rows],
    colLabels=columns,
    cellLoc='center',
    loc='center'
)

# Formatting
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.0, 1.5)

# Shade headers
for i in range(len(columns)):
    table[(0, i)].set_facecolor('#DDDDDD')

plt.tight_layout()
plt.show()
