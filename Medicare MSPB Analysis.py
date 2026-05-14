''' Medicare Spending Per Beneficiary Analyzer
Date: October 5, 2025
Name: Emily Quick-Cole

Background: Medicare is a federal health insurance program in the United States primarily for people age 65 or older,
but also for younger individuals with certain disabilities, End-Stage Renal Disease (permanent kidney failure),
or Amyotrophic Lateral Sclerosis (ALS). It provides health care coverage through its different parts, such as Part A
for hospital stays and hospice care, Part B for doctors' services and outpatient care, Part C (Medicare Advantage)
which offers a bundled private plan option, and Part D for prescription drug coverage.

According to the Centers for Medicaid and Medicare Services (CMS), The Medicare Spending Per Beneficiary (MSPB)
Measure shows whether Medicare spends more, less, or about the same for an episode of care (episode) at a specific
hospital compared to all hospitals nationally. An MSPB episode includes Medicare Part A and Part B payments for
services provided by hospitals and other healthcare providers the 3 days prior to, during, and 30 days following a
patient's inpatient stay. This measure evaluates hospitals' costs compared to the costs of the national median
(or midpoint) hospital. This measure takes into account important factors like patient age and health status
(risk adjustment) and geographic payment differences (payment-standardization).

Purpose: To produce an informational one to two-page report on states' median MSPB scores using CMS data from 2023.

Data Source: https://data.cms.gov/provider-data/dataset/rrqw-56er

Date of Data Download: October 2, 2025

Results: See PDF output.
'''

# Import relevant packages needed for data exploration and analysis
import numpy as np
import matplotlib.colors as mcolors
import geopandas as gpd
from shapely.geometry import Polygon
import os
import logging
from fpdf import FPDF
import time
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi

# -------------------------------------------------------
# LOGGING SETUP
# Logs are saved to the working directory alongside outputs.
# Each run appends to the same log file so you retain a
# full history of runs, warnings, and data quality flags.
# -------------------------------------------------------
#Set up the log path
log_path = "/Users/emilyquick-cole/Documents/Python/medicare_analysis/medicare_analyzer.log"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_path),  # writes to log file
        logging.StreamHandler()         # also prints to console
    ]
)

logger = logging.getLogger(__name__)
logger.info('=' * 60)
logger.info('Medicare MSPB Analyzer — Run started')
logger.info('=' * 60)


# -------------------------------------------------------
# SETUP
# -------------------------------------------------------
new_directory_path = "/Users/emilyquick-cole/Documents/Python/medicare_analysis"
os.chdir(new_directory_path)
logger.info(f'Working directory set to: {new_directory_path}')


# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
logger.info('--- Loading data ---')

#Load the hospital data
df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')
#Convert to a dataframe
df = pd.DataFrame(df)

#Take the length of the df to get the total number of hospitals
total_hospitals = len(df)
#Print to the log the total number of hospitals in the dataset
logger.info(f'Data loaded successfully — {total_hospitals} hospitals in dataset')


# -------------------------------------------------------
# INITIAL DATA CLEANING
# -------------------------------------------------------
logger.info('--- Initial data cleaning ---')

#count the number of rows that are missing a Score value
rows_with_missing_data = df['Score'].isnull().sum()
#Print this number to the log
logger.info(f'Rows with null Score values: {rows_with_missing_data}')

#Save the number of rows where the Score value is Not Available
na_count = (df['Score'] == 'Not Available').sum()
#Save this number to the log
logger.info(f'Hospitals reporting scores as "Not Available": {na_count}')

# Create a flag if the na_count is above 30%
if na_count / total_hospitals > 0.3:
    logger.warning(f'"Not Available" scores represent more than 30% of the dataset ({na_count}/{total_hospitals}) — review before proceeding')

# Save not available rows and drop from main dataframe
na_df = df[df['Score'] == 'Not Available']
score_df = df[df['Score'] != 'Not Available']

#Print to the log the number of hospitals retained in the dataset
logger.info(f'Hospitals with reportable scores retained: {len(score_df)}')

# Convert Score to float and State to string
score_df['Score'] = score_df['Score'].astype('float64')
score_df['State'] = score_df['State'].astype('string')
#Print these changes to the log
logger.info('Score column converted to float64, State column converted to string')


# -------------------------------------------------------
# MEDIAN SCORE BY STATE
# -------------------------------------------------------
logger.info('--- Computing median MSPB score by state ---')

#Group the score_df values by State and take the median value of the Scores
med_df = score_df.groupby(['State'])['Score'].median().reset_index()
#Sort this dataframe by Score
med_df = med_df.sort_values(by=['Score'], ascending=False)

#identify the number of states with a median score above 1, equal to 1, and below 1
above1 = len(med_df[med_df['Score'] > 1.0])
at1 = len(med_df[med_df['Score'] == 1.0])
below1 = len(med_df[med_df['Score'] < 1.0])

logger.info(f'States with median score above 1.0: {above1}')
logger.info(f'States with median score equal to 1.0: {at1}')
logger.info(f'States with median score below 1.0: {below1}')

# Flag if any states are missing entirely
expected_states = 51  # 50 states + DC
if len(med_df) < expected_states:
    logger.warning(f'Only {len(med_df)} states found in scored data — expected {expected_states}. Check for missing state records.')


# -------------------------------------------------------
# MAP VISUAL
# -------------------------------------------------------
logger.info('--- Generating map visual ---')

#import the shape file
shapefile_path = '/Users/emilyquick-cole/Documents/Python/medicare_analysis/cb_2018_us_state_500k'
# Print to the log the file path of the shape file
logger.info(f'Loading shapefile from: {shapefile_path}')

#read the file
gdf = gpd.read_file(shapefile_path)
#merge the dataframes with median scores onto the gdf shape file
gdf = gdf.merge(med_df, left_on='STUSPS', right_on='State')

#Create a flag that tells how many states were mapped onto the gdf file
logger.info(f'Shapefile merged with MSPB data — {len(gdf)} states mapped')

# Check that AK and HI are present for inset maps
for state in ['AK', 'HI']:
    if state not in gdf['State'].values:
        logger.warning(f'{state} not found in merged geodataframe — inset map for this state will be skipped')

#Export the gdf file to an Excel file document for manual checks
gdf.to_excel('/Users/emilyquick-cole/Documents/Python/medicare_analysis/gdf.xlsx', index=False)

#Print a flag to the log indicating that we exported the GDF file
logger.info('Merged geodataframe exported to gdf.xlsx for review')

# Reproject the gdf dataframe to a different coordinate reference system (CRS) —
# specifically EPSG 2163, which is a U.S.-centered equal-area projection that
# makes the map look more proportional than raw latitude/longitude.
visframe = gdf.to_crs('epsg:2163')

#Save the column name Score to a variable to reference later
variable = 'Score'
#Pulls the minimum and maximum Score values from the geodataframe.
# These are used to anchor the colormap scale so the color range spans
# the actual data range — the lowest scoring state gets the lightest color
# and the highest gets the darkest.
vmin, vmax = gdf.Score.min(), gdf.Score.max()
# Sets the colormap to Yellow-Orange-Brown
colormap = "YlOrBr"

#Print the score range for the colormap to the log file
logger.info(f'Score range for colormap: {vmin:.4f} to {vmax:.4f}')

# Create a helper function makeColorColumn that takes our dataframe, variable, vmin and vmax
# and creates a new column that assigns each row with a color hue
# states with similar scores get similar colors and the full range of
# scores maps consistently across the colormap.
def makeColorColumn(gdf, variable, vmin, vmax):
    #Normalizes the scale based on the vmin and vmax of Score
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax, clip=True)
    # Create the actual color mapper by combining the normalizer with the YlOrBr colormap.
    mapper = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.YlOrBr)
    # converts the score to an RGBA color tuple and then to a hexstring and store the value
    # in the new column
    gdf['value_determined_color'] = gdf[variable].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))
    return gdf

#Apply the function to the gdf dataframe, using the previously defined variables
gdf = makeColorColumn(gdf, variable, vmin, vmax)

#set up the figure and plotting area
fig, ax = plt.subplots(1, figsize=(18, 14))
#Hide the axis and tick lines as this is a map not a chart
ax.axis('off')
# Set the font type
hfont = {'fontname': 'Helvetica'}
#set the map title
ax.set_title('Figure 1: 2023 Median State MSPB Scores', **hfont, fontdict={'fontsize': '38'})

# Create a colorbar legend
fig = ax.get_figure()
# Create a small rectangular plot region for the colorbar and set the coordinates
cbax = fig.add_axes([0.89, 0.21, 0.03, 0.31])

# Add a title above the colorbar
cbax.set_title("Median Medicare Spending\nper Beneficiary Score", **hfont, fontdict={'fontsize': '15', 'fontweight': '0'})

# Create a mapping between numeric MSPB values and colors
sm = plt.cm.ScalarMappable(cmap=colormap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
# Fill in the colorbar legend using the custom axes (cbax)
fig.colorbar(sm, cax=cbax)
# Enlarge the tick labels on the colorbar
cbax.tick_params(labelsize=16)

#Add a note to the figure
ax.annotate("Data: CMS Medicare Spending Per Beneficiary - Hospital, accessed 2 Oct 2025\nhttps://data.cms.gov/provider-data/dataset/rrqw-56er#data-table",
            xy=(0.22, .085), xycoords='figure fraction', fontsize=14, color='#555555')

# Loop through each State row,
for row in visframe.itertuples():
    # Handle AK and HI later
    if row.State not in ['AK', 'HI']:
        # Take the shape of the current state
        vf = visframe[visframe.State == row.State]
        # Retrieves a precomputed color associated with the state's MSPB value
        c = gdf[gdf.State == row.State][0:1].value_determined_color.item()
        # Plot the state on the main map
        vf.plot(color=c, linewidth=0.8, ax=ax, edgecolor='0.8')

# Add Alaska inset map
#Create a smaller plotting area for alaska
akax = fig.add_axes([0.1, 0.17, 0.2, 0.19])
#Hide the axes again
akax.axis('off')
#Create a bounding box to clip Alaska's geometry
polygon = Polygon([(-170, 50), (-170, 72), (-140, 72), (-140, 50)])
#Extract Alaska geometry from the gdf dataframe
alaska_gdf = gdf[gdf.State == 'AK']
#clips geometry to the polygon and draws Alaska in its inset
alaska_gdf.clip(polygon).plot(color=gdf[gdf.State == 'AK'].value_determined_color, linewidth=0.8, ax=akax, edgecolor='0.8')


# Add Hawaii Inset Map
hiax = fig.add_axes([.28, 0.20, 0.1, 0.1])
#Hide the Axes
hiax.axis('off')
# create the bounding box for the Hawaii polygon
hipolygon = Polygon([(-160, 0), (-160, 90), (-120, 90), (-120, 0)])
#Extract the shape of Hawaii from the gdf dataframe
hawaii_gdf = gdf[gdf.State == 'HI']
# Clips the geometry to the polygon and draws Hawaii in its inset
hawaii_gdf.clip(hipolygon).plot(column=variable, color=hawaii_gdf['value_determined_color'], linewidth=0.8, ax=hiax, edgecolor='0.8')

#Builds a file path in the current working directory
map_path = os.getcwd() + '/MSPBmap.png'
#Save the figure
fig.savefig(map_path, dpi=400, bbox_inches="tight")

#Log in the log file that we saved the map, including the map path
logger.info(f'Map visual saved to {map_path}')


# -------------------------------------------------------
# REGIONAL TABLE
# -------------------------------------------------------
logger.info('--- Building regional table ---')

#Create lists that categorize each state by region
ne = ['ME', 'VT', 'NH', 'CT', 'MA', 'RI']
midatl = ['NY', 'PA', 'NJ', 'MD', 'DE', 'DC']
midwest = ['OH', 'MI', 'IN', 'IL', 'WI', 'IA', 'MO', 'MN', 'ND', 'SD', 'NE', 'KS']
southwest = ['OK', 'TX', 'AZ', 'NM']
west = ['CO', 'WY', 'MT', 'UT', 'ID', 'WA', 'OR', 'NV', 'CA', 'AK', 'HI']
south = ['VA', 'WV', 'KY', 'NC', 'TN', 'AR', 'SC', 'GA', 'AL', 'MS', 'LA', 'FL']

#create a master list that holds all of the state names
all_regional_states = ne + midatl + midwest + southwest + west + south
logger.info(f'There are {len(all_regional_states)} states in all lists.')

#Insert a new list title region
score_df.insert(loc=6, column='Region', value=np.nan)
#reset the index of the score_df
score_df = score_df.reset_index()

#Create a helper function that sorts the States into regional categories
def categorize_region(value):
    if value in ne:
        return 'North East'
    elif value in midatl:
        return 'Mid-Atlantic'
    elif value in midwest:
        return 'Midwest'
    elif value in southwest:
        return 'South West'
    elif value in west:
        return 'West'
    elif value in south:
        return 'South'

#apply the function to the score_df and fill the region column
score_df['Region'] = score_df['State'].apply(categorize_region)

# Flag any states that didn't get assigned a region
unassigned = score_df[score_df['Region'].isnull()]['State'].unique().tolist()
if unassigned:
    logger.warning(f'The following states were not assigned a region: {unassigned}')
else:
    logger.info('All states successfully assigned to a region')

# Export the score_df to an Excel file
score_df.to_excel('/Users/emilyquick-cole/Documents/Python/medicare_analysis/score_df.xlsx', index=False)
# Flag the eported file to an Excel file.
logger.info('Score dataframe with region assignments exported to score_df.xlsx')

#Set the region column as a category
score_df['Region'] = score_df['Region'].astype('category')

#Find the median value Score for each region
regional_df = score_df.groupby(['Region'])['Score'].median().reset_index(drop=False)
#Print the value counts of each region
reg_hosp_df = score_df['Region'].value_counts()

# Recall the na_df from earlier and categorize these values by region
na_df['Region'] = na_df['State'].apply(categorize_region)
#create a table of value counts of these states that are missing a score
na_hosp_df = na_df['Region'].value_counts()

#Export to Excel a datafile of the rows that don't have a Score value
na_df.to_excel('/Users/emilyquick-cole/Documents/Python/medicare_analysis/na_df.xlsx', index=False)
# Record to the log that we exported this dataframe to Excel
logger.info('Hospitals with Score Not Available exported to na_df.xlsx')

#Merge the Regional Hospital dataframe onto the regional dataframe
table_df = regional_df.merge(reg_hosp_df, left_on='Region', right_on='Region')
# Merge the Na dataframe onto table dataframe
table_df = table_df.merge(na_hosp_df, left_on='Region', right_on='Region')
#Create a new row that sums the counts
table_df['Total Hospitals'] = table_df['count_x'] + table_df['count_y']
# Take all the rows of table_df and select the specified columns
table_df = table_df.iloc[:, [0, 4, 3, 2, 1]]
# Rename the columns
table_df = table_df.rename(columns={'Score': 'Median Score', 'count_x': 'Hospitals w/ Scores', 'count_y': 'Hospitals w/o Scores'})
#Sort the values by Median Score
table_df = table_df.sort_values('Median Score')

#Save to the log that we built a regional table and the number of regions
logger.info(f'Regional table built — {len(table_df)} regions')
#For each region, print the region and the median score and the number of hospitals
for _, row in table_df.iterrows():
    logger.info(f"  {row['Region']}: Median Score {row['Median Score']:.4f}, Total Hospitals {int(row['Total Hospitals'])}")

# Save the columns we want to sum
cols_to_sum = ['Total Hospitals', 'Hospitals w/o Scores', 'Hospitals w/ Scores']
# Sum the specified columns of the table_Df and save to totals
totals = table_df[cols_to_sum].sum(numeric_only=True)
#convert table row to a series
total_row = pd.Series(totals, name='Total')
#Set the last row value of "Region" as the string Total
total_row['Region'] = 'Total'
# Set the row values as the total_row values
table_df.loc['Total'] = total_row
# Record in the log that we added a totals row
logger.info(f'Totals row added — {int(totals["Total Hospitals"])} total hospitals across all regions')


# -------------------------------------------------------
# REGIONAL TABLE VISUAL
# -------------------------------------------------------
logger.info('--- Generating regional table visual ---')

# set the minimum median value from the Median Score colum as medianvmin
medianvmin = table_df['Median Score'].min()
# Set the maximum median value from the Median Score colum as medianvmax
medianvmax = table_df['Median Score'].max()
# Set the style
styles = [
    dict(selector="caption", props=[
        ("font-size", "20px"),
        ("padding-bottom", "13px"),
        ('text-align', 'left'),
        ('font-family', 'Helvetica')
    ])
]

# Create a function that bolds the row if the Region value =  "Total"
def bold_row(row):
    if row['Region'] == 'Total':
        return ['font-weight: bold'] * len(row)
    else:
        return [''] * len(row)
#reset the table_df index
table_df.reset_index(inplace=True, drop=True)

#create the stylized table
styled_table_df = (table_df.style.hide(axis="index")
                   .set_properties(**{'text-align': 'center', 'font-size': '12pt'})
                   .highlight_null(props="color: transparent;")
                   .format({'Total Hospitals': "{:,}", 'Hospitals w/o Scores': "{:,}",
                            'Hospitals w/ Scores': "{:,}", 'Median Score': "{:.2f}"})
                   .background_gradient(axis=None, vmin=medianvmin, vmax=medianvmax,
                                        cmap=colormap, subset=pd.IndexSlice[0:5, 'Median Score'])
                   .set_caption('Table 1: 2023 Median U.S. Region MSPB Scores')
                   .apply(bold_row, axis=1)
                   .set_table_styles(styles))


#Set the table path
table_path = '/Users/emilyquick-cole/Documents/Python/medicare_analysis/regional_table.png'
# Export the table path
dfi.export(styled_table_df, table_path, dpi=400)
# Record to the log where we saved teh table_path
logger.info(f'Regional table visual saved to {table_path}')

#Print the data for visual 3 to the log
logger.info(f"\n--- Regional Table ---\n{table_df.to_string()}\n----------------------------")


# -------------------------------------------------------
# PDF GENERATION
# -------------------------------------------------------
logger.info('--- Generating PDF report ---')

#Create a helper function to generate a pdf
def create_letterhead(letterhead, pdf):
    pdf.set_font('Helvetica', 'b', 20)
    pdf.multi_cell(0, 8, txt=letterhead, border=0, align='L', fill=0)
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 10)
    current_time = time.localtime()
    today = time.strftime("%B %d, %Y", current_time)
    pdf.write(4, f'{today}')
    pdf.ln(8)
#Create a helper function to generate the title of the PDF
def create_title(title, pdf):
    pdf.set_font('Helvetica', 'b', 20)
    pdf.ln(40)
    pdf.write(5, title)
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(r=128, g=128, b=128)
    current_time = time.localtime()
    today = time.strftime("%d/%m/%Y", current_time)
    pdf.write(4, f'{today}')
    pdf.ln(10)
#Create a subtitle helper function
def create_subtitle(subtitle, pdf):
    pdf.set_font('Helvetica', 'BU', 12)
    pdf.write(5, subtitle)
    pdf.ln(8)
#Create a function to write words to teh pdf
def write_to_pdf(pdf, words):
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, txt=words, border=0, align='L', fill=0)

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

TITLE = "Sample Data Report - Medicare Spending per Beneficiary Score (MSPB) Overview"
LETTERHEAD = "Sample Data Report - Medicare Spending per Beneficiary Score (MSPB) Overview"
WIDTH = 210
HEIGHT = 297
# Set up the PDF and put all information together
pdf = PDF()
pdf.add_page()

create_letterhead(LETTERHEAD, pdf)
create_subtitle('Background', pdf)

write_to_pdf(pdf, "Medicare is a U.S. federal health insurance program primarily for people age 65 or older, but also for younger individuals with certain disabilities, or other chronic conditions. It provides care coverage through different parts, such as Part A for hospital stays and hospice care and Part B for doctors' services and outpatient care.")
pdf.ln(5)

write_to_pdf(pdf, "According to the Centers for Medicaid and Medicare Services (CMS), the Medicare Spending Per Beneficiary (MSPB) Measure shows whether Medicare spends more, less, or about the same for an episode of care (episode) at a specific hospital compared to all hospitals nationally. An MSPB episode includes Medicare Part A and Part B payments for services provided by hospitals and other healthcare providers the 3 days prior to, during, and 30 days following a patient's inpatient stay. This measure evaluates hospitals' costs compared to the costs of the national median (or midpoint) hospital. This measure takes into account important factors like patient age and health status (risk adjustment) and geographic payment differences (payment-standardization).")
pdf.ln(5)

create_subtitle('Visuals and Findings', pdf)

pdf.image("/Users/emilyquick-cole/Documents/Python/medicare_analysis/regional_table.png", 10, 115, 95, 50)
pdf.image("/Users/emilyquick-cole/Documents/Python/medicare_analysis/MSPBmap.png", 105, 115, 95)
pdf.ln(70)

write_to_pdf(pdf, "- In 2023 4,530 hospitals across the U.S. received medicare patients. Of these, 2,909 from 49 different states reported MSPB scores. Eight states had a median MSPB score of 1.0, while 10 states' median scores were above 1.0, and 32 states' median scores were below 1.0.")
pdf.ln(2)
write_to_pdf(pdf, "- These hospitals are located in all regions of the U.S., with the most concentrated in the midwest (1,355), the south (1,137), and the west (811). The midwest and the south had the lowest median MSPB scores (0.97), while the mid-atlantic and the southwest had the greatest (1.01).")
pdf.ln(2)
write_to_pdf(pdf, "- Of the 4,591 hospitals, 1,621 hospitals did not report an MSPB. This may be because the hospitals did not meet the minimum number of beneficiary episodes (25), they had a significant number of episodes that are excluded for specific reasons, or the hospitals opted out of the Medicare program entirely.")
pdf.ln(5)

create_subtitle('Conclusions', pdf)
write_to_pdf(pdf, "A lower MSPB score suggests that a hospital or provider is more cost-efficient than the national average, while a higher score indicates higher spending. The score is used to affect a hospital's payments from Medicare. A higher MSPB score (meaning higher spending) can result in lower incentive payments or financial penalties. Overall, the MSPB measure is designed to identify variations in spending and to incentivize providers to deliver high-quality care in a more cost-effective manner.")
pdf.ln(2)
#Export the pdf
pdf_path = "/Users/emilyquick-cole/Documents/Python/medicare_analysis/2023MSPBReport.pdf"
pdf.output(pdf_path, 'F')
#Set up a flag to show where the PDF was exported to 
logger.info(f'PDF report saved to {pdf_path}')

# -------------------------------------------------------
# RUN COMPLETE
# -------------------------------------------------------
logger.info('=' * 60)
logger.info('Medicare MSPB Analyzer — Run complete')
logger.info('=' * 60)
