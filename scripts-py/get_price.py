import datetime
import requests
import json
import pandas as pd

testlimit = "1668038400"
timenow = 1668067247
query = """
           {
  priceFeeds(where:{tokenSymbol:"BTC",timestamp_lt : %s, timestamp_gt : 1668038400},orderBy:timestamp,orderDirection:desc){
    tokenPrice
    timestamp
  }
}
    """ % (timenow)
print(datetime.datetime.fromtimestamp(int(timenow)))
url = 'http://localhost:4000/graphql'
r = requests.post(url, json={'query': query})
json_data = json.loads(r.text)
df_data = json_data['data']['priceFeeds']
df = pd.DataFrame(df_data)
print(datetime.datetime.fromtimestamp(int(df_data[-1]['timestamp']))) 
print(df_data)
