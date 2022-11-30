import pandas as pd
import matplotlib.pyplot as plt


import random


def get_random_number():
    return random.randint(1000000, 10000000)


def execute_code(text, file_names):
    plt.switch_backend('Agg')

    if(len(file_names) == 1):

        df = pd.read_csv(file_names[0])
        if 'plt.show()' in text:
            rand = get_random_number()
            text = text.replace(
                'plt.show()', 'plt.savefig("{}.png")'.format(rand))
        print(text)
        exec(text)
        return rand
# df[df.roic>0].plot()
# plt.legend()
    else:

        df = pd.read_csv(file_names[0])
        df1 = pd.read_csv(file_names[1])

        while len(df.index) != len(df1.index):
            if len(df.index) > len(df1.index):
                df = df.drop(df.index[0])
            else:
                df1 = df1.drop(df1.index[0])
        df_to_graph = df.join(df1, lsuffix=file_names[0].split('.')[
                              0], rsuffix=file_names[1].split('.')[0])
        if 'plt.show()' in text:
            rand = get_random_number()
            text = text.replace(
                'plt.show()', 'plt.savefig("{}.png")'.format(rand))
        exec(text)
        return rand
