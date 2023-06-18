# :house_with_garden: Reducing Poverty without Community Displacement: "Calculating Indicators of Inclusive Prosperity"
Based on the findings of Acharya, R., & Morris, R. (2022). [*Reducing poverty without community displacement: Indicators of inclusive prosperity in U.S. neighborhoods. The Brookings Institution.*](https://www.brookings.edu/research/reducing-poverty-without-community-displacement-indicators-of-inclusive-prosperity-in-u-s-neighborhoods/)

## Table of Contents
1. [Quick Start: How to Use This Repository](https://github.com/shawnadean/indicators-inclusive-prosperity/tree/v4#quick-start-how-to-use-this-repository)
2. [What Are Indicators of Inclusive Prosperity?](https://github.com/shawnadean/indicators-inclusive-prosperity/tree/v4#what-are-the-indicators-of-inclusive-prosperity)
3. Calculation Metholodgy / Data Dictionary
4. How to Calculate the Indicators of Inclusive Prosperity for Your Community
</br>

## Quick Start: How to Use This Repository
With [git installed](https://github.com/git-guides/install-git), run the following commands:
```
mkdir inclusive-prosperity
cd inclusive-prosperity
git clone https://github.com/shawnadean/indicators-inclusive-prosperity.git
start calc_indicators_inclusive_prosperity.py
```
and run the code using your IDE. </br></br>
To open the output file, run
```
 cd tableau_input
 start '2021 Duval Indicators of Inclusive Prosperity - sample file.csv'
```
## What Are the Indicators of Inclusive Prosperity?
Through a 15 year study of over 3,500 US neighhborhoods, Acharya and Morris identified 8 indicators that differentiate neighborhoods that are most likely to experience large decreases in poverty rates and no community distplacement from other neighborhoods in concentrated poverty. By applying these findings, we can help community leaders assess need and identify interventions that will maximize the impact of their resources.
<div align="left">
  <img src="images/8_indicators.png" alt="Photo Not Available" width="600">
</div>
</br>

## Calculation Methodology / Data Dictionary
This methodology is based on the findings of the research study mentioned at the beginning of this file.  We have adapted the methodology to use only publicly available data.</br>
| Indicator                | Type     | Criteria for each neighborhood (census tract)                 | Source                                                                 |
|:------------------------:|:--------:|:------------------------------------------------ |:----------------------------------------------------------------------:|
| Positive Economic Growth | External | in a Metropolitan Statistical Area (MSA) that had positive GDP growth 2006-2021 | [US Bureau of Economic Analysis API](https://apps.bea.gov/api/signup/) |
| Lower Homicide Rates     | External | in a county with < 25 murders per 100,000 residents | [FL Department of Law Enforcement](https://www.fdle.state.fl.us/CJAB/UCR/Annual-Reports/UCR-Annual-Archives) | Low Risk of Displacement* | External | Displacement Risk Ratio (Home Value/Median Household Income) < 75th percentile of the MSA | American Community Survey | Higher Rates of Home Ownership | Internal | Home Ownership Rate >= 25th percentile of the MSA | American Community Survey | Lower Residential Vacancy | Internal | Residential Vacancy Rate < 75th percentile of the MSA | American Community Survey | Increased Housing Density | Internal | # of Housing Units Built 2010-2019 > 0 | American Community Survey | Greater Self-Employment | Internal | Self-Employment Rate >= 25th percentile in the MSA | American Community Survey | Presence of COmmunity Organizations | Internal | has >=1 community-building organization located within 1 mile of the center of the census tract | National Center for Charitable Statistics, US Census Centers of Population |









