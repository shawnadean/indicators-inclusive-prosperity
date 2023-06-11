import requests
import pandas as pd
import shapefile
import numpy as np
import math

# Shape File
#shp = shapefile.Reader(r"C:\Users\Shawna\Documents\UF\Philanthropies\Census Tracts Shp Files\tl_2011_12_tract\tl_2011_12_tract.shp")
#idx = shapefile.Reader(r"C:\Users\Shawna\Documents\UF\Philanthropies\Census Tracts Shp Files\tl_2011_12_tract\tl_2011_12_tract.shx")
'''
column_names_shp = [x[0] for x in shp.fields[1:]]
shp = shp.records()

df_shp = (pd.DataFrame(shp, columns=column_names_shp)
          .query('COUNTYFP in ("003","019","031","089","109") and ALAND != 0')
          [['GEOID', 'COUNTYFP', 'TRACTCE']]
          .rename(columns={'GEOID': 'GEO_ID'})
          .assign(GEO_ID=lambda x: '1400000US' + x['GEO_ID']))
'''

# GDP Growth
API_bea  = 'https://apps.bea.gov/api/data/?UserID=23913CE5-A976-471A-AC8C-7743C25F5053&method=GetData&datasetname=Regional&TableName=CAGDP2&LineCode=1&GeoFIPS=27260%20&Year=ALL&ResultFormat=json'
gdp_bea = (requests.get(API_bea)).json()['BEAAPI']['Results']['Data']

column_names_gdp = gdp_bea[0]
df_gdp = pd.DataFrame(columns=column_names_gdp, data=gdp_bea[1:]).rename(columns={'TimePeriod':'Year'})
df_gdp['Year'] = df_gdp['Year'].astype(int)
df_gdp['DataValue'] = df_gdp['DataValue'].str.replace(',', '').astype(int)

startYear = 2011
endYear = 2021
gdp_start = df_gdp['DataValue'].loc[df_gdp['Year'] == startYear].values[0]
gdp_end = df_gdp['DataValue'].loc[df_gdp['Year'] == endYear].values[0]

gdp_growth = (gdp_end - gdp_start) / gdp_start



# Murders per 100,000 = [(Total # of Murders in MSA) / (Total # of People in MSA)] * 100,000
# Input manually from https://www.fdle.state.fl.us/CJAB/UCR/Annual-Reports/UCR-Annual-Archives

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
    
    

profile = ACS(r'https://api.census.gov/data/2021/acs/acs5/profile?get=GEO_ID,DP05_0001E,DP04_0089E,DP04_0090E,DP04_0002E,DP04_0003E,DP04_0001E,DP04_0018E&for=tract:*&in=state:12&in=county:003,019,031,089,109')
df_profile = profile.toDataFrame()
# DP04_0018E is Houses Built 2010-19 for year 2021

subject = ACS(r'https://api.census.gov/data/2021/acs/acs5/subject?get=GEO_ID,S2503_C01_013E&for=tract:*&in=state:12&in=county:003,019,031,089,109')
df_subject = subject.toDataFrame()

detail = ACS(r'https://api.census.gov/data/2021/acs/acs5?get=GEO_ID,B19053_002E&for=tract:*&in=state:12&in=county:003,019,031,089,109')
df_detail = detail.toDataFrame()

df = pd.merge(pd.merge(df_profile, df_subject, on='GEO_ID', how='left'), df_detail)
df[['DP05_0001E', 'DP04_0089E', 'DP04_0090E', 'DP04_0002E', 'DP04_0003E', 'DP04_0001E', 'DP04_0018E', 'S2503_C01_013E', 'B19053_002E']] = df[['DP05_0001E', 'DP04_0089E', 'DP04_0090E', 'DP04_0002E', 'DP04_0003E', 'DP04_0001E', 'DP04_0018E', 'S2503_C01_013E', 'B19053_002E']].astype(float)

df = df.loc[(df['DP05_0001E'] != -666666666) &
            (df['DP04_0089E'] != -666666666) &
            (df['DP04_0090E'] != -666666666) &
            (df['DP04_0002E'] != -666666666) &
            (df['DP04_0003E'] != -666666666) &
            (df['DP04_0001E'] != -666666666) &
            (df['DP04_0018E'] != -666666666) &
            (df['S2503_C01_013E'] != -666666666) &
            (df['B19053_002E'] != -666666666)]


df['Displacement Risk Ratio'] = df['DP04_0089E'] / df['S2503_C01_013E']
df['Home Ownership Rate'] = df['DP04_0090E'] / df['DP04_0002E']
df['Vacancy Rate'] = df['DP04_0003E'] / df['DP04_0001E']
df['Self-Employment Rate'] = df['B19053_002E'] / df['DP05_0001E']

DRR_75perc = np.percentile(df['Displacement Risk Ratio'], 75)
home_ownership_25perc = np.percentile(df['Home Ownership Rate'], 25)
vacancy_75perc = np.percentile(df['Vacancy Rate'], 75)
self_emp_25perc = np.percentile(df['Self-Employment Rate'], 25)


df = df.reset_index(drop=True)
# Calculating Indicators

for index, row in df.iterrows():
    
    # Positive Economic Growth
    if gdp_growth > 0:
        df.at[index, 'Positive Economic Growth Met'] = round(1)
    else:
        df.at[index, 'Positive Economic Growth Met'] = 0
        
    # Murders per 100,000
    if murders_per_100000 < 25:
        df.at[index, 'Lower Murder Rate Met'] = round(1)
    else:
        df.at[index, 'Lower Murder Rate Met'] = 0
        
    # Low Risk of Displacement
    if row['Displacement Risk Ratio'] < DRR_75perc:
        df.at[index, 'Low Risk of Displacement Met'] = 1
    else:
        df.at[index, 'Low Risk of Displacement Met'] = 0 
        
    # Higher Rates of Home Ownership
    if row['Home Ownership Rate'] >= home_ownership_25perc:
        df.at[index, 'Higher Rates of Home Ownership Met'] = 1
    else:
        df.at[index, 'Higher Rates of Home Ownership Met'] = 0
        
    # Lower Residential Vacancy
    if row['Vacancy Rate'] < vacancy_75perc:
        df.at[index, 'Lower Residential Vacancy Met'] = 1
    else:
        df.at[index, 'Lower Residential Vacancy Met'] = 0
        
    # Increased Housing Density
    if row['DP04_0018E'] > 0:
        df.at[index, 'Increased Housing Density Met'] = 1
    else:
        df.at[index, 'Increased Housing Density Met'] = 0
        
    # Greater Self-Employment
    if row['Self-Employment Rate'] >= self_emp_25perc:
        df.at[index, 'Greater Self-Employment Met'] = 1
    else:
        df.at[index, 'Greater Self-Employment Met'] = 0
        

        

# Presence of Community Organizations
df_orgs = pd.DataFrame(pd.read_csv(r"C:\Users\Shawna\Documents\UF\Philanthropies\2021 Duval Community Orgs Geocodio.csv"), columns=['NAME', 'Latitude','Longitude'])

df_centers = pd.DataFrame(pd.read_csv(r"https://www2.census.gov/geo/docs/reference/cenpop2020/tract/CenPop2020_Mean_TR12.txt"), columns=['COUNTYFP','TRACTCE', 'LATITUDE','LONGITUDE'])
df_centers = df_centers[(df_centers.COUNTYFP==31)]
df_centers["TRACTCE"] = (df_centers["TRACTCE"].astype(str)).str.zfill(6)
df_centers = df_centers.reset_index()
df_comm_org = pd.DataFrame(columns=['TRACTCE', 'd','Presence of Community Organizations Met']) 


for indexC, rowC in df_centers.iterrows():
    #print(indexC, rowC['TRACTCE'])
    df_comm_org.at[indexC,'TRACTCE'] = rowC['TRACTCE']
    
    for indexO, rowO in df_orgs.iterrows():
        #print(indexO, rowO['NAME'])
        orgsLat = rowO['Latitude']
        orgsLong = rowO['Longitude']
        
        centersLat = rowC['LATITUDE']
        centersLong = rowC['LONGITUDE']
        
        d = math.acos( math.cos(math.radians(90-orgsLat)) * math.cos(math.radians(90-centersLat)) + math.sin(math.radians(90-orgsLat)) * math.sin(math.radians(90-centersLat)) * math.cos(math.radians(orgsLong-centersLong)) ) * 3959
                      
        if d <= 1:
            df_comm_org.at[indexC,'Presence of Community Organizations Met'] = 1
            break
        else:
            df_comm_org.at[indexC,'Presence of Community Organizations Met'] = 0
            
            
    df_comm_org.at[indexC,'d'] = d
    #print(indexC, df_comm_org.at[indexC,'TRACTCE'], df_comm_org.at[indexC,'d'], df_comm_org.at[indexC,'Presence of Community Organizations Met']) 

df_comm_org['GEO_ID'] = "1400000US12031" + df_comm_org['TRACTCE']
df_comm_org = pd.DataFrame(df_comm_org, columns=['GEO_ID', 'Presence of Community Organizations Met'])

df = df.merge(df_comm_org, on='GEO_ID', how='left')
#df = df[df['GEO_ID'].str.contains('1400000US12031')]

# Output
output_file_path = r'C:\Users\Shawna\Documents\UF\Philanthropies\Indicators 2021.csv'
df.to_csv(output_file_path, index=False)
#print(df)
# print('done')

