# AtcoderLocalAssistant

## 概要
AtCoderの問題を解く際に、ローカルでテストケースを実行するためのツールです。
user scriptと併用することで、ページを開いたときにテストケースをダウンロードし、コードを書いたあとにページ上でワンボタンでコードを反映、テスト、提出ができます。

また、VSCode上でもテストケースを実行できます。

## インストール
1. このリポジトリをクローンします。
2. Pythonのvenvとして、`flask`環境を作ります。
3. `flask`環境をactivateし、`pip install -r requirements.txt`を実行します。
4. タスク`atcoder_assistant_new.py`を実行します。
5. tampermonkeyなどで`atcoder_local_assistant.js`と、`atcoder_easy_test.js`をインストールします。
6. AtCoderの問題ページを開くと、テストケースが自動でダウンロードされます。
