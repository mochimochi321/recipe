import requests
import json
import time
import pandas as pd
from pprint import pprint

# 1. 楽天レシピのレシピカテゴリ一覧を取得する

res = requests.get('https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?applicationId=1044994305728423696')

json_data = json.loads(res.text)

parent_dict = {} # mediumカテゴリの親カテゴリの辞書

df = pd.DataFrame(columns=['category1','category2','category3','categoryId','categoryName'])

# データを一時保存するリスト
rows = []

# 大カテゴリ
for category in json_data['result']['large']:
    rows.append({
        'category1': category['categoryId'],
        'category2': "",
        'category3': "",
        'categoryId': category['categoryId'],
        'categoryName': category['categoryName']
    })

# 中カテゴリ
for category in json_data['result']['medium']:
    rows.append({
        'category1': category['parentCategoryId'],
        'category2': category['categoryId'],
        'category3': "",
        'categoryId': f"{category['parentCategoryId']}-{category['categoryId']}",
        'categoryName': category['categoryName']
    })
    parent_dict[str(category['categoryId'])] = category['parentCategoryId']

# 小カテゴリ
for category in json_data['result']['small']:
    parent2 = str(category['parentCategoryId'])  # 中カテゴリID
    parent1 = parent_dict.get(parent2)           # 大カテゴリID
    if parent1:
        child = str(category['categoryId'])
        rows.append({
            'category1': parent1,
            'category2': parent2,
            'category3': child,
            'categoryId': f"{parent1}-{parent2}-{child}",
            'categoryName': category['categoryName']
        })

# 最後にまとめてDataFrameに変換
df = pd.DataFrame(rows)

print("材料名")
key = input().strip()

# 2. キーワードからカテゴリを抽出する
df_keyword = df[df['categoryName'].str.contains(key, na=False)]

# 3. 人気レシピを取得する
df_recipe = pd.DataFrame(columns=['recipeId', 'recipeTitle', 'foodImageUrl', 'recipeMaterial', 'recipeCost', 'recipeIndication', 'categoryId', 'categoryName', 'recipeUrl'])

# 3. 人気レシピを取得する
recipe_rows = []

for index, row in df_keyword.iterrows():
    time.sleep(3)  # アクセスマナー

    url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1044994305728423696&categoryId='+row['categoryId']
    res = requests.get(url)
    json_data = json.loads(res.text)
    
    # エラー回避のため、'result' が存在するか確認
    if 'result' not in json_data:
        continue
    
    recipes = json_data['result']

    for recipe in recipes:
        recipe_rows.append({
            'recipeId': recipe['recipeId'],
            'recipeTitle': recipe['recipeTitle'],
            'foodImageUrl': recipe['foodImageUrl'],
            'recipeMaterial': recipe['recipeMaterial'],
            'recipeCost': recipe['recipeCost'],
            'recipeIndication': recipe['recipeIndication'],
            'categoryId': row['categoryId'],
            'categoryName': row['categoryName'],
            'recipeUrl':recipe['recipeUrl']
        })

# append の代わりに最後に DataFrame 化
df_recipe = pd.DataFrame(recipe_rows)


# 4. 材料名が含まれるレシピのみを抽出
df_filtered = df_recipe[df_recipe['recipeMaterial'].apply(lambda x: any(key in m for m in x))]

# 結果を表示
print("🔍 材料にキーワードが含まれるレシピ一覧：\n")
print(f"{df_filtered[['recipeTitle', 'recipeMaterial', 'recipeUrl']]}\n")
