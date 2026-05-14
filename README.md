# 2023-Hospital-Medicare-Spending-per-Beneficary-Score-MSPB-Analysis
The purpose of this analysis is to produce a sample output of a one-page summary report using 2023 MSBP score data from U.S.-based hospitals.  

## Description

The following steps were conducted within this analysis: 
1. Set up the Log file.
2. Import relevant packages.
3. Explore the data, removing any rows that do not contain a numeric MSPB value.
4. Format the data for the map visual by grouping MSPB values by state and taking the median.
5. Create the map graphic.
6. Create a variable that assigns to each row a region based on which state the hospital is located.
7. Take the median MSPB value for each region.
8. Create a table that contains median MSPB values by U.S. region.
9. Stylize and output the table.
10. Create functions that will be used to design our PDF output (header/subheadings etc.)
11. Write the background information, findings, and conclusionary statements to the PDF.
12. Output the PDF file. 

## Getting Started

### Dependencies
To download the most up-to-date Medicaid data, go to: https://data.cms.gov/provider-data/dataset/rrqw-56er#data-table
or use the "Medicare_Hospital_Spending_Per_Patient-Hospital.csv" included in this repository (downloaded 10/2/2025).

Use "2023MSPBAnalysis.py" to see data cleaning and visualizations code.

Relevant packages: 
import numpy as np
import matplotlib.colors as mcolors
import geopandas as gpd 
from shapely.geometry import Polygon
import os
from fpdf import FPDF
import time
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi 

### Installing

Modify file path names for uploading the Medicaid dataset and output files. 
Install geopandas and dataframe_image in your terminal using: 

pip install geopandas
pip install dataframe_image

## Useful Resources
https://david-kyn.medium.com/workplace-automation-generate-pdf-reports-using-python-fa75c50e7715

https://medium.com/@alex_44314/use-python-geopandas-to-make-a-us-map-with-alaska-and-hawaii-39a9f5c222c6

https://pandas.pydata.org/docs/user_guide/style.html

## Author
Emily Quick-Cole

## Output
[2023 MSPB Report](https://github.com/eaqcole/2023-Hospital-Medicare-Spending-per-Beneficary-Score-MSPB-Analysis/blob/1d57700ae1ac30f4eb7e572889142864f647013b/2023MSPBReport.pdf)

## Figures
![Regional Table](regional_table.png)

![Map Image](MSPBmap.png)

## Log File 
<details>
<summary>View Build Logs</summary>

```text
2026-05-14 16:37:39 | INFO | ============================================================
2026-05-14 16:37:39 | INFO | Medicare MSPB Analyzer — Run started
2026-05-14 16:37:39 | INFO | ============================================================
2026-05-14 16:37:39 | INFO | Working directory set to: /Users/emilyquick-cole/Documents/Python/medicare_analysis
2026-05-14 16:37:39 | INFO | --- Loading data ---
2026-05-14 16:37:39 | INFO | Data loaded successfully — 4591 hospitals in dataset
2026-05-14 16:37:39 | INFO | --- Initial data cleaning ---
2026-05-14 16:37:39 | INFO | Rows with null Score values: 0
2026-05-14 16:37:39 | INFO | Hospitals reporting scores as "Not Available": 1682
2026-05-14 16:37:39 | WARNING | "Not Available" scores represent more than 30% of the dataset (1682/4591) — review before proceeding
2026-05-14 16:37:39 | INFO | Hospitals with reportable scores retained: 2909
2026-05-14 16:37:39 | INFO | Score column converted to float64, State column converted to string
2026-05-14 16:37:39 | INFO | --- Computing median MSPB score by state ---
2026-05-14 16:37:39 | INFO | States with median score above 1.0: 10
2026-05-14 16:37:39 | INFO | States with median score equal to 1.0: 8
2026-05-14 16:37:39 | INFO | States with median score below 1.0: 32
2026-05-14 16:37:39 | WARNING | Only 50 states found in scored data — expected 51. Check for missing state records.
2026-05-14 16:37:39 | INFO | --- Generating map visual ---
2026-05-14 16:37:39 | INFO | Loading shapefile from: /Users/emilyquick-cole/Documents/Python/medicare_analysis/cb_2018_us_state_500k
2026-05-14 16:37:39 | INFO | Shapefile merged with MSPB data — 50 states mapped
2026-05-14 16:37:39 | INFO | Merged geodataframe exported to gdf.xlsx for review
2026-05-14 16:37:39 | INFO | Score range for colormap: 0.8650 to 1.0700
2026-05-14 16:37:40 | INFO | Map visual saved to /Users/emilyquick-cole/Documents/Python/medicare_analysis/MSPBmap.png
2026-05-14 16:37:40 | INFO | --- Building regional table ---
2026-05-14 16:37:40 | INFO | There are 51 states in all lists.
2026-05-14 16:37:40 | INFO | All states successfully assigned to a region
2026-05-14 16:37:40 | INFO | Score dataframe with region assignments exported to score_df.xlsx
2026-05-14 16:37:40 | INFO | Hospitals with Score Not Available exported to na_df.xlsx
2026-05-14 16:37:40 | INFO | Regional table built — 6 regions
2026-05-14 16:37:40 | INFO |   Midwest: Median Score 0.9700, Total Hospitals 1355
2026-05-14 16:37:40 | INFO |   West: Median Score 0.9700, Total Hospitals 811
2026-05-14 16:37:40 | INFO |   North East: Median Score 0.9800, Total Hospitals 173
2026-05-14 16:37:40 | INFO |   South: Median Score 1.0000, Total Hospitals 1137
2026-05-14 16:37:40 | INFO |   Mid-Atlantic: Median Score 1.0100, Total Hospitals 428
2026-05-14 16:37:40 | INFO |   South West: Median Score 1.0100, Total Hospitals 626
2026-05-14 16:37:40 | INFO | Totals row added — 4530 total hospitals across all regions
2026-05-14 16:37:40 | INFO | --- Generating regional table visual ---
2026-05-14 16:37:42 | INFO | Regional table visual saved to /Users/emilyquick-cole/Documents/Python/medicare_analysis/regional_table.png
2026-05-14 16:37:42 | INFO | 
--- Regional Table ---
         Region  Total Hospitals  Hospitals w/o Scores  Hospitals w/ Scores  Median Score
0       Midwest             1355                   667                  688          0.97
1          West              811                   306                  505          0.97
2    North East              173                    51                  122          0.98
3         South             1137                   281                  856          1.00
4  Mid-Atlantic              428                    97                  331          1.01
5    South West              626                   219                  407          1.01
6         Total             4530                  1621                 2909           NaN
----------------------------
2026-05-14 16:37:42 | INFO | --- Generating PDF report ---
2026-05-14 16:38:38 | INFO | PDF report saved to /Users/emilyquick-cole/Documents/Python/medicare_analysis/2023MSPBReport.pdf
2026-05-14 16:38:38 | INFO | ============================================================
2026-05-14 16:38:38 | INFO | Medicare MSPB Analyzer — Run complete
2026-05-14 16:38:38 | INFO | ============================================================
2026-05-14 16:44:07 | INFO | ============================================================
2026-05-14 16:44:07 | INFO | Medicare MSPB Analyzer — Run started
2026-05-14 16:44:07 | INFO | ============================================================
2026-05-14 16:44:07 | INFO | Working directory set to: /Users/emilyquick-cole/Documents/Python/medicare_analysis
2026-05-14 16:44:07 | INFO | --- Loading data ---
2026-05-14 16:44:07 | INFO | Data loaded successfully — 4591 hospitals in dataset
2026-05-14 16:44:07 | INFO | --- Initial data cleaning ---
2026-05-14 16:44:07 | INFO | Rows with null Score values: 0
2026-05-14 16:44:07 | INFO | Hospitals reporting scores as "Not Available": 1682
2026-05-14 16:44:07 | WARNING | "Not Available" scores represent more than 30% of the dataset (1682/4591) — review before proceeding
2026-05-14 16:44:07 | INFO | Hospitals with reportable scores retained: 2909
2026-05-14 16:44:07 | INFO | Score column converted to float64, State column converted to string
2026-05-14 16:44:07 | INFO | --- Computing median MSPB score by state ---
2026-05-14 16:44:07 | INFO | States with median score above 1.0: 10
2026-05-14 16:44:07 | INFO | States with median score equal to 1.0: 8
2026-05-14 16:44:07 | INFO | States with median score below 1.0: 32
2026-05-14 16:44:07 | WARNING | Only 50 states found in scored data — expected 51. Check for missing state records.
2026-05-14 16:44:07 | INFO | --- Generating map visual ---
2026-05-14 16:44:07 | INFO | Loading shapefile from: /Users/emilyquick-cole/Documents/Python/medicare_analysis/cb_2018_us_state_500k
2026-05-14 16:44:07 | INFO | Shapefile merged with MSPB data — 50 states mapped
2026-05-14 16:44:07 | INFO | Merged geodataframe exported to gdf.xlsx for review
2026-05-14 16:44:07 | INFO | Score range for colormap: 0.8650 to 1.0700
2026-05-14 16:44:08 | INFO | Map visual saved to /Users/emilyquick-cole/Documents/Python/medicare_analysis/MSPBmap.png
2026-05-14 16:44:08 | INFO | --- Building regional table ---
2026-05-14 16:44:08 | INFO | There are 51 states in all lists.
2026-05-14 16:44:08 | INFO | All states successfully assigned to a region
2026-05-14 16:44:08 | INFO | Score dataframe with region assignments exported to score_df.xlsx
2026-05-14 16:44:08 | INFO | Hospitals with Score Not Available exported to na_df.xlsx
2026-05-14 16:44:08 | INFO | Regional table built — 6 regions
2026-05-14 16:44:08 | INFO |   Midwest: Median Score 0.9700, Total Hospitals 1355
2026-05-14 16:44:08 | INFO |   West: Median Score 0.9700, Total Hospitals 811
2026-05-14 16:44:08 | INFO |   North East: Median Score 0.9800, Total Hospitals 173
2026-05-14 16:44:08 | INFO |   South: Median Score 1.0000, Total Hospitals 1137
2026-05-14 16:44:08 | INFO |   Mid-Atlantic: Median Score 1.0100, Total Hospitals 428
2026-05-14 16:44:08 | INFO |   South West: Median Score 1.0100, Total Hospitals 626
2026-05-14 16:44:08 | INFO | Totals row added — 4530 total hospitals across all regions
2026-05-14 16:44:08 | INFO | --- Generating regional table visual ---
2026-05-14 16:44:09 | INFO | Regional table visual saved to /Users/emilyquick-cole/Documents/Python/medicare_analysis/regional_table.png
2026-05-14 16:44:09 | INFO | 
--- Regional Table ---
         Region  Total Hospitals  Hospitals w/o Scores  Hospitals w/ Scores  Median Score
0       Midwest             1355                   667                  688          0.97
1          West              811                   306                  505          0.97
2    North East              173                    51                  122          0.98
3         South             1137                   281                  856          1.00
4  Mid-Atlantic              428                    97                  331          1.01
5    South West              626                   219                  407          1.01
6         Total             4530                  1621                 2909           NaN
----------------------------
2026-05-14 16:44:09 | INFO | --- Generating PDF report ---
2026-05-14 16:45:09 | INFO | PDF report saved to /Users/emilyquick-cole/Documents/Python/medicare_analysis/2023MSPBReport.pdf
2026-05-14 16:45:09 | INFO | ============================================================
2026-05-14 16:45:09 | INFO | Medicare MSPB Analyzer — Run complete
2026-05-14 16:45:09 | INFO | ============================================================

```

</details>


