import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from pandas.plotting import scatter_matrix
import matplotlib as mpl
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

mpl.rcParams.update({
    'font.size'           : 20.0,
    'axes.titlesize'      : 'large',
    'axes.labelsize'      : 'medium',
    'xtick.labelsize'     : 'medium',
    'ytick.labelsize'     : 'medium',
    'legend.fontsize'     : 'large',
})


def avg_metric_by_product(df, metric):
    '''
    INPUT: dataframe, string
    OUTPUT: dataframe

    Groups dataframe by product id and averages each product over the given
    metric (column)
    '''

    return df.groupby('product_id').mean()[metric].reset_index()

def get_beta_params(df, metric):
    '''
    INPUT: dataframe, string
    OUTPUT: float, float

    Calculates alpha and beta for beta distribution using the mean and standard
    deviation
    '''
    df[metric] = df[metric]/df[metric].max()
    mu = np.mean(df.loc[:,metric])
    sd = np.std(df.loc[:,metric])
    alpha = (((1 - mu )/sd**2) - (1/mu)) * mu**2
    beta = alpha * ((1 / mu) - 1)
    return(alpha, beta)

def beta_test(a1, a2, b1, b2):
    '''
    INPUT: float, float, float, float
    OUTPUT: float

    Runs a Baysian hypothesis test on two distributions with parameters a and b.
    Returns a probability
    '''
    count = 0
    for i in range(10000):
        if np.random.beta(a1, b1) > np.random.beta(a2, b2):
            count +=1
    return count/10000

def plot_distribution(vines_avgs, verified_avgs, metric):
    '''
    INPUT: dataframe, dataframe, string
    OUTPUT: graph

    Graphs the probability distribution of a column from each of two dataframes along with
    their fitted beta distribution
    '''
    vines_a, vines_b = get_beta_params(vines_avgs, metric)
    ver_a, ver_b = get_beta_params(verified_avgs, metric)
    random_variable = metric.replace('_', ' ')

    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    x = np.linspace(0, 1, 100)

    ax.plot(x, stats.beta.pdf(x, vines_a, vines_b),'r-', lw=5, alpha=0.6, label='beta pdf')
    ax2.plot(x, stats.beta.pdf(x, ver_a, ver_b),'r-', lw=5, alpha=0.6, label='beta pdf')

    ax.hist(vines_avgs[metric], bins = 15, rwidth = 0.75, density = True)
    ax2.hist(verified_avgs[metric], bins = 15, rwidth = 0.75, density = True)

    ax.set_ylabel(f'P({random_variable} = x)')
    ax.set_xlabel('x')
    ax2.set_ylabel(f'P({random_variable} = x)')
    ax2.set_xlabel('x')
    ax.set_title('Vine reviews - ' + metric.replace('_', ' '))
    ax2.set_title('Verified reviews - ' + metric.replace('_', ' '))

    fig2 = plt.figure(figsize=(16, 16))
    bx = fig2.add_subplot(111)
    bx.plot(x, stats.beta.pdf(x, vines_a, vines_b),'r-', lw=5, alpha=0.6, label='beta pdf')
    bx.plot(x, stats.beta.pdf(x, ver_a, ver_b),'b-', lw=5, alpha=0.6, label='beta pdf')
    bx.set_ylabel(f'P({random_variable} = x)')
    bx.set_xlabel('x')
    bx.set_title('Vine reviews - ' + metric.replace('_', ' '))

def compile_analysis(vines, verified, metric):
    '''
    INPUT: dataframe, dataframe, string
    OUTPUT: float

    Calls above functions and returns results of hypothesis test.

    '''
    vines_rating_avgs = avg_metric_by_product(vines, metric)
    verified_rating_avgs = avg_metric_by_product(verified, metric)

    plot_distribution(vines_rating_avgs, verified_rating_avgs, metric)

    vines_a, vines_b = get_beta_params(vines_rating_avgs, metric)
    ver_a, ver_b = get_beta_params(verified_rating_avgs, metric)

    probability = beta_test(vines_a, ver_a, vines_b, ver_b)*100

    print(f'''It is {probability} percent probable that the distribution of
{metric.replace('_', ' ')} for vine reviews is higher than for verified purchases \n''')

    return(beta_test(vines_a, ver_a, vines_b, ver_b))

def rating_distribution_hypothesis(df1, df2, rating):
    '''
    INPUT: dataframe, dataframe, int
    OUTPUT: float

    Calculates sample proporitions for the given rating for each dataframe and
    returns the results of a z-test.

    '''

    df1_positives = df1[df1['star_rating']==rating].count()['star_rating']
    df1_negatives = df1[df1['star_rating']!=rating].count()['star_rating']
    df1_len = df1.star_rating.count()
    proportion_1 = df1_positives/df1_len

    df2_positives = df2[df2['star_rating']==rating].count()['star_rating']
    df2_negatives = df2[df2['star_rating']!=rating].count()['star_rating']
    df2_len = df2.star_rating.count()
    proportion_2 = df2_positives/df2_len

    pooled_proportion = (df1_positives + df2_positives)/(df1_len + df2_len)

    std_err = (pooled_proportion * (1 - pooled_proportion) * ((1/df1_len) + (1/df2_len)))**0.5

    z_score = (proportion_1 - proportion_2)/std_err
    p_value = (1 - stats.norm.cdf(abs(z_score)))*2

    print(f'''Test that the proportion of {rating}'s for vine reviews does not
equal that of verified purchases with a significance level of 0.05''')
    if p_value <= 0.01:
        print(f'We reject the null hypothesis. P-score: {p_value} \n')
    else:
        print(f'We cannot reject the null hypothesis. P-score: {p_value} \n')

    return(z_score, p_value)

#def graph_normals(p1, p2, std_err):


if __name__ == '__main__':

    rev_df = pd.read_csv('data/top_review_set.csv')
    products_df = pd.read_csv('data/vines_top_products.csv', names = ['product_id'])
    word_count_df = pd.read_csv('data/for_regression.csv')

    #separate dfs with vines, verified not vines, not verified or vines
    vines = rev_df[rev_df['vine']==1]
    verified = rev_df[rev_df['verified_purchase']==1 & (rev_df['vine']==0)]
    vine_words = word_count_df[rev_df['vine']==1]
    verified_words = word_count_df[rev_df['verified_purchase']==1 & (rev_df['vine']==0)]

    print(f'Analysis of {len(rev_df)} reviews of {len(products_df)} unique products\n')

    #Baysian hypothesis testing
    compile_analysis(vines, verified, 'star_rating')
    compile_analysis(vines, verified, 'helpful_ratio')
    compile_analysis(vine_words, verified_words, 'review_word_count')

    #Z-test for sample proportions
    for i in range(1, 6):
        rating_distribution_hypothesis(vines, verified, i)

    plt.show()
