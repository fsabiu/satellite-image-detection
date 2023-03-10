import ast
from datetime import datetime
import pandas as pd
from testdata.report_data import samples


# Dict DataFrame names -> JSON names
report_fields = {
    "title": "title",
    "desc": "description",
    "fromCoordx": "fromCoordx",
    "fromCoordy": "fromCoordy",
    "toCoordx": "toCoordx",
    "toCoordy": "toCoordy",
    "creationDate": "creationDate",
    "authFirstName": "authorFirstName",
    "authLastName": "authorLastName",
    "id": "reportId",
    "lastUpdateDate": "lastUpdateDate",
    "linkedMetadata": "linkedMetadata",
    "tags": "tags"
}

def convertReports(reports_df):
    reports_entries = reports_df.to_dict(orient="records")
    for record in reports_entries:
        record[report_fields['tags']] = ast.literal_eval(record[report_fields['tags']])
        record[report_fields['creationDate']] = datetime.strptime(record[report_fields['creationDate']], '%Y-%m-%d').date()
        record[report_fields['lastUpdateDate']] = datetime.strptime(record[report_fields['lastUpdateDate']], '%Y-%m-%d').date()
        record[report_fields['fromCoordx']] = float(record[report_fields['fromCoordx']])
        record[report_fields['fromCoordy']] = float(record[report_fields['fromCoordy']])
        record[report_fields['toCoordx']] = float(record[report_fields['toCoordx']])
        record[report_fields['toCoordy']] = float(record[report_fields['toCoordy']])

    return reports_entries


def isContained(x, y, from_x, from_y, to_x, to_y):
    res = False

    writeLog('report_logs.txt', from_x)
    writeLog('report_logs.txt', to_x)
    writeLog('report_logs.txt', from_y)
    writeLog('report_logs.txt', to_y)

    if(float(x) >= from_x and float(x) <= to_x and float(y) <= from_y and float(y) >= to_y):
        res = True

    writeLog('report_logs.txt', res)
    return res

def filterReports(reports, fields, searchAny = False):

    cond = list([0]*len(reports))
    res_reports = []

    text_fields = [report_fields['title'], report_fields['desc'], report_fields['authFirstName'], report_fields['authLastName'], report_fields['id']]

    writeLog('report_logs.txt', "SearchAny: " + str(searchAny))

    if not searchAny:
        for i, report in enumerate(reports):
            for field, filter in fields.items():
                if field in text_fields:
                    if filter.lower() in report[field].lower():
                        cond[i] = cond[i] + 1
                if field == 'x':
                    if('y' in fields and fields['y'] is not None):
                        if isContained(fields['x'], fields['y'], report[report_fields['fromCoordx']], report[report_fields['fromCoordy']], report[report_fields['toCoordx']], report[report_fields['toCoordy']]):
                            cond[i] = cond[i] + 2

                if field in ['tags']:
                    writeLog('report_logs.txt', "if field in tags")
                    found = 0
                    for tag in report[report_fields['tags']]:
                        writeLog('report_logs.txt', "Current tag: " + tag)
                        for tag_value in filter:
                            writeLog('report_logs.txt', "Tag value: " + tag_value)
                            if tag_value == tag:
                                writeLog('report_logs.txt', "Found tag " + tag)
                                found = found + 1
                    if found == len(filter):
                        cond[i] = cond[i] + 1
    
        res_reports = [report for i, report in enumerate(reports) if cond[i] == len(fields)]

    if searchAny:
        for i, report in enumerate(reports):
            found = False
            for field in text_fields:
                writeLog('report_logs.txt', "Query: " + fields["query"].lower())
                writeLog('report_logs.txt', "Field: " + field)
                writeLog('report_logs.txt', "Field content: " + report[field].lower())
                if fields["query"].lower() in report[field].lower():
                    found = True
                    writeLog('report_logs.txt', "Found!")

            if found:
                res_reports.append(report)

    return res_reports


def query(fields):

    reports = pd.read_csv("testdata/dummy_reports.csv", index_col=0)

    # Converting DataFrame to list of records
    reports_entries = convertReports(reports)

    # Filter list

    filtered_reports = filterReports(reports_entries, fields, False)
    
    return filtered_reports


def searchInReports(fields):

    reports = pd.read_csv("testdata/dummy_reports.csv", index_col=0)

    # Converting DataFrame to list of records
    reports_entries = convertReports(reports)

    # Filter list

    filtered_reports = filterReports(reports_entries, fields, True)

    return filtered_reports


def getTags(filter):

    result = [tag for tag in samples.tags if filter.lower() in tag.lower()]

    return result


def writeLog(path, obj):
    date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(path, "a") as logfile:
        logfile.write(date_time + ":" + str(obj) + "\n")