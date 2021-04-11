#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 13:57:07 2018

@author: alexandra.darmon
"""
import os
import pandas as pd
from punctuation.parser.punctuation_parser import (
    get_textinfo,
    enrich_features
)
from punctuation.parser.gutenberg_parser import (
        get_gutenberg_texts_tokens
    )
from punctuation.utils.utils import chunks
from multiprocessing import  cpu_count
import multiprocess as mp
import spacy

spacy.load('en_core_web_sm')


def get_current_data(path='data/pickle/gutenberg_token_features/'):
    df_text_final = pd.DataFrame()
    for l in os.listdir(path):
         df_text = pd.read_pickle('{path}/{l}'.format(path=path, l=l))
         df_text_final = pd.concat([df_text_final,df_text])
    return df_text_final



def get_current_data_text(path='data/pickle/gutenberg_text_token/'):
    df_text_final = pd.DataFrame()
    for l in os.listdir(path):
         df_text = pd.read_pickle('{path}/{l}'.format(path=path, l=l))
         df_text_final = pd.concat([df_text_final,df_text])
    return df_text_final



print('start')
df_cache = pd.read_pickle('data/pickle/cache_step1_only2language.p')
total_list_book_ids = list(df_cache['book_id'])
df_text_final = get_current_data(path='data/pickle/gutenberg_token_features/')
list_book_processed = df_text_final['book_id'].tolist()
total_list_book_ids = list(set(total_list_book_ids).difference(set(list_book_processed)))
print(len(total_list_book_ids))

import sys
sys.exit(2)

def enrich_features_pool(list_b):    
    l_text, l_tokens =  get_gutenberg_texts_tokens(list_b)
    df_text = pd.DataFrame(zip(list_b, l_text, l_tokens),
                           columns=['book_id','text', 'tokens_nb_words'])
    # df_text = pd.merge(df_cache, df_text, on='book_id')
    try:
        enrich_features(df_text)
        del df_text['text']
        l = list_b[0]
        df_text.to_pickle('data/pickle/gutenberg_token_features/token_features{}.p'.format(str(l)))
        
    except:
        print(list_b)
        l = list_b[0]
        df_text.to_pickle('data/pickle/error{}.p'.format(str(l)))
        pass
    
    return df_text

print('start 2')


total_threads = cpu_count()

chunk_size = 10 #int(len(total_list_book_ids) / total_threads) + 1
sets_to_be_computed = chunks(total_list_book_ids, chunk_size)
pool = mp.Pool(total_threads)
results = pool.map(enrich_features_pool, sets_to_be_computed)



df_res = df_text_final #pd.DataFrame(None)
for df in results:
    df_res = pd.concat([df_res, df])
    

df_res.to_pickle('data_pickle/cron_job_save.p')
save_as_pickled_object(df_res, 'data_pickle/cron_job_save2.p')
print('done')