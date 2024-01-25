import pytz
pst = pytz.timezone('America/Los_Angeles')  # Pacific Standard Time

from app import db
from app.models.user import DailyScheduleData, LDAPUserData, EDStaff, ReportLDAPMappings
from app.utils.ldap_utils import UCILDAPLookup, ATTRIBUTES

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import datetime as dt

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

    def to_dataframe(self, username):
        """Converts records to a pandas DataFrame and does necessary conversions."""
        df = pd.DataFrame(self.records)

        # Convert to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        df['DateDetail'] = pd.to_datetime(df['DateDetail'])

        # Localize to PST
        df['DateDetail'] = df['DateDetail'].dt.tz_localize(pst, ambiguous='infer')

        # Convert Value to float
        df['Value'].replace('', np.nan, inplace=True)
        df['Value'] = df['Value'].astype(float)

        # Drop rows where 'Name' is empty or null
        df = df[df['Name'].astype(bool)]

        # Add the username to the DataFrame
        df['record_uploaded_by'] = username
        
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
        xml_records = df.to_dict(orient='records')
        
        # Create instances of DailyScheduleData and add to session
        for record in xml_records:
            entry = DailyScheduleData(**record)
            db.session.add(entry)
        
        # Commit the session to save data to the database
        db.session.commit()


        #next, lets check the names 
        employees = df['name'].unique().tolist()

         # Update ldap_user_data
        for employee_name in employees:
            try:
                self.ldap_update(employee_name)  # Use 'self' to call the method from the same class
            except Exception as e:
                current_app.logger.error(f"LDAP update error for {employee_name}: {str(e)}")


    def delete_existing_db_records(self, date):
        # Delete existing records with the given date
        db.session.query(DailyScheduleData).filter(DailyScheduleData.date == date).delete()
        db.session.commit()


    def check_date_exists(self, date):
        """Check if a given date already exists in the database."""
        exists = db.session.query(
            db.exists().where(DailyScheduleData.date == date)
        ).scalar()
        return exists
    
    def ldap_update(self, full_name):
        """
        Attempts to associate a username to new staff records by cross-referencing first and last name via the LDAP system,
        this looks for staff listed under ED only.
        """
        ldap_lookup = UCILDAPLookup()
        result_df = ldap_lookup.name_lookup(full_name)

        current_time = dt.datetime.utcnow()
        
        if result_df.empty: # If the LDAP search returned no results 
            existing_staff = EDStaff.query.filter_by(displayname=full_name).first()
            
            #check if the full_name pulled from the report already exists in the ed_staff table
            if existing_staff: # If the full_name already exists, just update the update_date
                existing_staff.update_date = current_time
            else: # If no such staff exists, create a new one and insert now for creation date and update date
                new_staff = EDStaff(displayname=full_name, initial_creation_date=current_time, update_date=current_time)
                db.session.add(new_staff)

        else:  # If the LDAP search returned results
            for _, row in result_df.iterrows():
                # Create a dictionary for the LDAPUserData record
                ldap_record = {attr: row[attr] for attr in ATTRIBUTES if attr in row}
                # Check if the record already exists in the internal ldap_user_data table
                existing_user = LDAPUserData.query.filter_by(uid=ldap_record['uid']).first()
                # Also check to see if the full_name exists in the ed_staff table
                
                if not existing_user:
                    # If the record does not exist, create and add the new LDAPUserData record to the session
                    new_ldap_user = LDAPUserData(**ldap_record)
                    db.session.add(new_ldap_user)

                #Check to see if there is a report_ldap_mapping for the record
                existing_entry = ReportLDAPMappings.query.filter_by(full_name = full_name, uid = ldap_record.get('uid', None)).first()

                if existing_entry: # If the entry exists with a blank UID, update it
                    if existing_entry.uid is None:
                        existing_entry.uid = ldap_record.get('uid')
                else: # If no such entry exists, create a new one
                    new_entry = ReportLDAPMappings(full_name = full_name, uid = ldap_record.get('uid'))
                    db.session.add(new_entry)

                #Check to see if the user_staff table has a record with the full_name string in it
                ed_staff_existing_user = EDStaff.query.filter_by(displayname = full_name).first()
                
                if ed_staff_existing_user: #If there is a a record that has a full_name exactly matching the report value
                    #check to see if there is a value associated with the username column for that record
                    existing_username = ed_staff_existing_user.username
                                               
                    if existing_username is None: #if there is no value available under the username then update it with the uid
                         ed_staff_existing_user.username = ldap_record.get('uid')

                else: #if there is no matching displayname then add the new record to the ed_staff table
                    new_ed_staff_user = EDStaff(
                        displayname=full_name,
                        username=ldap_record.get('uid', None),
                        initial_creation_date = current_time,
                        update_date =  current_time
                    )

                    db.session.add(new_ed_staff_user)

        # Commit the session to save all new records to the database
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback the changes on error
            current_app.logger.error(f"Error updating LDAPUserData: {str(e)}")
            raise  # Optionally re-raise the exception or handle it as needed


if __name__ == "__main__":
    parser = XMLParser('app/uploads/Daily Roster by Shift.xml')
    parser.parse_xml()
    df = parser.to_dataframe()

    # Get a list of distinct codes abstracted from the xml file
    distinct_shift_codes = df[['Code']].drop_duplicates()


    df.to_csv('.output.csv', index=False)


