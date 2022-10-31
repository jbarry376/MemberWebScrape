# directory_tool.py

# Import the argparse library
import argparse

import re

import requests

from bs4 import BeautifulSoup
import pandas as pd 


# Create the parser
my_parser = argparse.ArgumentParser(description='Get Member info from Directory')

# argument for webaddress
my_parser.add_argument('-w', '--web-address', help = "Web Address to Parse")
# argument for saving the results 
my_parser.add_argument('-o', '--output', default='member_directory.csv',
                    help='Output file to write member directory to')
# argument for not including phone numbers 
my_parser.add_argument('--no-phone', required = False, default = False, 
                    action='store_true', help = 'Optional : Exclude Phone Numbers')
# argument for not including address
my_parser.add_argument('--no-address', required = False, default = False,
                    action ='store_true', help = 'Optional : Exclude Addresses')

# Execute the parse_args() method
args = my_parser.parse_args()



# helper functions for processing phone numbers and addresses 
def _get_phone(s: str) -> str: 
    """take member string from web results -> return phone number if it's there"""
    # pattern ddd-ddd-dddd or (ddd) ddd-dddd
    pattern = "(\d{3}-\d{3}-\d{4})|(\([^\d]*(\d+)[^\d]*\) \d{3}-\d{4})"
    res = re.search(pattern, s)
    try: 
        return res.group(0)
    except: 
        return None

def _get_addr(s :str) -> str:
    """take member string from web, match regex, return address string"""
    res = re.search("\d+ .* \d{5}", s)
    try:
        return res.group(0)
    except:
        return None


# Create WebScrapping Request 
URL = args.web_address

page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

# find chamber member divisions in contents-soup 
chamber_members = soup.find_all("div", {"class" : "card-body gz-directory-card-body"})
members = [r.get_text().strip() for r in chamber_members]

m = [re.sub("[\\n+]+", "\t", m) for m in members]
df = pd.DataFrame({"member" : m})

# parse member features and drop member column 
df['member_name'] = df['member'].apply(lambda s : s.split("\t")[0])
df['phone_number'] = df['member'].apply(lambda x : _get_phone(x))
df['address'] = df['member'].apply(lambda x : _get_addr(x))
df = df.drop('member', axis = 1)



if args.no_phone: 
    df = df.drop(['phone_number'], axis = 1)
if args.no_address: 
    df = df.drop(['address'], axis = 1)

print('Preview of Member Data: ')
print(df.head(3))


df.to_csv(args.output)