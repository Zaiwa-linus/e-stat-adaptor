# e-Stat API Data Retrieval Library

このライブラリは、日本のe-Stat APIから統計データを取得し、Pandas DataFrame形式で利用できるようにするためのシンプルなインターフェースを提供します。

## 特徴

- **簡単な操作性**: 必要な統計データIDを指定するだけでデータを取得可能。
- **Pandas DataFrame対応**: 取得データを直接DataFrame形式で操作できます。
- **エラー処理**: APIエラーやデータ変換エラーを明確に通知。



## インストール方法

以下のコマンドでご利用のpython環境にインストールしてください。

```bash
pip install git+https://github.com/Zaiwa-linus/e-stat-adaptor.git
```


## 使用方法

### 1. ライブラリのインポート

ライブラリをインポートし、`Session`クラスを使用します。

```python
from eStatAdaptor import Session
```

### 2. セッションの作成

e-Stat APIのアプリケーションIDを指定してセッションを初期化します。

```python
session = Session(api_key="your_api_key_here")
```

### 3. 統計データIDの検索

検索キーワードを指定して統計データIDを検索します。取得データはPandas DataFrameとして返されます。

```
search_word = "人口動態"
df_reports = session.searchReports(search_word)

print(df_reports)
```

検索時のオプションは以下の通りです：

| 引数名         | 型      | 必須 | 説明 |
|--------------|--------|----|--------------------------------|
| `search_word` | `str`  | ✅  | 検索キーワード（統計名、調査名など） |
| `survey_year` | `str`  | ❌  | 調査年度（例: `"2023"`、指定なしの場合は全期間） |
| `limit`       | `int`  | ❌  | 取得件数の上限（デフォルト: `10`） |
| `show_full`   | `bool` | ❌  | `True` にすると、詳細な情報を含む DataFrame を返す |



### 4. データの取得

統計データID (`stats_data_id`) を指定してデータを取得します。取得データはPandas DataFrameとして返されます。

```python
stats_data_id = "0003109201"  # 統計表表示IDの例
df = session.getData(stats_data_id)

print(df)
```

---

## エラー処理

以下のエラーが発生する可能性があります。それぞれの対処法を確認してください：

1. **APIキー未指定**

   ```python
   ValueError: APIキーは必須です。
   ```

   → 初期化時にAPIキーを指定してください。

2. **統計データID未指定**

   ```python
   ValueError: 統計データIDは必須です。
   ```

   → `getData` メソッドに適切な統計データIDを渡してください。

3. **データ取得エラー**

   ```python
   RuntimeError: データ取得中にエラーが発生しました: {エラーメッセージ}
   ```

   → APIのレスポンスを確認し、統計データIDやAPIキーが正しいことを確認してください。

4. **データ変換エラー**

   ```python
   ValueError: データフレーム変換中にエラーが発生しました: {エラーメッセージ}
   ```

   → JSONデータに問題がないか確認してください。

---

## 注意事項

1. **APIキーの管理**
   - APIキーは、環境変数や設定ファイルを使用して安全に管理してください。
2. **APIの利用制限**
   - e-Stat APIには利用制限があるため、大量のリクエストを送信する場合は注意してください。

---

## このライブラリの提供目的

このライブラリは主にデータ分析に関する学校教育などで用いることを想定しています。
データ取得時に躓きやすいAPIの理解を省き、APIを意識せずに直接pandas.DataFrameとしてデータを用意できる環境を提供することを目指しています。

不具合や機能追加のリクエストがありましたが、PRやXでコメントいただけますと幸いです。

なお、本ライブラリは非公式のものであり統計局とは一切関係ありませんが、
独立行政法人統計センター様よりご要望がある場合、本ライブラリをMITライセンスで公開の上全てのコードを提供いたします。