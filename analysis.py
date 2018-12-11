import os
import pandas as pd
import numpy as np
import time

import warnings
warnings.filterwarnings('ignore')
# What is the purpose of this?

import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import seaborn as sns

# %matplotlib inline
plt.style.use("seaborn-whitegrid")
plt.rcParams['savefig.facecolor']='white'

params = {'figure.figsize' : (18,12),
            'axes.titlesize' : 20}
plt.rcParams.update(params)

# If directory does not exist, create that exist
def check_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

# bar chart for distribution
def plot_pie_chart(df, column, save = False):

    temp = df[column].value_counts()
    temp = pd.DataFrame({'labels': temp.index,
                       'values': temp.values
                      })
    values = temp['values']
    labels = temp['labels']

    fig = plt.figure(figsize=(12, 12), facecolor='w')
    bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.6)
    patches = plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance = 0.8,
        textprops={'fontsize': 20, 'bbox': bbox_props})
    plt.axis('equal')
    title = 'Distribution of ' + column
    plt.title(title, loc = 'center', y=1.08, fontsize = 25)
    plt.tight_layout()

    if save:
        saved_path = os.path.join(plot_dir, title).replace(' ', '-')
        fig.savefig(saved_path, dpi=200, bbox_inches="tight")
    else:
        plt.show()

    plt.close()

def plot_box(df, column, save = False):

    temp = df[column].value_counts()
    temp = pd.DataFrame({'labels': temp.index,
                       'values': temp.values
                      })
    values = temp['values']
    labels = temp['labels']

    fig = plt.figure(figsize=(12, 12), facecolor='w')
    bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.6)
    patches = plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance = 0.8,
        textprops={'fontsize': 20, 'bbox': bbox_props})
    plt.axis('equal')
    title = 'Distribution of ' + column
    plt.title(title, loc = 'center', y=1.08, fontsize = 25)
    plt.tight_layout()

    if save:
        saved_path = os.path.join(plot_dir, title).replace(' ', '-')
        fig.savefig(saved_path, dpi=200, bbox_inches="tight")
    else:
        plt.show()

    plt.close()

data_path = 'data/Glassdoor_Jobs_Data.csv'
plot_dir = 'plot'
check_dir(plot_dir)

jobs_df = pd.read_csv(data_path, encoding = "ISO-8859-1")
print(jobs_df.shape)
print(jobs_df.isnull().sum())
print(jobs_df.nunique())
print(jobs_df.describe())
jobs_df.head()

# Data Cleaning ================================================================
jobs_df = jobs_df.rename(columns = {'Comapny Description': 'Company Description'})

# Industry
# Remove duplicates in "Company" and "Industry" pair, count distinct
df = jobs_df.drop_duplicates(['Company', 'Industry']).groupby(['Company'])['Industry'].count().reset_index()
df.shape
jobs_df.shape
companies_more_than_1_industry = list(df[df['Industry'] > 1]['Company'])
companies_more_than_1_industry
# Two companies categorize itself under 2 industries, " Citibank" and "MSD"

# Companies in the same industry as "Citibank"
jobs_df[jobs_df['Company'] == companies_more_than_1_industry[0]]['Industry'].value_counts()
citibank_industry_0 = jobs_df[jobs_df['Company'] == companies_more_than_1_industry[0]]['Industry'].value_counts().index[0]
citibank_industry_0
# Companies in the industry same as the first
jobs_df[jobs_df['Industry'] == citibank_industry_0]['Company'].unique()
citibank_industry_1 = jobs_df[jobs_df['Company'] == companies_more_than_1_industry[0]]['Industry'].value_counts().index[1]
citibank_industry_1
# Only three companies in the industry citibank_industry_0
jobs_df['Industry'] = jobs_df['Industry'].replace(citibank_industry_0, citibank_industry_1)
jobs_df['Company'] = jobs_df['Company'].replace('Citibank NA', 'Citibank')
jobs_df[jobs_df['Company'] == 'Citibank NA'].shape

# Companies in the same industry as "MSD"
jobs_df[jobs_df['Company'] == companies_more_than_1_industry[1]]['Industry'].value_counts()
msd_industry_0 = jobs_df[jobs_df['Company'] == companies_more_than_1_industry[1]]['Industry'].value_counts().index[0]
msd_industry_0
msd_industry_1 = jobs_df[jobs_df['Company'] == companies_more_than_1_industry[1]]['Industry'].value_counts().index[1]
msd_industry_1
jobs_df[jobs_df['Industry'] == msd_industry_0]['Company'].unique()
# Only MSD is in this industry
jobs_df[jobs_df['Industry'] == msd_industry_1]['Company'].unique()
jobs_df['Industry'] = jobs_df['Industry'].replace('Wholesale', 'Biotech & Pharmaceuticals')

# Fill NA
jobs_df['Industry'] = jobs_df['Industry'].fillna('NA')


# Companies, take out NAs ('Company' field should not be NA)
jobs_df = jobs_df[~pd.isnull(jobs_df['Company'])]

jobs_df.shape


# Head Quarter
df = jobs_df.drop_duplicates(['Company', 'Head Quarter']).groupby(['Company'])['Head Quarter'].count().reset_index()
companies_more_than_1_hq = list(df[df['Head Quarter'] > 1]['Company'])
companies_more_than_1_hq
for company in companies_more_than_1_hq:
    hq = jobs_df[jobs_df['Company'] == company]['Head Quarter'].value_counts().index[0]
    jobs_df.loc[jobs_df['Company'] == company, 'Head Quarter'] = hq

# Fill NA
jobs_df['Head Quarter'] = jobs_df['Head Quarter'].fillna('NA')


# Company size
df = jobs_df.drop_duplicates(['Company', 'Company Size']).groupby(['Company'])['Company Size'].count().reset_index()
companies_more_than_1_size = list(df[df['Company Size'] > 1]['Company'])
companies_more_than_1_size
# There are companies more than one size
for company in companies_more_than_1_size:
    size = jobs_df[jobs_df['Company'] == company]['Company Size'].value_counts().index[0]
    jobs_df.loc[jobs_df['Company'] == company, 'Company Size'] = size
jobs_df = jobs_df[~pd.isnull(jobs_df['Company Size'])]
jobs_df.shape
sizes = list(jobs_df['Company Size'].value_counts().index)
sizes
sizes_map = {size: int(sum([int(size.split()[0]), int(size.split()[2])]) / 2) for size in sizes[1:]}
# sizes_map indicates the size range and the mid value in the interval
# Last range is "10000+", assign the mid value to be 25000
sizes_map[sizes[0]] = 25000
sizes_map
# Just treate the company size as the mid value of the internval its size is in.
jobs_df['Company Size (Num)'] = jobs_df['Company Size'].map(sizes_map)


# Compant Revenue
revenues = list(jobs_df['Company Revenue'].value_counts().index)
revenues
# Revenue is also indicated as a range, but not the exact value. Do the same manipulation as the company size
# Use revenue.split()[0][:1] to get the lower bound(remove $), revenue.split()[0][:1] too get the upper bound
revenue_map = {revenue: int(sum([int(revenue.split()[0][1:]), int(revenue.split()[2][1:])]) / 2) * 10**(6 if revenue.split()[-2] == 'million' else 9) for revenue in revenues[1:-1]}
# Deal with the largest range and the smallest range
revenue_map[revenues[0]] = 25 * 10**9
revenue_map[revenues[-1]] = 0.5 * 10**6
jobs_df['Company Revenue (Num)'] = jobs_df['Company Revenue'].map(revenue_map)


# Overall Rating
df = jobs_df.drop_duplicates(['Company', 'Overall Rating']).groupby(['Company'])['Overall Rating'].count().reset_index()
companies_more_than_1_rating = list(df[df['Overall Rating'] > 1]['Company'])
companies_more_than_1_rating
# Some companies have more than 1 ratings, take the first one
for company in companies_more_than_1_rating:
    rating = jobs_df[jobs_df['Company'] == company]['Overall Rating'].value_counts().index[0]
    jobs_df.loc[jobs_df['Company'] == company, 'Overall Rating'] = rating

# Company with no rating
company_no_rating = list(set(jobs_df[pd.isnull(jobs_df['Overall Rating'])]['Company']))
len(company_no_rating)
for company in company_no_rating:
    ratings = list(jobs_df[jobs_df['Company'] == company]['Overall Rating'].value_counts().index)
    if len(ratings) != 0:
        jobs_df.loc[jobs_df['Company'] == company, 'Overall Rating'] = ratings[0]
rating_mode = jobs_df['Overall Rating'].mode()[0]
jobs_df['Overall Rating'].fillna(rating_mode, inplace = True)

sns.distplot(jobs_df['Overall Rating'])
jobs_df.loc[jobs_df['Overall Rating'] == -1, 'Overall Rating'] = rating_mode


# Founded Year
sns.distplot(jobs_df['Founded Year'])
df = jobs_df.drop_duplicates(['Company', 'Founded Year']).groupby(['Company'])['Founded Year'].count().reset_index()
companies_more_than_1_founded_year = list(df[df['Founded Year'] > 1]['Company'])
companies_more_than_1_founded_year
for company in companies_more_than_1_founded_year:
    years = list(jobs_df[jobs_df['Company'] == company]['Founded Year'].value_counts().index)
    if 0 in years:
        years.remove(0)
    jobs_df.loc[jobs_df['Company'] == company, 'Founded Year'] = years[0]
jobs_df['Founded Year'].replace(0, np.nan, inplace = True)
year_mode = jobs_df['Founded Year'].mode()[0]
jobs_df['Founded Year'].fillna(year_mode, inplace = True)


# Data Plotting ================================================================
# Univariate
plot_pie_chart(jobs_df, 'Company Size')
plot_pie_chart(jobs_df, 'Company Size', save = True)
plot_pie_chart(jobs_df, 'Company Revenue')
plot_pie_chart(jobs_df, 'Company Revenue', save = True)

sns.distplot(jobs_df['Overall Rating'])
sns.distplot(jobs_df['Founded Year'])

sns.catplot(x="Company Size", kind="count", data=jobs_df, order=list(jobs_df[~pd.isnull(jobs_df['Company Size (Num)'])].sort_values('Company Size (Num)')['Company Size'].unique()), height=8, aspect=12/8)
sns.catplot(x="Company Revenue", kind="count", data=jobs_df, order=list(jobs_df[~pd.isnull(jobs_df['Company Revenue (Num)'])].sort_values('Company Revenue (Num)')['Company Revenue'].unique()), height=12, aspect=12/8)
sns.catplot(x="Company Revenue", kind="count", data=jobs_df, order=list(jobs_df.sort_values('Company Revenue (Num)')['Company Revenue'].unique()), height=8, aspect=12/8)

jobs_df.columns


# Bivariate
sns.catplot(x="Company Size", y="Company Revenue (Num)", order=list(jobs_df.sort_values('Company Size (Num)')['Company Size'].unique()), kind="box", data=jobs_df, height=8, aspect=12/8)
sns.catplot(x="Company Size", y="Salary 50th Percentile", order=list(jobs_df.sort_values('Company Size (Num)')['Company Size'].unique()), kind="box", data=jobs_df, height=8, aspect=12/8)
sns.catplot(x="Company Size", y="Salary 10th Percentile", order=list(jobs_df.sort_values('Company Size (Num)')['Company Size'].unique()), kind="box", data=jobs_df, height=8, aspect=12/8)
sns.catplot(x="Company Size", y="Salary 90th Percentile", order=list(jobs_df.sort_values('Company Size (Num)')['Company Size'].unique()), kind="box", data=jobs_df, height=8, aspect=12/8)

df = pd.concat([jobs_df[['Company Size', 'Salary 10th Percentile']].rename(columns = {'Salary 10th Percentile': 'Salary'}), jobs_df[['Company Size', 'Salary 50th Percentile']].rename(columns = {'Salary 50th Percentile': 'Salary'}), jobs_df[['Company Size', 'Salary 90th Percentile']].rename(columns = {'Salary 90th Percentile': 'Salary'})])
df['Salary Type'] = ['Salary 10th Percentile'] * jobs_df.shape[0] + ['Salary 50th Percentile'] * jobs_df.shape[0] + ['Salary 90th Percentile'] * jobs_df.shape[0]
fig = sns.catplot(x="Company Size", y="Salary", hue = 'Salary Type', order=list(jobs_df.sort_values('Company Size (Num)')['Company Size'].unique()), kind="box", data=df, height=8, aspect=12/8)
title = "Salary Range for Company with Different Size"
plt.title(title, loc = 'center', y=1.08, fontsize = 25)
saved_path = os.path.join(plot_dir, title).replace(' ', '-')
fig.savefig(saved_path, dpi=200, bbox_inches="tight")


# Plot Word Cloud
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

text = " ".join(str(review) for review in jobs_df['Job Description'])
print ("There are {} words in the combination of all review.".format(len(text)))

# Create stopword list:
stopwords = set(STOPWORDS)
plt.figure(figsize=(20,10))
wordcloud = WordCloud(width=1600, height=800, stopwords=stopwords, background_color="white").generate(text)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)
plt.savefig('wordcloud.png', bbox_inches='tight')
