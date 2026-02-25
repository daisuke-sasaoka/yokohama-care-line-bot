# Yokohama Care LINE Bot

横浜市の介護相談窓口を案内するLINEボットです。

## 機能

- 横浜市の区名を検出
- 介護関連キーワードを判定
- 該当区の窓口情報を自動返信

## 使用技術

- Python
- FastAPI
- LINE Messaging API
- ngrok

## 起動方法

```bash
uvicorn main:app --reload --port 8000
