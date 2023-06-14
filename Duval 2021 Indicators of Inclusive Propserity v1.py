import requests
import pandas as pd
import shapefile
import numpy as np
import math


# GDP Growth
bea_UserID = '23913CE5-A976-471A-AC8C-7743C25F5053'
CBSA_FIPS_code = '27260'

API_bea  = ('https://apps.bea.gov/api/data/?UserID=' + 
            bea_UserID +'&method=GetData&datasetname=Regional&TableName=CAGDP2&LineCode=1&GeoFIPS=' + 
            CBSA_FIPS_code + '%20&Year=ALL&ResultFormat=json')

gdp_bea = ((requests
           .get(API_bea))
           .json()['BEAAPI']['Results']['Data'])

column_names_gdp = gdp_bea[0]
df_gdp = (pd.DataFrame(
    columns=column_names_gdp, 
    data=gdp_bea[1:])
          .rename(columns={'TimePeriod':'Year'}))

df_gdp['Year'] = df_gdp['Year'].astype(int)
df_gdp['DataValue'] = (df_gdp['DataValue']
                       .str.replace(',', '')
                       .astype(int))

startYear = 2011
endYear = 2021
gdp_start = (df_gdp['DataValue']
             .loc[df_gdp['Year'] == startYear]
             .values[0])

gdp_end = (df_gdp['DataValue']
           .loc[df_gdp['Year'] == endYear]
           .values[0])

gdp_growth = (gdp_end - gdp_start) / gdp_start


# Murders per 100,000 
murders_per_100000 = 9.865032444


# ACS Tables
class ACS:
    def __init__(self, api):
        self.api = api
        
    def toDataFrame(self):
        data = requests.get(self.api).json()
        column_names = data[0]
        df = pd.DataFrame(columns=column_names, data=data[1:]).drop(['state','county','tract'], axis=1)
        return df
    
endYear = str(endYear)
state_FIPS = '12'
county_fp_int = 31 # enter as int
county_fp = str(county_fp_int).zfill(3)
county_MSA_FIPS = '003,019,031,089,109' # all county fp codes in your MSA, must be 3 digits each

total_population = 'DP05_0001E' # Estimate!!SEX AND AGE!!Total population
median_home_value = 'DP04_0089E' # Estimate!!VALUE!!Owner-occupied units!!Median (dollars)
home_ownership_rate = 'DP04_0046PE' # Percent!!HOUSING TENURE!!Occupied housing units!!Owner-occupied
vacancy_rate = 'DP04_0003PE' # Percent!!HOUSING OCCUPANCY!!Total housing units!!Vacant housing units
built_prev_10 = 'DP04_0018E' # Estimate!!YEAR STRUCTURE BUILT!!Total housing units!!Built 2010 to 2019
median_household_income = 'S2503_C01_013E' # Estimate!!Occupied housing units!!Occupied housing units!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2021 INFLATION-ADJUSTED DOLLARS)!!Median household income (dollars)
with_self_employment_income = 'B19053_002E' # Estimate!!Total:!!With self-employment income
poverty_rate = 'S1701_C03_001E' # Estimate!!Percent below poverty level!!Population for whom poverty status is determined

df_profile = ACS(r'https://api.census.gov/data/' + 
                 endYear + '/acs/acs5/profile?get=GEO_ID,' + 
                 total_population + ',' + 
                 median_home_value + ',' + 
                 home_ownership_rate + ',' + 
                 vacancy_rate + ',' + 
                 built_prev_10 + '&for=tract:*&in=state:' + 
                 state_FIPS + '&in=county:' + 
                 county_MSA_FIPS
            ).toDataFrame()

df_subject = ACS(r'https://api.census.gov/data/' + 
                 endYear + '/acs/acs5/subject?get=GEO_ID,' + 
                 median_household_income + ',' +
                 poverty_rate + '&for=tract:*&in=state:' + 
                 state_FIPS + '&in=county:' + 
                 county_MSA_FIPS    
            ).toDataFrame()

df_detail = ACS(r'https://api.census.gov/data/' + 
                endYear + '/acs/acs5?get=GEO_ID,' + 
                with_self_employment_income + '&for=tract:*&in=state:' + 
                state_FIPS + '&in=county:' + 
                county_MSA_FIPS
            ).toDataFrame()

df = pd.merge(
    pd.merge(df_profile, df_subject, on='GEO_ID', how='left'), 
    df_detail)

df.columns = (['GEO_ID', 
               'Total Population', 
               'Median Home Value', 
               'Home Ownership Rate', 
               'Vacancy Rate', 
               'Units Built Prev 10', 
               'Median Household Income', 
               'Poverty Rate',
               'Population w Self-Employment Income'])

cols_to_float = (['Total Population', 
                  'Median Home Value', 
                  'Home Ownership Rate', 
                  'Vacancy Rate', 
                  'Units Built Prev 10', 
                  'Median Household Income', 
                  'Poverty Rate',
                  'Population w Self-Employment Income'])
df[cols_to_float] = df[cols_to_float].astype(float)

df = df.loc[(df['Total Population'] != -666666666) &
            (df['Median Home Value'] != -666666666) &
            (df['Home Ownership Rate'] != -666666666) &
            (df['Vacancy Rate'] != -666666666) &
            (df['Units Built Prev 10'] != -666666666) &
            (df['Median Household Income'] != -666666666) &
            (df['Population w Self-Employment Income'] != -666666666)]

df['Displacement Risk Ratio'] = df['Median Home Value'] / df['Median Household Income']
df['Home Ownership Rate'] = df['Home Ownership Rate'] / 100
df['Vacancy Rate'] = df['Vacancy Rate'] / 100
df['Self-Employment Rate'] = df['Population w Self-Employment Income'] / df['Total Population']
df['Poverty Rate'] = df['Poverty Rate'] / 100

DRR_75perc = np.percentile(df['Displacement Risk Ratio'], 75)
home_ownership_25perc = np.percentile(df['Home Ownership Rate'], 25)
vacancy_75perc = np.percentile(df['Vacancy Rate'], 75)
self_emp_25perc = np.percentile(df['Self-Employment Rate'], 25)

df = df[df['GEO_ID'].str.contains('1400000US' + state_FIPS + county_fp)]
df = df.reset_index(drop=True)

# Calculating Indicators
for index, row in df.iterrows():
    
    # Positive Economic Growth
    if gdp_growth > 0:
        df.at[index, 'Positive Economic Growth Present'] = round(1)
    else:
        df.at[index, 'Positive Economic Growth Present'] = 0
        
    # Murders per 100,000
    if murders_per_100000 < 25:
        df.at[index, 'Lower Murder Rate Present'] = round(1)
    else:
        df.at[index, 'Lower Murder Rate Present'] = 0
        
    # Low Risk of Displacement
    if row['Displacement Risk Ratio'] < DRR_75perc:
        df.at[index, 'Low Risk of Displacement Present'] = 1
    else:
        df.at[index, 'Low Risk of Displacement Present'] = 0 
        
    # Higher Rates of Home Ownership
    if row['Home Ownership Rate'] >= home_ownership_25perc:
        df.at[index, 'Higher Rates of Home Ownership Present'] = 1
    else:
        df.at[index, 'Higher Rates of Home Ownership Present'] = 0
        
    # Lower Residential Vacancy
    if row['Vacancy Rate'] < vacancy_75perc:
        df.at[index, 'Lower Residential Vacancy Present'] = 1
    else:
        df.at[index, 'Lower Residential Vacancy Present'] = 0
        
    # Increased Housing Density
    if row['Units Built Prev 10'] > 0:
        df.at[index, 'Increased Housing Density Present'] = 1
    else:
        df.at[index, 'Increased Housing Density Present'] = 0
        
    # Greater Self-Employment
    if row['Self-Employment Rate'] >= self_emp_25perc:
        df.at[index, 'Greater Self-Employment Present'] = 1
    else:
        df.at[index, 'Greater Self-Employment Present'] = 0
             

# Presence of Community Organizations
df_orgs = pd.DataFrame(pd.read_csv(r"C:\Users\Shawna\Documents\UF\Philanthropies\2021 Duval Community Orgs Geocodio.csv"), 
                       columns=['NAME', 'Latitude','Longitude'])

df_centers = (pd.DataFrame(
    pd.read_csv(r"https://www2.census.gov/geo/docs/reference/cenpop2020/tract/CenPop2020_Mean_TR" + state_FIPS + ".txt"), 
    columns=['COUNTYFP','TRACTCE', 'LATITUDE','LONGITUDE']))

df_centers = df_centers[(df_centers.COUNTYFP==county_fp_int)]
df_centers["TRACTCE"] = (df_centers["TRACTCE"].astype(str)).str.zfill(6)
df_centers = df_centers.reset_index()
df_comm_org = pd.DataFrame(columns=['TRACTCE', 'd','Presence of Community Organizations Present']) 


for indexC, rowC in df_centers.iterrows():
    #print(indexC, rowC['TRACTCE'])
    df_comm_org.at[indexC,'TRACTCE'] = rowC['TRACTCE']
    
    for indexO, rowO in df_orgs.iterrows():
        #print(indexO, rowO['NAME'])
        orgsLat = rowO['Latitude']
        orgsLong = rowO['Longitude']
        
        centersLat = rowC['LATITUDE']
        centersLong = rowC['LONGITUDE']
        
        d = (math.acos(
            math.cos(math.radians(90-orgsLat)) * 
            math.cos(math.radians(90-centersLat)) + 
            math.sin(math.radians(90-orgsLat)) * 
            math.sin(math.radians(90-centersLat)) * 
            math.cos(math.radians(orgsLong-centersLong))) 
            * 3959)
                      
        if d <= 1:
            df_comm_org.at[indexC,'Presence of Community Organizations Present'] = 1
            break
        else:
            df_comm_org.at[indexC,'Presence of Community Organizations Present'] = 0
            
    df_comm_org.at[indexC,'d'] = d
    #print(indexC, df_comm_org.at[indexC,'TRACTCE'], df_comm_org.at[indexC,'d'], df_comm_org.at[indexC,'Presence of Community Organizations Present']) 

df_comm_org['GEO_ID'] = "1400000US" + state_FIPS + county_fp + df_comm_org['TRACTCE']
df_comm_org = pd.DataFrame(df_comm_org, columns=['GEO_ID', 'Presence of Community Organizations Present'])

df = df.merge(df_comm_org, on='GEO_ID', how='left')

# Output
output_file_path = r'C:\Users\Shawna\Documents\UF\Philanthropies\Indicators 2021.csv'
df.to_csv(output_file_path, index=False)
# print(df.columns)

