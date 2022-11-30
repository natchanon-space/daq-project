import datetime
import requests
import json
import pandas as pd

testlimit = "1668038400"
timenow = "1668125651"
query = """
            {
        liquidityPools( where:{id:"0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"}){
        inputTokens(first:2){
        symbol
        }
        totalValueLockedUSD,
        deposits(where:{timestamp_lt: %s, timestamp_gt:%s	},orderBy:timestamp,orderDirection:desc){
        amountUSD
        timestamp
        }
    }}
    """ % (timenow,testlimit)
print(datetime.datetime.fromtimestamp(int(timenow)))
url = 'http://localhost:4000/graphql'
r = requests.post(url, json={'query': query})
json_data = json.loads(r.text)
df_data = json_data['data']['liquidityPools'][0]['deposits']
df = pd.DataFrame(df_data)
print(datetime.datetime.fromtimestamp(int(df_data[-1]['timestamp']))) 
print(r.text)
print(df_data[-1]['timestamp'] <= testlimit)
