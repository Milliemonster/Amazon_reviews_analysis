import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup


def get_reviews(cols, rows, num_products):
    '''Inputs: list of columns to use and number of rows to use when inporting data.
    number of products to return in output dataframe
    Output:
    Set of ASINs of the products with the most vine reviews. Dataframe of individual reviews for products in the ASIN set

    Reads csv file and converts vine and verified purcahase to numerics.
    Sorts product ids by greatest number of vine reviews.
    Returns ASIN set to be used and reviews of products with those ASINs

    '''

    reviews_df = pd.read_csv('data/amazon_reviews_toys.tsv', sep = '\t', usecols = cols, nrows = rows, error_bad_lines = False)

    reviews_df.vine = (reviews_df.vine == 'Y')*1
    reviews_df.verified_purchase = (reviews_df.verified_purchase == 'Y')*1

    vines_df = reviews_df.groupby(['product_id']).sum().sort_values('vine', ascending = False).reset_index()
    vines_df = vines_df[vines_df['vine'] > 20]
    vines_df = vines_df[vines_df['verified_purchase'] > 20]

    print (len(vines_df))

    vines_top_products = list(vines_df.iloc[:, 0])
    #vines_df.iloc[:num_products, 0].to_csv('vines_top_products.csv', index = False)
    top_df = reviews_df[reviews_df['product_id'].isin(vines_top_products)]

    return(vines_top_products, top_df)

def get_prices(ASIN_list):
    '''Inputs: list of ASINs for amazon products
    Returns: dataframe containing ASINs and product price

    writes extracted data to csv
    '''


    extracted_data = pd.DataFrame(columns = ['ASIN', 'price'])
    count = 0


    for i in ASIN_list:
        URL = "http://www.amazon.com/dp/"+i
        page = requests.get(URL,headers={"User-Agent":"Defined"})
        soup = BeautifulSoup(page.content, "html.parser")

        if soup.find(id="price_inside_buybox") != None:
            price = soup.find(id="price_inside_buybox").get_text().strip()
            df = pd.DataFrame([[i, price]], columns = ['ASIN', 'price'])
            extracted_data = pd.concat([extracted_data, df])
            count += 1
            print(count)
            if count % 25 == 0:
                extracted_data.to_csv('amazon_toy_prices.csv')

    return extracted_data


if __name__ == '__main__':

    '''Fetch a subset of reviews and writes to csv
    '''

    cols = ['customer_id', 'review_id', 'product_id','product_category', 'star_rating',
    'helpful_votes', 'total_votes', 'vine', 'verified_purchase', 'review_headline', 'review_body', 'review_date']

    ASINs, rev_df = get_reviews(cols, 10000000, 5000)

    rev_df['helpful_ratio'] = rev_df['helpful_votes']/rev_df['total_votes']

    rev_df.to_csv('top_review_set.csv', index = False)

    #prices = get_prices(ASINs)
