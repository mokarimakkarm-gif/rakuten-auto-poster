# メール通知設定ガイド

このドキュメントでは、GitHub ActionsからGmailへのメール通知を設定する手順を説明します。

## 📋 必要な準備

### 1. Gmailアカウントの準備
- Gmailアカウントが必要です（mokari.makka.rm@gmail.com）
- 2段階認証を有効にしてください

### 2. Googleアプリパスワードの生成

**ステップ1: Google Account Securityにアクセス**
1. https://myaccount.google.com/security にアクセス
2. 左メニューから「Security」をクリック
3. 「2-Step Verification」が有効になっていることを確認

**ステップ2: アプリパスワードを生成**
1. 「App passwords」をクリック
2. 「Select app」で「Mail」を選択
3. 「Select device」で「Windows Computer」（または使用デバイス）を選択
4. 「Generate」をクリック
5. 生成されたパスワードをコピー（16文字）

### 3. OAuth認証情報の取得

**ステップ1: Google Cloud Consoleにアクセス**
1. https://console.cloud.google.com にアクセス
2. 新しいプロジェクトを作成（例: "rakuten-auto-poster"）

**ステップ2: Gmail APIを有効化**
1. 「APIs & Services」 → 「Library」をクリック
2. 「Gmail API」を検索
3. 「Enable」をクリック

**ステップ3: OAuth 2.0認証情報を作成**
1. 「APIs & Services」 → 「Credentials」をクリック
2. 「Create Credentials」 → 「OAuth client ID」をクリック
3. 「Application type」で「Desktop application」を選択
4. 「Create」をクリック
5. 「Client ID」と「Client Secret」をコピー

**ステップ4: リフレッシュトークンを取得**

以下のPythonスクリプトを実行:

```python
from google.auth.transport.requests import Request
from google.oauth2.service_account import ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

print("Refresh Token:", creds.refresh_token)
```

## 🔐 GitHubシークレットの設定

### ステップ1: GitHubリポジトリにアクセス
1. https://github.com/mokarimakkarm-gif/rakuten-auto-poster にアクセス
2. 「Settings」をクリック
3. 左メニューから「Secrets and variables」 → 「Actions」をクリック

### ステップ2: シークレットを追加

以下の3つのシークレットを追加してください:

| シークレット名 | 値 | 説明 |
|-------------|-----|------|
| `NOTIFICATION_EMAIL` | mokari.makka.rm@gmail.com | 通知先メールアドレス |
| `GMAIL_CLIENT_ID` | (Google Consoleから取得) | Gmail API Client ID |
| `GMAIL_CLIENT_SECRET` | (Google Consoleから取得) | Gmail API Client Secret |
| `GMAIL_REFRESH_TOKEN` | (上記スクリプトで取得) | Gmail リフレッシュトークン |

**追加手順:**
1. 「New repository secret」をクリック
2. 「Name」に上記の名前を入力
3. 「Secret」に値をペースト
4. 「Add secret」をクリック

## 📧 メール通知の種類

### 1. 投稿完了通知
- **トリガー**: 毎日日本時間12時に投稿完了時
- **内容**: 投稿件数、成功/失敗、詳細リンク
- **例**:
  ```
  ✅ 楽天ROOM投稿完了 - 2026-02-04T12:00:00Z
  
  本日の楽天ROOM投稿が完了しました。
  
  実行時刻: 2026-02-04T12:00:00Z
  ワークフロー: 楽天ROOM自動投稿
  ステータス: 成功 ✅
  ```

### 2. 投稿失敗通知
- **トリガー**: 投稿に失敗した場合
- **内容**: エラー内容、ログリンク
- **例**:
  ```
  ❌ 楽天ROOM投稿失敗 - 2026-02-04T12:00:00Z
  
  本日の楽天ROOM投稿に失敗しました。
  ログを確認して対応してください。
  ```

### 3. API変更検出通知
- **トリガー**: 楽天市場のページ構造が変更された場合
- **内容**: 変更内容、確認リンク
- **例**:
  ```
  🚨 楽天市場API変更検出アラート
  
  楽天市場のページ構造が変更されました。
  スクリプトの確認と修正が必要です。
  ```

### 4. セキュリティ更新通知
- **トリガー**: Dependabotがセキュリティ脆弱性を検出した場合
- **内容**: パッケージ名、バージョン、重要度
- **例**:
  ```
  🔒 セキュリティ更新が利用可能です
  
  パッケージ: beautifulsoup4
  現在のバージョン: 4.9.3
  新しいバージョン: 4.12.0
  重要度: 高
  ```

## 🧪 テスト実行

### メール通知のテスト
1. GitHub Actions実行ページにアクセス
2. 「楽天ROOM自動投稿」ワークフローをクリック
3. 「Run workflow」をクリック
4. 「Run workflow」ボタンをクリック
5. 実行完了後、メールを確認

### API変更検出のテスト
1. 「楽天市場API変更検出」ワークフローをクリック
2. 「Run workflow」をクリック
3. 「Run workflow」ボタンをクリック
4. 実行完了後、メールを確認

## 🔧 トラブルシューティング

### メールが届かない場合

**1. Gmailのセキュリティ設定を確認**
- https://myaccount.google.com/security にアクセス
- 「Less secure app access」が有効になっているか確認

**2. シークレットが正しく設定されているか確認**
- GitHub Settings → Secrets を確認
- 値が正しくコピーされているか確認

**3. ワークフロー実行ログを確認**
- GitHub Actions実行ページでエラーメッセージを確認

### 認証エラーが発生する場合

**1. リフレッシュトークンを再生成**
- 上記のPythonスクリプトを再実行
- 新しいトークンをシークレットに設定

**2. Googleアプリパスワードをリセット**
- Google Account Securityで新しいパスワードを生成
- シークレットを更新

## 📞 サポート

問題が発生した場合は、以下を確認してください:

1. GitHub Actions実行ログ
2. Gmailのセキュリティ設定
3. シークレットの設定値
4. Google Cloud Consoleの設定

## 📚 参考リンク

- [Gmail API Documentation](https://developers.google.com/gmail/api/guides)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Console](https://console.cloud.google.com)
- [Gmail Security](https://myaccount.google.com/security)
