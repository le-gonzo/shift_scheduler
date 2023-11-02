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

    def search(self, user_id):
        """Search for a specific user_id in the LDAP."""
        search_filter = f"(uid={user_id})"
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
    

if __name__ == "__main__":
    ldap_lookup = UCILDAPLookup()
    user_id = input("Enter UCINetId to search: ")
    result_df = ldap_lookup.uidlookup(user_id)
    ic(result_df.T)
