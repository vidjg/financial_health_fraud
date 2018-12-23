# !/usr/bin/env python
#
# -*- coding: utf-8 -*-
"""

-----------------------------------------------------
    File Name:          fraud_sample_processing
    Description:        
    Author:             Martin Qian
    Create date:        2018/12/22
    Latest version:     v1.0.1
-----------------------------------------------------
    Change Log:
#---------------------------------------------------#
    v1.0.0              qs          2018/12/22
    1. Create the File
#---------------------------------------------------#
    v1.0.1              qs          2018/12/22
    1. Add year & quarter column
    2. Add output step
-----------------------------------------------------

"""

import os
import re
import datetime
import numpy as np
import pandas as pd


def process(raw_df):
    pass


if __name__ == '__main__':

    # Load Raw Data
    rawdata = pd.read_excel('./reference/违规.xlsx').loc[:, ['代码', '名称', '公告日期', '违规类型', '处罚对象',
                                                           '违规行为', '处理人', '相关法规', '证监会行业', 'Wind行业']]
    rawdata.columns = ['stockcode', 'sname', 'adate', 'disobey_type', 'company_name', 'content', 'regulator', 'law',
                       'industry_name', 'industry_name_w']
    rawdata.dropna(subset=['company_name'], inplace=True)

    # Process the data
    process_df = rawdata.copy(deep=True)

    process_df['f_fake'] = process_df.content.apply(lambda x: '|'.join(re.findall(
        '(?:(?:201\d\s*年度?)[^。]*?(?:虚[增减]|调[^查]整?[增减]?[加多少]?|[多少]计提?)'
        '|(?:虚[增减]|调[^查]整?[增减]?[加多少]?|[多少]计提?)[当本]?期?[^。]*?(?:201\d\s*年度?))'
        '[^。]*?'
        '\s*[\d,]*\d+\.?\d*\s*.?元',
        x)))

    process_df['f_account'] = process_df.f_fake.apply(lambda x: '|'.join(re.findall(
        '(?:(?:201\d\s*年度?)[^。]*?(?:虚[增减]|调[^查]整?[增减]?[加多少]?|[多少]计提?)'
        '|(?:虚[增减]|调[^查]整?[增减]?[加多少]?|[多少]计提?)[当本]?期?[^。]*?(?:201\d\s*年度?))[^。]*?'
        '([^。，、]*?)'  # Account
        '\s*(?:\d|,)*\d+.?\d*\s*.?元',  # Amount
        x)))

    process_df['year'] = process_df.f_fake.apply(lambda x: '|'.join(set(re.findall(
        '(?:(201\d)\s*年度?)',  # Year
        x))))

    process_df['quarter'] = process_df.f_fake.apply(lambda x: '|'.join(set(re.findall(
        '(?:201\d\s*年度?)'  # Year
        '.{0,3}'  # Noise
        '(?:[一二三]季[度报]?|半年报|年报|年末)'  # Quarter
        '(?:、(?:[一二三]季[度报]?|半年报|年报|年末))*',  # Repetitive
        x))))

    # Add label
    process_df['label'] = 0
    process_df.loc[process_df.f_fake != '', 'label'] = 1

    # Output the result
    result_df = process_df.loc[process_df.label == 1, ['company_name', 'stockcode', 'sname', 'f_fake', 'f_account',
                                                       'year', 'quarter']]

    today = datetime.date.today()
    result_df.to_csv('./class_parameter/F_bad_sample_{}_processed.csv'.format(datetime.date.strftime(today, '%y%m%d')),
                     encoding='utf-8', index=False)

    print('Done!')
