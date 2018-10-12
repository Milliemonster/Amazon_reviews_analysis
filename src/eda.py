import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import aquire_clean

import matplotlib as mpl
mpl.rcParams.update({
'font.size'           : 11.0,
'axes.titlesize'      : 'large',
'axes.labelsize'      : 'large',
'xtick.labelsize'     : 'medium',
'ytick.labelsize'     : 'medium',
'legend.fontsize'     : 'large',
})

if __name__ == '__main__':

    rev_df = pd.read_csv('data/top_review_set.csv')
    products_df = pd.read_csv('data/vines_top_products.csv', names = ['product_id'])

    #separate dfs with vines, verified not vines, not verified or vines
    vines = rev_df[rev_df['vine']==1]
    verified = rev_df[rev_df['verified_purchase']==1 & (rev_df['vine']==0)]
    not_verified = rev_df[(rev_df['verified_purchase']==0) & (rev_df['vine']==0)]

    print(rev_df.info())

    most_helpful = rev_df.sort_values('helpful_votes', ascending = False)

    print(most_helpful.review_body[0:10])

    
    #No missing values
    rev_df.isna().sum()

    print(rev_df.corr())

    plt.hist(rev_df['star_rating'], bins = [0, 1.01, 2.01, 3.01, 4.01, 5], align = 'right', rwidth = 0.75)

    rev_df.hist('helpful_votes', log = True, rwidth = 0.75)

    rev_df.hist('total_votes', log = True, rwidth = 0.75)

    rev_df.hist('vine')

    rev_df.hist('verified_purchase')

    len(rev_df.customer_id.unique())


    print(vines.star_rating.describe())
    print(verified.star_rating.describe())
    print(not_verified.star_rating.describe())


    fig = plt.figure(figsize=(16, 16))

    ax = fig.add_subplot(141)
    vine = ax.pie([55.,  239.,  859., 2613., 3510.], autopct='%1.1f%%', pctdistance = 0.8)
    ax.set_xlabel('Vine reviews')

    ax2 = fig.add_subplot(142)
    verified = ax2.pie([ 1325.,   775.,  1293.,  2370., 12557.], autopct='%1.1f%%', pctdistance = 0.8)
    ax2.set_xlabel('Verified reviews \n (excludes vine)')

    ax3 = fig.add_subplot(143)
    not_verified = ax3.pie([ 267.,   97.,  158.,  334., 1003.], autopct='%1.1f%%', pctdistance = 0.8)
    ax3.set_xlabel('Not verified reviews \n (excludes vine)')

    ax3.legend(["1 star", "2 star", "3 star", "4 star", "5 star"],
          title="Star rating",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))

    plt.show()
