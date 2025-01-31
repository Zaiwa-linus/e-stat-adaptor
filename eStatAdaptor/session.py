import pandas as pd
from .utils import fetch_stats_data, json_to_dataframe

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
        df.loc[df['value'].notna(), 'note'] = None
        return df


