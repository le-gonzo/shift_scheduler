from app import db 
from app.models.user import DailyScheduleData, Location, Assignment, ShiftTemplate

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from icecream import ic

from flask import current_app

#from config import DB_CONFIG 


class XMLParser:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.namespace = {'ns': 'Daily_x0020_Roster_x0020_by_x0020_Shift'}
        self.records = []

    def _extract_detail(self, detail_element):
        """Extracts details from the XML's 'Detail' element."""
        # Format the extracted date to match PostgreSQL's date format
        formatted_date = pd.to_datetime(self.date).strftime('%Y-%m-%d')
        return {
            'Date': formatted_date, # Use the formatted date
            'Entity': self.entity,
            'Coverage Period': self.coverage_period,
            'Department': self.department,
            'DateDetail': detail_element.get('textbox47', ''),
            'Name': detail_element.get('textbox37', ''),
            'Role': detail_element.get('textbox38', ''),
            'Contact': detail_element.get('textbox39', ''),
            'Code': detail_element.get('textbox40', ''),
            'Value': detail_element.get('Textbox4', '')
        }
    
    def parse_xml(self):
        #TODO:  No guerentee this stuff will stay the same, will need to come up with a way to detect and record xml schema
        #       - implement schema detection
        #       - introduce versioning
        #       - Create translators per version
        #       - archive old schema
        #       - setup notification system
        #       - setup a fallback mechanism
        #       - document everything
        """Parses the XML file and populates the records list."""
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        for trunk in root.findall(".//ns:table1_TrunkOrganizationUnitCode", self.namespace):
            self.date = trunk.get("textbox56").split("Date: ")[-1].strip()
            self.entity = trunk.get("textbox62").split("Entity: ")[-1].strip()

            for leaf in trunk.findall(".//ns:table1_LeafOrganizationUnitCode_CoverageCode", self.namespace):
                self.coverage_period = leaf.get("textbox175", "").split("Coverage Period: ")[-1].strip()

                for department_detail in leaf.findall(".//ns:table1_CoveragePeriodCode_Leaf", self.namespace):
                    self.department = department_detail.get("textbox257").split("Department: ")[-1].strip()

                    for detail in department_detail.findall(".//ns:Detail", self.namespace):
                        record = self._extract_detail(detail)
                        self.records.append(record)

    def to_dataframe(self):
        """Converts records to a pandas DataFrame and does necessary conversions."""
        df = pd.DataFrame(self.records)

        # Convert to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        df['DateDetail'] = pd.to_datetime(df['DateDetail'])

        # Convert Value to float
        df['Value'].replace('', np.nan, inplace=True)
        df['Value'] = df['Value'].astype(float)

        # Drop rows where 'Name' is empty or null
        df = df[df['Name'].astype(bool)]
        
        columns_list = df.columns.tolist()
        current_app.logger.info(f'xml file parsed into the follow columns: {columns_list}')

        # Rename columns to match the model
        df.rename(columns={
            'Date': 'date',
            'Entity': 'entity',
            'Coverage Period': 'coverage_period',
            'Department': 'department',
            'DateDetail': 'date_detail',
            'Name': 'name',
            'Role': 'role',
            'Contact': 'contact',
            'Code': 'code',
            'Value': 'value'
        }, inplace=True)

        return df
    
    def to_database(self, df):
        """Save DataFrame to the DailyScheduleData table."""
        
        # Convert DataFrame to a list of dictionaries
        records = df.to_dict(orient='records')
        
        # Create instances of DailyScheduleData and add to session
        for record in records:
            entry = DailyScheduleData(**record)
            db.session.add(entry)
        
        # Commit the session to save data to the database
        db.session.commit()


if __name__ == "__main__":
    parser = XMLParser('app/uploads/Daily Roster by Shift.xml')
    parser.parse_xml()
    df = parser.to_dataframe()

    # Get a list of distinct codes abstracted from the xml file
    distinct_shift_codes = df[['Code']].drop_duplicates()
    ic(distinct_shift_codes)


    df.to_csv('.output.csv', index=False)


