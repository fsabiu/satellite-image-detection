from datetime import date, timedelta
import os
import random
import string
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import pandas as pd
import report_utils
from testdata.polish_names.generator import generate_people
from testdata.report_data import samples

def generateNames(n):
    n_males = n//2
    n_females = n - n_males
    males = generate_people(n_males, "M")
    females = generate_people(n_females, "F")
    
    res = males + females
    random.shuffle(res)
    
    first_names = [item.split()[0] for item in res]
    last_names = [item.split()[1] for item in res]
    
    return first_names, last_names

def generateTitles(n):
    return random.sample(samples.titles, n)

def generateDescriptions(n):
    return random.sample(samples.descriptions, n)

def generateTags(n, max_tags):
    tags = []
    for i in range(n):
        tags.append(random.sample(samples.tags, random.randrange(1, max_tags)))
    return tags

def generateDates(n):
    # initializing dates ranges 
    date1, date2 = date(2017, 6, 3), date(2020, 1, 15)
    
    # getting days between dates
    dates_bet = date2 - date1
    total_days = dates_bet.days

    creationDates = []
    updateDates = []
    
    for idx in range(n):
        random.seed(a=None)

        # getting random days
        randay = random.randrange(total_days)

        # getting random dates 
        creationDates.append(date1 + timedelta(days=randay))
        updateDates.append(date2 + timedelta(days=randay))
        
    return creationDates, updateDates

def generateBool(n): # Metadata available
    res = []
    for i in range(n):
        if(random.randint(1, 100)<50):
            res.append(False)
        else:
            res.append(True)
    return res

def generateIDs(n):
    ids = []
    while len(ids) < n:
        id = ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=7))
        if id not in ids:
            ids.append(id)
    return ids

def generateCoordinates(n):
    rectangles = []
    for i in range(n):
        # Generate random coordinates 
        x1 = random.uniform(49.00, 55.00)
        y1 = random.uniform(14.00, 32.00)
        
        side_length = random.uniform(0.01, 0.01)
        x2 = x1 + side_length
        y2 = y1 + side_length

        # Ensure that the second coordinate is always lower-right corner
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 > y1:
            y1, y2 = y2, y1

        # Add the rectangle coordinates to the list
        rectangles.append(((x1, y1), (x2, y2)))

    fromCoordx = [item[0][0] for item in rectangles]
    fromCoordy = [item[0][1] for item in rectangles]
    toCoordx = [item[1][0] for item in rectangles]
    toCoordy = [item[1][1] for item in rectangles]
    
    return fromCoordx, fromCoordy, toCoordx, toCoordy

def generateDummyReports(n):
    first_names, last_names = generateNames(n)
    titles = generateTitles(n)
    descriptions = generateDescriptions(n)
    tags = generateTags(n, 3) # From 1 to 3 tags
    creationDates, updateDates = generateDates(n)
    metadata = generateBool(n)
    ids = generateIDs(n)
    fromCoordx, fromCoordy, toCoordx, toCoordy = generateCoordinates(n)
    
    reports = pd.DataFrame(
    {report_utils.report_fields['title']: titles,
     report_utils.report_fields['desc']: descriptions,
     report_utils.report_fields['fromCoordx']: fromCoordx,
     report_utils.report_fields['fromCoordy']: fromCoordy,
     report_utils.report_fields['toCoordx']: toCoordx,
     report_utils.report_fields['toCoordy']: toCoordy,
     report_utils.report_fields['creationDate']: creationDates,
     report_utils.report_fields['authFirstName']: first_names,
     report_utils.report_fields['authLastName']: last_names,
     report_utils.report_fields['id']: ids,
     report_utils.report_fields['lastUpdateDate']: updateDates,
     report_utils.report_fields['linkedMetadata']: metadata,
     report_utils.report_fields['tags']: tags
    })
    
    return reports


if __name__ == "__main__":

    reports = generateDummyReports(100)
    reports.to_csv("dummy_reports.csv")