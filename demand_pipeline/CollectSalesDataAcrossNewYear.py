from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os
import sys

### works for notgrapefruit results files
# change this based on new results sheets that come in
# newYear = 2019
newYear = sys.argv[1]

# directory setup
ROOT_DIR = os.path.dirname(os.getcwd()) 
relevant_path = os.path.join(ROOT_DIR, 'Results')

# check if the custom year already exists in the old sales.csv file
salesCSV = pd.read_csv('sales.csv')
years = salesCSV['Year']
unique = pd.Series(years.values.ravel()).unique()
strNewYear = str(newYear)
check = strNewYear in unique

# initialize the final data frame
df = pd.DataFrame()

# iterating through each excel file/workbook

if check == True:
    print 'Data from ' + strNewYear + ' already exists in the current sales.csv file'
else:
    
    df = salesCSV
    
    # fixed data for data frame
    months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
    regions = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']
    source = ['notgrapefruit']
    sourceString = ''.join(source)
    
    tempFileName = sourceString + strNewYear + '.xlsm'

    # file name 
    myFile = os.path.join(relevant_path, tempFileName)

    # open desired results-year excel file
    wb = Workbook(myFile, app_visible = False)

    # extraction of year from selected workbook
    yearCell = Range('annual_report', 'C3').value
    year = str(yearCell[-4:])

    # extract pricing across products
    ORA_price_array = np.array(Range('pricing', 'D6:O12', atleast_2d=True).value)
    POJ_price_array = np.array(Range('pricing', 'D15:O21', atleast_2d=True).value)
    ROJ_price_array = np.array(Range('pricing', 'D24:O30', atleast_2d=True).value)
    FCOJ_price_array = np.array(Range('pricing', 'D33:O39', atleast_2d=True).value)

    # extract sales across products
    ORA_sales_array = np.array(Range('ORA', 'D109:O115', atleast_2d=True).value)
    POJ_sales_array = np.array(Range('POJ', 'D109:O115', atleast_2d=True).value)
    ROJ_sales_array = np.array(Range('ROJ', 'D109:O115', atleast_2d=True).value)
    FCOJ_sales_array = np.array(Range('FCOJ', 'D109:O115', atleast_2d=True).value)

    # close excel workbook
    wb.close()

    # ORA
    ORA_data = {'Sales': ORA_sales_array.ravel(),
                'Price': ORA_price_array.ravel(),
                'Region': [region for region in regions for j in xrange(0, len(months))],
                'Product': ['ORA'] * len(regions) * len(months),
                'Year': [str(year)] * len(regions) * len(months),
                'Month': months * len(regions),
                'Source': source * len(regions) * len(months)}

    ORA_dataFrame = pd.DataFrame(ORA_data, columns=['Sales', 'Price', 'Region', 'Product','Year', 'Month', 'Source'])

    # POJ
    POJ_data = {'Sales': POJ_sales_array.ravel(),
                'Price': POJ_price_array.ravel(),
                'Region': [region for region in regions for j in xrange(0, len(months))],
                'Product': ['POJ'] * len(regions) * len(months),
                'Year': [str(year)] * len(regions) * len(months),
                'Month': months * len(regions),
                'Source': source * len(regions) * len(months)}

    POJ_dataFrame = pd.DataFrame(POJ_data, columns=['Sales', 'Price', 'Region', 'Product','Year', 'Month', 'Source'])

    # ROJ
    ROJ_data = {'Sales': ROJ_sales_array.ravel(),
                'Price': ROJ_price_array.ravel(),
                'Region': [region for region in regions for j in xrange(0, len(months))],
                'Product': ['ROJ'] * len(regions) * len(months),
                'Year': [str(year)] * len(regions) * len(months),
                'Month': months * len(regions),
                'Source': source * len(regions) * len(months)}

    ROJ_dataFrame = pd.DataFrame(ROJ_data, columns=['Sales', 'Price', 'Region', 'Product','Year', 'Month', 'Source'])

    # FCOJ
    FCOJ_data = {'Sales': FCOJ_sales_array.ravel(),
                'Price': FCOJ_price_array.ravel(),
                'Region': [region for region in regions for j in xrange(0, len(months))],
                'Product': ['FCOJ'] * len(regions) * len(months),
                'Year': [str(year)] * len(regions) * len(months),
                'Month': months * len(regions),
                'Source': source * len(regions) * len(months)}

    FCOJ_dataFrame = pd.DataFrame(FCOJ_data, columns=['Sales', 'Price', 'Region', 'Product','Year', 'Month', 'Source'])

    # concatenate data frames for single workbook's worth of data
    frames = [ORA_dataFrame, POJ_dataFrame, ROJ_dataFrame, FCOJ_dataFrame]
    sales_dataFrame = pd.concat(frames, ignore_index=True)

    # append the current workbook's sales data to the cumulative data frame object
    df = df.append(sales_dataFrame)

    #########

    # write the cumulative data frame object to CSV
    df.to_csv('sales.csv', index=False)
    print 'Updated sales.csv with data from ' + strNewYear
