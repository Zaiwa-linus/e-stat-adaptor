import pandas as pd
import requests

def fetch_stats_data(app_id, stats_data_id):
    """
    e-Stat APIを使用して統計データを取得する関数

    :param app_id: e-Stat APIのアプリケーションID
    :param stats_data_id: 統計表表示ID
    :return: APIから取得したデータ（辞書形式）
    """
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    params = {
        "appId": app_id,
        "statsDataId": stats_data_id
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTPエラーがある場合は例外を発生
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching data: {e}")
    
def fetch_stats_list(app_id, search_word, survey_year=None, limit=10):
    """
    e-Stat APIを使用して統計帳票を検索する関数。

    :param app_id: e-Stat APIのアプリケーションID
    :param search_word: 検索キーワード
    :param survey_year: 調査年度（オプション, 例: "2023"）
    :param limit: 取得件数の上限（デフォルト: 10）
    :return: APIから取得したデータ（辞書形式）
    """
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"
    params = {
        "appId": app_id,
        "searchWord": search_word,
        "limit": limit
    }
    
    if survey_year:
        params["surveyYears"] = survey_year

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTPエラーがある場合は例外を発生
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching statistics list: {e}")

def json_to_dataframe(json_data):
    """
    JSONのVALUE部分を汎用的にPandas DataFrameに変換する関数。
    列名の順序を維持し、infoセクションを使って列名と値を変換。
    
    :param json_data: JSON形式のデータ
    :return: Pandas DataFrame
    """
    # VALUEフィールドを取得
    value_data = json_data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]

    # infoセクションを取得
    info = json_data["GET_STATS_DATA"]["STATISTICAL_DATA"].get("CLASS_INF", {}).get("CLASS_OBJ", [])

    # infoセクションからマッピングを構築
    column_mapping = {col["@id"]: col["@name"] for col in info if "@id" in col and "@name" in col}

    value_mappings = {}
    for col in info:
        if "@id" in col and "CLASS" in col:
            class_data = col["CLASS"]

            # CLASSが辞書型の場合、リストに変換
            if isinstance(class_data, dict):
                class_data = [class_data]

            # CLASSがリストである場合の処理
            if isinstance(class_data, list):
                value_mappings[col["@id"]] = {
                    entry["@code"]: entry["@name"]
                    for entry in class_data
                    if isinstance(entry, dict) and "@code" in entry and "@name" in entry
                }


    # 全ての列名を順序付きで収集
    all_columns = []
    for item in value_data:
        if not isinstance(item, dict):
            raise TypeError(f"Unexpected type in VALUE data: {type(item)}")
        for key in item.keys():
            if key not in all_columns:
                all_columns.append(key)


    # データフレームを作成し、欠損値はNaNで埋める
    try:
        df = pd.DataFrame([{col: item.get(col, None) for col in all_columns} for item in value_data], columns=all_columns)
    except Exception as e:
        raise ValueError(f"Error creating DataFrame: {e}")
    
    df.columns = [col.replace("@", "") for col in df.columns]



    # 列内の値をinfoセクションの対応に基づいて変換
    for col, mapping in value_mappings.items():
        if col in df.columns:
            try:
                df[col] = df[col].map(mapping).fillna(df[col])
            except Exception as e:
                raise ValueError(f"Error mapping values for column {col}: {e}")
    
    try:
        df.rename(columns=column_mapping, inplace=True)
    except Exception as e:
        raise ValueError(f"Error renaming columns: {e}")
    
    df.columns = [col.replace("$", "value") for col in df.columns]

    return df