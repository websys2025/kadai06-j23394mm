import requests
import pandas as pd

APP_ID = "d4c8a684d3eeaa7950288bbdbe19ff792c1d5479"  # 自分のアプリケーションID
API_URL  = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"  # エンドポイント

# コロナ前後で家計動向にどのような影響があったのか
params = {
    "appId": APP_ID,
    "statsDataId":"0003348425",  # 景気ウォッチャー調査の分野・業種別DI
    "cdTime": "2024000909,2023000909,2022000909,2021000909,2020000909,2019000909,2018000909",  # 年月: 2024年から2018年までの9月
    "cdCat01": "110,120,180,200,320,370,380",  # 分野: 家計動向関連、家計動向関連_小売関連、家計動向関連_小売関連_スーパー、家計動向関連_小売関連_コンビニエンスストア、家計動向関連_飲食関連、家計動向関連_サービス関連、家計動向関連_サービス関連_旅行・交通関連
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
