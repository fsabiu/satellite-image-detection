import ast
from datetime import datetime
import pandas as pd


# Dict DataFrame names -> JSON names
report_fields = {
    "title": "title",
    "desc": "description",
    "fromCoordx": "fromCoordsx",
    "fromCoordy": "fromCoordsy",
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

    return reports_entries


def query(fields):

    reports = pd.read_csv("testdata/dummy_reports.csv", index_col=0)


    # Filter DataFrame


    # Conversion to records
    reports_entries = convertReports(reports)
    
    return reports_entries
