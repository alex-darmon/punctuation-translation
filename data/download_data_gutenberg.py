#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 15:37:28 2019

@author: alexandradarmon
"""

import os
from punctuation.logs.logger import create_logger
from punctuation.utils.utils import trial
from punctuation.utils.utils import chunks
from punctuation.parser.gutenberg_cache_parser import get_cache_info
import pandas as pd
from multiprocessing import Pool, cpu_count

BASEDIR = os.path.join(os.path.dirname('__file__'))
logger = create_logger()

trial()

cache_data_directory = 'data/gutenberg_cache/epub'

list_epubs = os.listdir(cache_data_directory)
for x in ['DELETE', '.DS_Store', 'DELETE-52276', 'DELETE-55495']:
    if x in list_epubs:
        list_epubs.remove(x)

# total_threads = cpu_count()

# chunk_size = int(len(list_epubs) / total_threads) + 1
# sets_to_be_computed = chunks(list_epubs, chunk_size)
# pool = Pool(total_threads)
# results = pool.map(get_cache_info, sets_to_be_computed)

# df_res = pd.DataFrame(None)
# for df in results:
#     df_res = pd.concat([df_res, df])

# pool.close()
# pool.join()

df_res = get_cache_info(list_epubs, cache_data_directory=cache_data_directory)


df_res.to_pickle('data/pickle/cache.p')
print(len(df_res))
## Number of books in the cache: 64095



df_res.groupby('language',as_index=False)['book_id']\
    .count().sort_values('book_id', ascending=False).to_csv('data/languages.csv')
    
df_author_lang = df_res.groupby(['author', 'language'],as_index=False)['book_id']\
    .count().sort_values('author', ascending=False).rename(columns={'book_id':'nb_books_lang'})

df_author_book = df_res.groupby('author',as_index=False)['book_id']\
    .count().sort_values('book_id', ascending=False).rename(columns={'book_id':'nb_books'})
   
df_author_language_books = pd.merge(df_author_book, df_author_lang, on=['author'])
df_author_language_books.to_csv('data/author_languages.csv')

df_res.dropna(subset=['title'], inplace=True)
print(len(df_res))
# ### Number of books with a title that is not empty: 64093

df_res = df_res[df_res['language'].isin(['en','fr','it', 'pt','es'])]
print(len(df_res))
### Only  English Spanish, Portuguese, French, Italian  Books: ? now: 57283


list_book_title = df_res[['book_id','title']].to_records()
new_list_no_complete = []
for ind, book_id, title in list_book_title:
    if not('complete' in title.lower()):
        new_list_no_complete.append(book_id)
df_res = df_res[df_res['book_id'].isin(new_list_no_complete)]
print(len(df_res))
## Number of books with a title that doesn't contain 'complete work': 56713

list_author_language = df_res.groupby(['author'])['language'].apply(list).reset_index()
print(len(list_author_language))
# ## Number of authors 18517

list_author_language['nb_languages'] = list_author_language['language'].apply(lambda x : len(set(x)))
list_author_language = list_author_language[\
            (list_author_language.nb_languages >= 2)]
print(len(list_author_language))
## Number of authors with more than 2 books: 731

df_res_only2language = df_res[df_res.author.isin(list(list_author_language['author']))]
print(len(df_res_only2language))
# ## Number of books from author with more than 10 books: 25351 now: 21476

df_res.to_pickle('data/pickle/cache_step1.p')
df_res_only2language.to_pickle('data/pickle/cache_step1_only2language.p')
