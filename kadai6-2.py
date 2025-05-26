import requests
import pandas as pd

APP_ID = "d4c8a684d3eeaa7950288bbdbe19ff792c1d5479"  # 自分のアプリケーションID
API_URL  = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"  # エンドポイント

# 国土交通省のオープンデータから、政府統計ポータルサイトであるe-StatのAPIを参照
    # e-Stat: 総務省が提供している、API機能が利用できるオープンデータ
    # 国土交通省 統計情報: 国土交通省が提供している、分野別のオープンデータ
# コロナ前後で自動車燃料消費量にどのような影響があったのか
params = {
    "appId": APP_ID,
    "statsDataId":"0003181460",  # 自動車燃料消費量調査の第１表 燃料別・車種別 総括表
    "cdTime": "2024000909,2023000909,2022000909,2021000909,2020000909,2019000909,2018000909",  # 年月: 2024年から2018年までの9月
    "cdCat01": "140,190,220",  # 車種: バス・乗用車、普通車、軽自動車
    "metaGetFlg":"Y",  # メタ情報を取得する
    "cntGetFlg":"N",  # 件数を取得しない
    "explanationGetFlg":"Y",  # 統計表や提供統計、提供分類、各事項の解説を取得する
    "annotationGetFlg":"Y",  # 数値データの注釈を取得する
    "sectionHeaderFlg":"1",  # セクションヘッダを出力する
    "replaceSpChars":"0",
    "lang": "J"  # 日本語を指定
}

response = requests.get(API_URL, params=params)
# Process the response
data = response.json()

# 統計データからデータ部取得
values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']

# JSONからDataFrameを作成
df = pd.DataFrame(values)

# メタ情報取得
meta_info = data['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']

# 統計データのカテゴリ要素をID(数字の羅列)から、意味のある名称に変更する
for class_obj in meta_info:

    # メタ情報の「@id」の先頭に'@'を付与した文字列が、統計データの列名と対応している
    column_name = '@' + class_obj['@id']

    # 統計データの列名を「@code」から「@name」に置換するディクショナリを作成
    id_to_name_dict = {}
    if isinstance(class_obj['CLASS'], list):
        for obj in class_obj['CLASS']:
            id_to_name_dict[obj['@code']] = obj['@name']
    else:
        id_to_name_dict[class_obj['CLASS']['@code']] = class_obj['CLASS']['@name']

    # ディクショナリを用いて、指定した列の要素を置換
    df[column_name] = df[column_name].replace(id_to_name_dict)

# 統計データの列名を変換するためのディクショナリを作成
col_replace_dict = {'@unit': '単位', '$': '値'}
for class_obj in meta_info:
    org_col = '@' + class_obj['@id']
    new_col = class_obj['@name']
    col_replace_dict[org_col] = new_col

# ディクショナリに従って、列名を置換する
new_columns = []
for col in df.columns:
    if col in col_replace_dict:
        new_columns.append(col_replace_dict[col])
    else:
        new_columns.append(col)

df.columns = new_columns
print(df)
