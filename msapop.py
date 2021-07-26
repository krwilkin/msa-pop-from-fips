# -*- coding: utf-8 -*-
"""
python scipt to construct crosswalk between fips codes and msas and add
msa population

NOTES:
msa definitions based on april 2018 omb release (see 'msadefs' variable below).
population size taken from census population totals 2010-2019 for each county and
summed by msa 

Created on Fri Jun  4 13:06:02 2021

@author: wilki341
"""

# import modules
import os
import re
import json
import pandas as pd
import numpy as np


# change directory
os.chdir( '' )


# url to msa definitions file
msadefs = 'https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2018/delineation-files/list1.xls'


# import definitions file
msadf = pd.read_excel( msadefs , skiprows = 2 )

# rename fields
msafields = ['cbsa', 'md', 'csa', 'cbsa_title', 'metro_micro', 'md_title',
             'csa_title', 'county_name', 'state_name', 'stfips', 'ctyfips' ,
             'central_outlying']

msadf.columns = msafields

msadf.head()


# drop non-msa records and restrict columns to cbsa code and fips codes
msadf = msadf[msadf['metro_micro']=='Metropolitan Statistical Area']
msadf = msadf[['cbsa','cbsa_title','stfips','ctyfips']]

# drop puerto rico entries
msadf = msadf[msadf['stfips']!=72]

msadf.reset_index(drop=True, inplace=True)


'''
work with population totals by county
'''
# define link to pop estimates file and import
cntypop = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv'

popdf = pd.read_csv( cntypop , encoding = 'iso-8859-1' )

# subset variables
popdf = popdf[['STATE','COUNTY','POPESTIMATE2018','POPESTIMATE2019']]

# rename pop estimate fields to make more manageable
popdf.columns = ['stfips','ctyfips','pop2018','pop2019']


'''
join population totals with msa crosswalk file and sum totals by msa
'''
msapop = pd.merge( msadf ,
                   popdf ,
                   on = ['stfips', 'ctyfips'] ,
                   how = 'left' )

msapop18 = msapop.groupby('cbsa')['pop2018'].sum().reset_index()
msapop19 = msapop.groupby('cbsa')['pop2019'].sum().reset_index()

# add year and create msa population panel
msapop18.columns = ['cbsa','popest']
msapop19.columns = ['cbsa','popest']

msapop18['year']=2018
msapop19['year']=2019

msapop = pd.concat([msapop18, msapop19])
msapop.reset_index(drop=True, inplace=True)


# join msa and fips crosswalk with county estimates
msapopxw = pd.merge( msapop ,
                     msadf ,
                     on = 'cbsa' )

# convert fips to integer
msapopxw['stfips']=msapopxw['stfips'].apply(lambda x: int(x))
msapopxw['ctyfips']=msapopxw['ctyfips'].apply(lambda x: int(x))


'''
export to json
'''
with open( 'msapop.json' , 'w' ) as f:
    json.dump( msapopxw.to_dict(orient='records') , f , indent = 4 )


