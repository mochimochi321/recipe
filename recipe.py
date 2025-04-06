import requests
import json
import pandas as pd

res = requests.get('https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?applicationId=1044994305728423696')
json_data = json.loads(res.text)

# mediumカテゴリの親カテゴリの辞書
parent_dict = {}

# データを一時的に格納するリスト
data = []

# 大カテゴリ
for category in json_data['result']['large']:
    data.append({
        'category1': category['categoryId'],
        'category2': "",
        'category3': "",
        'categoryId': category['categoryId'],
        'categoryName': category['categoryName']
    })

# 中カテゴリ
for category in json_data['result']['medium']:
    data.append({
        'category1': category['parentCategoryId'],
        'category2': category['categoryId'],
        'category3': "",
        'categoryId': f"{category['parentCategoryId']}-{category['categoryId']}",
        'categoryName': category['categoryName']
    })
    parent_dict[str(category['categoryId'])] = category['parentCategoryId']

# 小カテゴリ
for category in json_data['result']['small']:
    parent1 = parent_dict[category['parentCategoryId']]
    parent2 = category['parentCategoryId']
    child = category['categoryId']
    data.append({
        'category1': parent1,
        'category2': parent2,
        'category3': child,
        'categoryId': f"{parent1}-{parent2}-{child}",
        'categoryName': category['categoryName']
    })

# 最後にDataFrameに変換
df = pd.DataFrame(data)

# 確認（必要に応じて）
print(df.head())
