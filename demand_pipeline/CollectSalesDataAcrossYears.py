from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

# directory setup
ROOT_DIR = os.path.dirname(os.getcwd()) 
relevant_path = os.path.join(ROOT_DIR, 'Results')

# for dynamic sizing for final data frame 
relevant_fileStarts = ['MomPop', 'notgrapefruit']
file_names = [fn for fn in os.listdir(relevant_path) if any(fn.startswith(st) for st in relevant_fileStarts)]
fileCount = len(file_names)

# initialize the final data frame
df = pd.DataFrame()

# to check which files have been iterated later on
minYear = 3000
maxYear = 1000

# iterating through each excel file/workbook
for myFileIndex in range(0,fileCount): 
    tempFileName = file_names[myFileIndex]
    
    # for one of the columns in the final data frame
    if 'notgrapefruit' in tempFileName:
        source = ['NotGrapefruit']
    else:
        source = ['MomPop']

    # file name 
    myFile = os.path.join(relevant_path, tempFileName)
    
    # open desired results-year excel file
    wb = Workbook(myFile, app_visible = False)

    # fixed data for data frame
    months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
    regions = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']
    
    # extraction of year from selected workbook
    yearCell = Range('annual_report', 'C3').value
    year = str(yearCell[-4:])
    
    # keep tally of the start/end year range for the files processed
    if int(year) > maxYear:
        maxYear = int(year)
    if int(year) < minYear:
        minYear = int(year)
    
    # naming for the practice files in the directory 
    if 'Practice 1' in tempFileName:
        year = str(yearCell[-4:]) + 'p1'
    elif 'Practice 2' in tempFileName:
        year = str(yearCell[-4:]) + 'p2'
    else:
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
print 'Iterated through data from years ' + str(minYear) + ' to ' + str(maxYear) + '.'
df.to_csv('sales_test.csv', index=False)