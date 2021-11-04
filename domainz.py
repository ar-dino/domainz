
import requests
import time
import json

api_key= open(f'../api_key.txt').read().strip()
secret_key= open(f'../api_secret.txt').read().strip()
headers = {"Authorization" : "sso-key {}:{}".format(api_key, secret_key)}
 
# Domain availability and appraisal end points
url = "https://api.godaddy.com/v1/domains/available"
appraisal = "https://api.godaddy.com/v1/appraisal/{}"
 

do_appraise = True
chunk_size = 500
max_length = 30

min_price = 0
max_price = 5000
min_appr_price = 0
 

min_sale_price = 0
min_sale_year = 2000
 
prefixes = []
keywords = []
suffixes = []
extensions = []
 
all_domains = []
similar_domains = []
found_domains = {}
 
with open("keyword.txt") as f:
   keywords = f.read().splitlines()
with open("extension.txt") as f:
   extensions = f.read().splitlines()
 
# Generate domains

for keyword in keywords:
    for extension in extensions:
        domain = "{}.{}".format(keyword,extension)
        # Filter by length
        if len(domain) <= max_length:
            all_domains.append(domain)
 
# This function splits all domains into chunks
# of a given size
def chunks(array, size):
   for i in range(0, len(array), size):
      yield array[i:i + size]
# Split the original array into subarrays
domain_chunks = list(chunks(all_domains, chunk_size))
 
# For each domain chunk (ex. 500 domains)
for domains in domain_chunks:
   # Get availability information by calling availability API
   availability_res = requests.post(url, json=domains, headers=headers)
   # Get only available domains with price range
   for domain in json.loads(availability_res.text)["domains"]:
      if domain["available"]:
         price = float(domain["price"])/1000000
         if price >= min_price and price <= max_price:
            print("{:30} : {:10}".format(domain["domain"], price))
            found_domains[domain["domain"]]=price
   print("-----------------------------------------------")
   time.sleep(2)
 
if not do_appraise:
   exit()
for domain, price in found_domains.items():
   
   appraisal_res = requests.get(appraisal.format(domain), headers=headers).json()
   try:   
      govalue = appraisal_res["govalue"]
      comparable_sales = appraisal_res["comparable_sales"]
   except:
      print(appraisal_res)
      continue
   if govalue >= min_appr_price:
      print("{:30} : {:10} : {}".format(domain, price, govalue))
#    for sale in comparable_sales:
#       # Filter similar sold domains by price and year
#       if sale["price"] >= min_sale_price and sale["year"] >= min_sale_year:
#          similar_domain = "{:30} : {:10} : {:10}".format(
#             sale["domain"], sale["price"], sale["year"])
#          # Do not include duplicates
#          if similar_domain not in similar_domains:
#             similar_domains.append(similar_domain)
   # Do not abuse the API
   time.sleep(2)
 
# Print similar sold domains
print("--------------------------------------------------------")
for domain in similar_domains:
   print(domain)
print("--------------------------------------------------------")