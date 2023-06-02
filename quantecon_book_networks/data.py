import pkg_resources
from re import X
import numpy as np
import pandas as pd
import networkx as nx
import json
from pandas_datareader import wb

## Utilities
def read_Z(data_file='data/csv_files/adjacency_matrix.csv', t=10):
    """
    Build the Z matrix from the use table.
    
    * Z[i, j] = sales from sector i to sector j
    
    """
    data_file = pkg_resources.resource_stream(__name__, data_file)

    df1 = pd.read_csv(data_file)
    df1 = df1.set_index("country")

    df2 = df1.replace(np.nan, 0)          # replace nan with 0

    df3 = df2.replace("---", 0)          # replace --- with 0

    countries = list(df3.index)
    countries = np.array(countries)
    countries = np.where(countries == 'CH', 'SW', countries)

    Z = np.asarray(df3.values.tolist(), dtype=np.float64)
    Z_visual = np.where(Z < t, 0, Z)
    
    output = {'Z':Z,'Z_visual':Z_visual, 'countries':countries}
    return output

def read_industry_Z(data_file='data/csv_files/use_15.csv', 
           N=15, 
           columnlist=['Name',
                       'Total Intermediate',
                       'Personal consumption expenditures',
                       'Private fixed investment',
                       'Change in private inventories',
                       'Exports of goods and services',
                       'Government consumption expenditures and gross investment',
                       'Total use of products']):
    """
    Build the Z matrix from the use table.
    
    * Z[i, j] = sales from sector i to sector j
    
    """
    data_file = pkg_resources.resource_stream(__name__, data_file)
    df1 = pd.read_csv(data_file)
    df2 = df1[:N]
    if columnlist != None:
        df3 = df2.drop(columns=columnlist)
    else:
        df3 = df2
    df4 = df3.replace('---', 0)
    Z = np.asarray(df4.values.tolist(), dtype=np.float64)
    return Z

def read_industry_X(data_file='data/csv_files/make_15.csv',
           colname='Total Industry Output',
           N=15):
    """
    Read total industry sales column from the make table.

    """
    data_file = pkg_resources.resource_stream(__name__, data_file)
    df5 = pd.read_csv(data_file)
    X = np.asarray(df5[colname])
    X = X[0:N].astype(np.float64)
    return X


def build_coefficient_matrices(Z, X):
    """
    Build coefficient matrices A and F from Z and X via 
    
        A[i, j] = Z[i, j] / X[j] 
        F[i, j] = Z[i, j] / X[i]
    
    """
    A, F = np.empty_like(Z), np.empty_like(Z)
    n = A.shape[0]
    for i in range(n):
        for j in range(n):
            A[i, j] = Z[i, j] / X[j]
            F[i, j] = Z[i, j] / X[i]

    return A, F

## Chapter data

def introduction():
    """
    Load data used in Introduction chapter. 

        Returns:
            ch_data (dict): Dictionary of data names and associated data objects. Note: some data objects are further nested as dictionaries. 
    """
    
    ch_data = {}

    ## Crude oil
    data_file = "data/crude_oil/data.csv"
    data_file = pkg_resources.resource_stream(__name__, data_file)
    crude_oil = pd.read_csv(data_file, dtype={'product_id': str})

    exporters = crude_oil[["export_value", "location_code"]].groupby(by=["location_code"]).sum().sort_values("export_value", ascending=False)[:10].index
    
    importers = crude_oil[["export_value", "partner_code"]].groupby(by=["partner_code"]).sum().sort_values("export_value", ascending=False)[:21].index
    # importers = set(importers.drop("ANS"))
    importers = set(importers)

    # Aggregate Data for Rest of the World
    row_concord = {}
    other_importers = set(crude_oil.partner_code.unique()).difference(importers)
    for cntry in other_importers:
        row_concord[cntry] = "ROW"
    importers.add("ROW")
    importers = pd.Index(importers, name='partner_code')

    # Aggregate Partner Locations
    crude_oil.partner_code = crude_oil.partner_code.replace(to_replace=row_concord)

    chart_data = crude_oil[["export_value", "location_code", "partner_code"]].groupby(by=["location_code", "partner_code"]).sum().reset_index()

    # country data
    data_file = "data/crude_oil/regions-iso3c.csv"
    data_file = pkg_resources.resource_stream(__name__, data_file)
    cdata = pd.read_csv(data_file)
    country_names = cdata[["alpha-3","name"]].set_index("alpha-3").to_dict()['name']
    country_names["ROW"] = "Rest of World"
    country_names['TWN'] = "Taiwan"
    country_names['GBR'] = "United Kingdom"

    DG_crude = nx.DiGraph()
    for idx,row in chart_data.iterrows():       
        if row.location_code not in exporters:
            continue
        if row.partner_code not in importers:
            continue
        DG_crude.add_weighted_edges_from([(country_names[row.location_code], country_names[row.partner_code], row.export_value)])

    ch_data["crude_oil"] = DG_crude

    ## aircraft_network
    data_file = "data/commercial_aircraft/aircraft_network.gexf"
    data_file = pkg_resources.resource_stream(__name__, data_file)

    ch_data["aircraft_network"] = nx.read_gexf(data_file)

    data_file = "data/commercial_aircraft/aircraft_network_layout.json"
    data_file = pkg_resources.resource_stream(__name__, data_file)
    f = open(data_file.name, "r")
    data = json.loads(f.read())
    pos = {}
    for nd in data['nodes']:
        pos[nd['id']] = np.array([nd['x'], nd['y']])
    ch_data["aircraft_network_pos"] = pos
    
    ## forbes-global2000
    data_file = 'data/csv_files/forbes-global2000.csv'
    data_file = pkg_resources.resource_stream(__name__, data_file)
    dfff = pd.read_csv(data_file)
    dfff = dfff[['Country', 'Sales', 'Profits', 'Assets', 'Market Value']]
    dfff = dfff.sort_values('Market Value', ascending=False)
    ch_data["forbes_global_2000"] = dfff
    
    ## adjacency_matrix
    data_file='data/csv_files/adjacency_matrix.csv'
    ch_data["adjacency_matrix"] = read_Z(data_file, t=0)

    return ch_data


def production():
    """
    Load data used in Production chapter. 

        Returns:
            ch_data (dict): Dictionary of data names and associated data objects. Note: some data objects are further nested as dictionaries. 
    """
    ch_data = {}

    Z, X = read_industry_Z(), read_industry_X()
    us_sectors_15 = {
        "adjacency_matrix": Z,
        "total_industry_sales": X,
        "codes": ( 'ag',    
           'mi',  
           'ut',  
           'co',  
           'ma',  
           'wh',  
           're', 
           'tr',  
           'in',  
           'fi',  
           'pr', 
           'ed',   
           'ar',  
           'ot',  
           'go')
    }

    ch_data["us_sectors_15"] =  us_sectors_15

    data_file = 'data/csv_files/use_71.csv'
    Z_71 = read_industry_Z(
        data_file, N=71,
         columnlist=['Unnamed: 0', 'T001', 'F010', 'F02E', 'F02N', 
                             'F02R', 'F02S', 'F030', 'F040', 'F06C', 'F06E', 
                             'F06N', 'F06S', 'F07C', 'F07E', 'F07N', 'F07S', 
                             'F10C', 'F10E', 'F10N', 'F10S', 'T019'])
    data_file = 'data/csv_files/make_71.csv'
    X_71 = read_industry_X(data_file, N=71)
    A_71, F_71 = build_coefficient_matrices(Z_71, X_71)

    us_sectors_71 = {
        "adjacency_matrix": A_71,
        "total_industry_sales": X_71,
        'codes': ('111CA',
         '113FF',
         '211',
         '212',
         '213',
         '22',
         '23',
         '321',
         '327',
         '331',
         '332',
         '333',
         '334',
         '335',
         '3361MV',
         '3364OT',
         '337',
         '339',
         '311FT',
         '313TT',
         '315AL',
         '322',
         '323',
         '324',
         '325',
         '326',
         '42',
         '441',
         '445',
         '452',
         '4A0',
         '481',
         '482',
         '483',
         '484',
         '485',
         '486',
         '487OS',
         '493',
         '511',
         '512',
         '513', 
         '514',
         '521CI',
         '523',
         '524',
         '525',
         'HS',
         'ORE',
         '532RL',
         '5411',
         '5415',
         '5412OP',
         '55',
         '561',
         '562',
         '61',
         '621',
         '622',
         '623',
         '624',
         '711AS',
         '713',
         '721',
         '722',
         '81',
         'GFGD',
         'GFGN',
         'GFE',
         'GSLG',
         'GSLE')
    }

    ch_data["us_sectors_71"] =  us_sectors_71

    data_file='data/csv_files/use_114_aus.csv'
    Z_114 = read_industry_Z(data_file,
                 N=114,
                 columnlist=None)
    
    data_file='data/csv_files/make_114_aus.csv'
    X_114 = read_industry_X(data_file, colname='total', N=114)
    A_114, F_114 = build_coefficient_matrices(Z_114, X_114)

    au_sectors_114 = {
        "adjacency_matrix": A_114,
        "total_industry_sales": X_114,
        'codes': ('0101',
        '0102',
        '0103',
        '0201',
        '0301',
        '0401',
        '0501',
        '0601',
        '0701',
        '0801',
        '0802',
        '0901',
        '1001',
        '1101',
        '1102',
        '1103',
        '1104',
        '1105',
        '1106',
        '1107',
        '1108',
        '1109',
        '1201',
        '1202',
        '1205',
        '1301',
        '1302',
        '1303',
        '1304',
        '1305',
        '1306',
        '1401',
        '1402',
        '1501',
        '1502',
        '1601',
        '1701',
        '1801',
        '1802',
        '1803',
        '1804',
        '1901',
        '1902',
        '2001',
        '2002',
        '2003',
        '2004',
        '2005',
        '2101',
        '2102',
        '2201',
        '2202',
        '2203',
        '2204',
        '2301',
        '2302',
        '2303',
        '2304',
        '2401',
        '2403',
        '2404',
        '2405',
        '2501',
        '2502',
        '2601',
        '2605',
        '2701',
        '2801',
        '2901',
        '3001',
        '3002',
        '3101',
        '3201',
        '3301',
        '3901',
        '4401',
        '4501',
        '4601',
        '4701',
        '4801',
        '4901',
        '5101',
        '5201',
        '5401',
        '5501',
        '5601',
        '5701',
        '5801',
        '6001',
        '6201',
        '6301',
        '6401',
        '6601',
        '6701',
        '6702',
        '6901',
        '7001',
        '7210',
        '7310',
        '7501',
        '7601',
        '7701',
        '8010',
        '8110',
        '8210',
        '8401',
        '8601',
        '8901',
        '9101',
        '9201',
        '9401',
        '9402',
        '9501',
        '9502')}

    ch_data["au_sectors_114"] =  au_sectors_114

    ## GDP growth rates and std. deviations
    varlist=['NY.GDP.MKTP.KD.ZG']; c='all'; s=1961; e=2020
    countries = ['Brazil', 'United States', 'United Kingdom', 'France', 'Japan', 
             'Indonesia', 'Argentina', 'Mexico', 'Australia', 'South Africa']
    
    gdp_df = wb.download(indicator=varlist, country=c, start=s, end=e)
    gdp_df = gdp_df.unstack(0)["NY.GDP.MKTP.KD.ZG"][countries]

    ch_data['gdp_df'] = gdp_df

    return ch_data 


def optimal_flows():
    """
    Load data used in Optimal Flows chapter. 

        Returns:
            ch_data (dict): Dictionary of data names and associated data objects. Note: some data objects are further nested as dictionaries. 
    """
    ch_data = {}

    return ch_data


def markov_chains_and_networks():
    """
    Load data used in Markov Chains and Networks chapter. 

        Returns:
            ch_data (dict): Dictionary of data names and associated data objects. Note: some data objects are further nested as dictionaries. 
    """

    data = wb.get_countries()
    data = data[data['region'] != 'Aggregates']
    countries = list(data['iso2c'])
    ind = ['NY.GDP.PCAP.CD']

    # NY.GDP.PCAP.CD GDP per capita in current US$ and NY.GDP.PCAP.PP.CD GDP per capita in current international $
    dat = wb.download(indicator=ind, country=countries, start=1960, end=2019, errors="ignore")
    dat = dat.reset_index()
    dat.columns = 'country', 'year', 'gdppc'

    dat0 = wb.download(indicator=ind, country='WLD', start=1960, end=2019, errors="ignore")
    dat0 = dat0.reset_index()
    dat0.columns = 'country', 'year', 'gdppc_w'
 
    dat0 = dat0[['year', 'gdppc_w']]

    df = pd.merge(dat, dat0, on='year').set_index(['country','year'])
    df['gdppc_r'] = df['gdppc'] / df['gdppc_w']

    ch_data = {
        'gdppc_df': df 

    }

    return ch_data


def nonlinear_interactions():
    """
    Load data used in Nonlinear Interactions chapter. 

        Returns:
            ch_data (dict): Dictionary of data names and associated data objects. Note: some data objects are further nested as dictionaries. 
    """
    ch_data = {}

    return ch_data


def appendix():
    """
    Load data used in Appendix chapter. 

        Returns:
            ch_data (dict): Dictionary of data names and associated data objects. Note: some data objects are further nested as dictionaries. 
    """
    ch_data = {}

    return ch_data