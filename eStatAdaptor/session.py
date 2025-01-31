import pandas as pd
from .utils import fetch_stats_data, json_to_dataframe,fetch_stats_list

class Session:
    """
    統計データ取得のためのセッションを管理するクラス。
    """

    def __init__(self, api_key):
        """
        インスタンスを初期化し、APIキーを保存します。

        :param api_key: e-Stat APIのアプリケーションID
        """
        if not api_key:
            raise ValueError("APIキーは必須です。")
        self.api_key = api_key

    def getData(self, stats_data_id) -> pd.DataFrame:
        """
        統計データIDを使用してデータを取得します。

        :param stats_data_id: 統計表表示ID
        :return: Pandas DataFrame形式のデータ
        """
        if not stats_data_id:
            raise ValueError("統計データIDは必須です。")

        # APIを呼び出してJSONデータを取得
        try:
            json_data = fetch_stats_data(self.api_key, stats_data_id)
        except RuntimeError as e:
            raise RuntimeError(f"データ取得中にエラーが発生しました: {e}")
        
        # JSONデータの中身を確認し、200以外の応答がある場合はエラーを示す
        result = json_data.get('GET_STATS_DATA', {}).get('RESULT', {})
        if result.get('STATUS') != 0:
            error_msg = result.get('ERROR_MSG', '不明なエラーが発生しました。')
            raise RuntimeError(f"APIエラー: {error_msg}")

        # JSONデータをDataFrameに変換
        try:
            df = json_to_dataframe(json_data)
        except ValueError as e:
            raise ValueError(f"データフレーム変換中にエラーが発生しました: {e}")
        
        # dfに値を付与し返す
        df['note'] = df['value'].copy()
        # Ensure 'value' column contains only numeric values
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['value'] = df['value'].astype(float)
        if df['value'].apply(lambda x: float(x).is_integer()).all():
            df['value'] = df['value'].astype(int)
        
        # 数値が入っている行のnoteを削除
        df.loc[df['value'].notna(), 'note'] = '-'
        return df


    def searchReports(self, search_word: str, survey_year: str = None, limit: int = 10,show_full:bool = False) -> pd.DataFrame:
        """
        指定したキーワードで統計帳票を検索し、該当する統計表を取得する。

        :param search_word: 検索キーワード
        :param survey_year: 調査年度 (例: "2023") (オプション)
        :param limit: 取得件数の上限 (デフォルト: 10)
        :return: 検索結果の統計表一覧 (Pandas DataFrame)
        """
        if not search_word:
            raise ValueError("検索キーワードは必須です。")

        # APIを呼び出してJSONデータを取得
        try:
            json_data = fetch_stats_list(self.api_key, search_word, survey_year, limit)
        except RuntimeError as e:
            raise RuntimeError(f"帳票検索中にエラーが発生しました: {e}")

        # 結果の確認
        result = json_data.get('GET_STATS_LIST', {}).get('RESULT', {})
        if result.get('STATUS') != 0:
            error_msg = result.get('ERROR_MSG', '不明なエラーが発生しました。')
            raise RuntimeError(f"APIエラー: {error_msg}")

        # 帳票データのリストを抽出
        table_info = json_data.get('GET_STATS_LIST', {}).get('DATALIST_INF', {}).get('TABLE_INF', [])

        if not table_info:
            raise ValueError("該当する統計帳票が見つかりませんでした。")

        # JSONデータをPandas DataFrameに変換
        df = pd.DataFrame(table_info)
 
        # 統計名を取得しやすい形に変換
        df['STAT_NAME'] = df['STAT_NAME'].apply(lambda x: x['$'] if isinstance(x, dict) else x)
        df['GOV_ORG'] = df['GOV_ORG'].apply(lambda x: x['$'] if isinstance(x, dict) else x)
        df['MAIN_CATEGORY'] = df['MAIN_CATEGORY'].apply(lambda x: x['$'] if isinstance(x, dict) else x)
        df['SUB_CATEGORY'] = df['SUB_CATEGORY'].apply(lambda x: x['$'] if isinstance(x, dict) else x)



        # STATISTICS_NAME_SPECを列に展開
        statistics_name_spec_columns = ['TABULATION_CATEGORY', 'TABULATION_SUB_CATEGORY1', 'TABULATION_SUB_CATEGORY2']
        for col in statistics_name_spec_columns:
            df[col] = df['STATISTICS_NAME_SPEC'].apply(lambda x: x.get(col) if isinstance(x, dict) else None)
        # STATISTICS_NAME_SPEC列を削除
        df = df.drop(columns=['STATISTICS_NAME_SPEC'])

        # TITLE_SPECを列に展開
        title_spec_columns = ['TABLE_CATEGORY', 'TABLE_NAME', 'TABLE_EXPLANATION']
        for col in title_spec_columns:
            df[col] = df['TITLE_SPEC'].apply(lambda x: x.get(col) if isinstance(x, dict) else None)
        # TITLE_SPEC列を削除
        df = df.drop(columns=['TITLE_SPEC'])

        df['TITLE'] = df['TITLE'].apply(lambda x: x['$'] if isinstance(x, dict) else x)

        # 統計名を取得しやすい形に変換
        df['STAT_NAME'] = df['STAT_NAME'].apply(lambda x: x['value'] if isinstance(x, dict) else x)

        df = df.rename(columns={"@id": "STATS_DATA_ID"})

        if show_full:
            return df

        selected_columns = ["STATS_DATA_ID",  "STAT_NAME","SURVEY_DATE", "GOV_ORG", "STATISTICS_NAME", "TITLE"]
        df = df[selected_columns]

        return df
