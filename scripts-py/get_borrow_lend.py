import datetime
import requests
import json
import pandas as pd

testlimit = "1668038400"
timenow =1668303827
query = """
           {
  marketHourlySnapshots( orderBy: timestamp, orderDirection: desc, where: {timestamp_lt: %s ,market: "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",timestamp_gt:1668038400}){
    timestamp
    totalValueLockedUSD
    totalBorrowBalanceUSD
  }
}
    """ % (timenow)
print(datetime.datetime.fromtimestamp(int(timenow)))
url = 'http://localhost:4000/graphql'
r = requests.post(url, json={'query': query})
json_data = json.loads(r.text)
df_data = json_data['data']['marketHourlySnapshots']
df = pd.DataFrame(df_data)
print(datetime.datetime.fromtimestamp(int(df_data[-1]['timestamp']))) 
print(df_data)
