import re
import pandas as pd
from ldap3 import Server, Connection, SUBTREE
from icecream import ic

LDAP_SERVER = 'ldaps://ldap.oit.uci.edu:636'
BASE_DN = "dc=uci,dc=edu"
ATTRIBUTES = [
        'uciUCNetID', 'uid', 'uciCampusID', 'displayName', 'sn',
        'givenName', 'middleName', 'uciPublishedTitle1', 'uciAffiliation',
        'uciPrimaryDepartmentCode', 'uciPrimaryDepartment',
        'uciLevel3DepartmentDescription', 'ou', 'uciMailDeliveryPoint',
        'uciPublishedOfficeAddress1', 'uciPublishedDepartment1'
        ]

class UCILDAPLookup:
    """Class to perform UCINetId lookup using LDAP connection."""
    
    def __init__(self, ldap_server=LDAP_SERVER, base_dn=BASE_DN, attributes=ATTRIBUTES):
        self.ldap_server = ldap_server
        self.base_dn = base_dn
        self.attributes = attributes
        self.server = Server(self.ldap_server, use_ssl=True)
        self.conn = Connection(self.server)

    def bind(self):
        """Bind to the LDAP server."""
        self.conn.bind()

    def unbind(self):
        """Unbind from the LDAP server."""
        self.conn.unbind()

    def search(self, user_id, search_key = 'uid'):
        """Search for a specific user_id in the LDAP."""
        search_filter = f"({search_key}={user_id})"
        self.conn.search(
            search_base=self.base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=self.attributes
        )

    def get_data_frame(self):
        """Construct a DataFrame from the LDAP search results."""
        if self.conn.entries:
            entry = self.conn.entries[0]
            data = {attr: [entry[attr].value] for attr in self.attributes if attr in entry}
            return pd.DataFrame(data)
        return pd.DataFrame(columns=self.attributes)

    def uidlookup(self, uid):
        """Lookup a uid (User ID) and return the results as a DataFrame."""
        self.bind()
        self.search(uid)
        df = self.get_data_frame()
        self.unbind()
        return df
    
    def ed_search_by_name(self, last_name, first_name_partial):
        """Search for a specific last name and partial first name in the LDAP."""
        # Construct the search filter for partial matching of givenName and exact matching of sn
        # uciPrimaryDepartment = Emergency Department
        search_filter = (
        f"(&"
        f"(sn=*{last_name}*)"
        f"(givenName=*{first_name_partial}*)"
        f"(uciPrimaryDepartment=Emergency Department)"
        f")"
        )

        self.conn.search(
            search_base=self.base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=self.attributes
        )
    
    
    def name_lookup(self, full_name):
        """Lookup by last name and partial first name and return the results as a DataFrame."""
        def _extract_simple_names(full_name):
            # Normalize the string (remove extra spaces, convert to the same case)
            full_name = re.sub(' +', ' ', full_name.strip().lower())
            
            # Split the name by the comma
            parts = [part.strip() for part in full_name.split(',', 1)]
            
            if len(parts) == 2:
                last_name, first_name = parts
                # Take the first part of the last name (before any spaces)
                last_name = last_name.split()[0]
                # Take the first part of the first name (before any spaces or hyphens)
                first_name = first_name.split()[0].split('-')[0]
            else:
                # For single part names (no commas), we assume it's a last name
                last_name = parts[0]
                first_name = ''
                
            return last_name.title(), first_name.title()

        # Extract the simplified last name and first name partial
        last_name, first_name_partial = _extract_simple_names(full_name)

        self.bind()
        self.ed_search_by_name(last_name, first_name_partial)
        df = self.get_data_frame()
        self.unbind()
        return df

if __name__ == "__main__":
    #ldap_lookup = UCILDAPLookup()
    #user_id = input("Enter UCINetId to search: ")
    #result_df = ldap_lookup.firstnamelookup(user_id)
    #ic(result_df.T)

    ldap_lookup = UCILDAPLookup()
    full_name = input("Enter the last name to search: ")
    result_df = ldap_lookup.name_lookup(full_name)
    ic(result_df.T)
