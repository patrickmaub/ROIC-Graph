from lxml import html
from vars import categories, data, configs
from bs4 import BeautifulSoup
import requests
from lxml import etree
import pandas as pd
from copy import deepcopy


empty_data = 0
final_categories = list(categories)


def request_stock(tag):

    # scrape
    table_data, years = scrape_table(tag)
    scraped_data = parse_table(table_data)

    chunks = [scraped_data[x:x+len(years)]
              for x in range(0, len(scraped_data), len(years))]

    clean_data = remove_empty_indicies(chunks, years)

    clean_data = chunks
    stock_data = deepcopy(data)

    years = [x for x in years if x != '- -']

    for i in range(24):
        if 0 not in clean_data[i]:
            stock_data[categories[i]] = clean_data[i]
        else:
            stock_data.pop(categories[i])

    stock_data['Year'] = years

    for i in range(len(stock_data['Year'])):
        if stock_data['Year'][i] != 'TTM':
            stock_data['Year'][i] = stock_data['Year'][i][-2:]
    if 'Year' not in final_categories:
        final_categories.append('Year')

    df = pd.DataFrame(stock_data, columns=final_categories)
    stock_data = data

    return df, final_categories


def scrape_table(tag):
    try:
        # req and target table from roic
        url = 'https://roic.ai/company/' + tag
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('body')
        table_values = body.findAll('div', attrs={
            'class': 'min-w-[50px] w-full grow text-center text-xs 2xl:text-sm h-full flex items-center pr-0.5 justify-end'})

        test = body.find('div', attrs={
            'class': 'min-w-[50px] w-full grow text-center text-xs 2xl:text-sm h-full flex pr-0.5 items-center justify-end'})
        table_headers = body.find(
            'div', attrs={'grid grid-flow-col w-full justify-items-center h-full'})
        table_values.insert((17*13)-1, test)

        # clean and scrape years
        yrs = []
        header_text = table_headers.text
        header_text = header_text.replace('TTM', '')
        for i in range((header_text.count('- -'))):
            yrs.append('- -')
        header_text = header_text.replace('- -', '')
        cols = int(len(header_text)/4)
        for i in range(0, cols):
            yrs.append(header_text[i*4:(i+1)*4])
        yrs.append('TTM')

    except:
        print('Error in scrape_table: Failed to scrape data for ' + tag)
        return None, None

    return table_values, yrs


# check for a leftmost empty column

def remove_empty_indicies(data, years):

    print(years)
    cols_to_delete = 0
    for yr in years:
        if '-' in yr:
            for i in range(24):
                del data[i][0]

    return list(data)


def parse_table(table_values):
    clean_data = []
    for val in table_values:
        clean_data.append(parse_text(val.text))
    return clean_data

# Attempt to scrape full name, if cant, use tag


def get_full_name(tag):
    try:
        url = 'https://roic.ai/company/' + tag
        response = requests.get(url)
        tree = html.fromstring(response.text)
        name = tree.xpath(
            '/html/body/div[1]/div/main/div[2]/div[1]/div[2]/div[2]/h1')[0].text
    except:
        print('Error in get_full_name: Failed to retrieve full name for ' + tag)
        name = tag
    return name


def remove_empty(stock_data, years):
    try:
        to_delete = []
        for i in range(24):
            if len(stock_data[categories[i]]) - len(years) != 0 or 0 in stock_data[categories[i]]:
                stock_data.pop(categories[i])
                to_delete.append(i)
        for delete in to_delete:
            final_categories.pop(delete)
        return final_categories
    except:
        print('Error in remove_empty: Could not delete missing values.')


def parse_text(text):
    parser = text.strip("'%()").strip('"')
    parser = parser.replace(',', '')
    if parser == '- -':
        parser = empty_data
    return float(parser)
