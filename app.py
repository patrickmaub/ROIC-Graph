
import json
import pickle
import base64
from google.cloud import firestore
import matplotlib.pyplot as plt
import pandas as pd
from request_stock import request_stock, get_full_name
from gpt_3 import get_symbols, get_graph
from vars import categories, configs
from gpt_executable import execute_code
from flask import Flask, request, jsonify
from flask_cors import CORS


def main(user_prompt):
    global file_names
    file_names = []
    print(user_prompt, ' user_prompt')

    # Get the stock symbols
    # throw error if no stock symbols
    # gpt-3 for stock symbols from prompt
    symbols_string = get_symbols(user_prompt)

    stock_symbols = []
    stock_symbols = symbols_string.split(',')

    for i in range(len(stock_symbols)):

        stock_symbols[i] = stock_symbols[i].upper().strip('%:, "')
        if stock_symbols[i] == 'ROIC' or stock_symbols[i] == 'NETP' or stock_symbols[i] == 'NET' or stock_symbols[i] == 'COMM' or stock_symbols[i] == 'NYSE' or stock_symbols[i] == 'AND' or stock_symbols[i] == 'CAPEX':
            stock_symbols.remove(stock_symbols[i])

    csv_files = get_csv_files(stock_symbols)
    final_categories = []
    for i in range(len(stock_symbols)):
        df, final_categories = request_stock(stock_symbols[i])
        df.to_csv(stock_symbols[i] + '.csv')

    prompt = set_config(user_prompt, final_categories)

    graph_code = get_graph(user_prompt, csv_files)

    # execute_code(graph_code, file_names)
    return graph_code


def get_csv_files(stock_symbols):
    csv_files = 'The CSV files are '
    for i in range(len(stock_symbols)):
        print(stock_symbols[i])
        stock_symbols[i] = stock_symbols[i].strip()
        csv_files += (' ' + stock_symbols[i] + '.csv')
        file_names.append(stock_symbols[i] + '.csv')
    return csv_files


def set_config(user_prompt, final_categories):
    print('set_config', user_prompt)
    columns = ""
    for category in final_categories:
        columns = columns + "['" + category + "'],"

    # Case 2 stocks
    if len(file_names) == 2:
        configs['graph'] = """Complete this Python 3 module to {}.
Answer:
import pandas as pd
import matplotlib.pyplot as plt
#{} and {} have the following columns: {}
df = pd.read_csv('{}')
df1 = pd.read_csv('{}')
""".format(user_prompt, file_names[0], file_names[1], columns, file_names[0], file_names[1], file_names[0].split('.')[0], file_names[1].split('.')[0],)
    # Case 1 stock
    if len(file_names) == 1:
        configs['graph'] = """Complete this Python 3 module to {}.     

Answer:
import pandas as pd
import matplotlib.pyplot as plt

#{} has the following columns: {}
df = pd.read_csv('{}')

""".format(user_prompt, file_names[0], columns, file_names[0],)

    print(configs['graph'])
    return configs['graph']


app = Flask(__name__)
CORS(app)


@app.route('/prompt', methods=['GET', 'POST'])
def getPrompt():

    user_prompt = request.data.decode('utf-8')
    print('USER PROMPT: ', user_prompt)
    if(user_prompt == '' or user_prompt == None or user_prompt == ' ' or user_prompt == '  ' or user_prompt == '   ' or len(user_prompt) < 4):
        return {'error': 'No prompt provided'}

    try:
        graph_code = main(user_prompt)
    except:
        return {'error': 'Error in scraper.'}

    #img = execute_code(graph_code, file_names)

    try:
        filename = str(execute_code(graph_code, file_names)) + '.png'
    except:
        return {'error': 'Error in graphing.'}

    print(filename)
    with open(filename, "rb") as img:
        f = img.read()
        c = base64.b64encode(f)
        image = c.decode('utf-8')

    prompt = user_prompt

    return {'prompt': prompt, 'image': image, 'code': graph_code}


if __name__ == '__main__':
    app.run()
