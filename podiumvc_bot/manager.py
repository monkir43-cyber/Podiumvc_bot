# manager.py
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data/player_data.json"

class PlayerData:
    def __init__(self):
        # データ読み込み
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ========================
    # コイン管理
    # ========================
    def get_coins(self, user_id: int) -> int:
        return self.data.get(str(user_id), {}).get("coins", 0)

    def add_coins(self, user_id: int, amount: int):
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {}
        self.data[uid]["coins"] = self.get_coins(user_id) + amount
        self.save()

    def remove_coins(self, user_id: int, amount: int) -> bool:
        """コインを減らす。足りなければFalseを返す"""
        current = self.get_coins(user_id)
        if current < amount:
            return False
        self.data[str(user_id)]["coins"] = current - amount
        self.save()
        return True

    # ========================
    # デイリーボーナス管理
    # ========================
    def claim_daily(self, user_id: int) -> bool:
        """1日1回のみ Trueなら受け取り成功"""
        uid = str(user_id)
        today = datetime.utcnow().date().isoformat()
        if uid not in self.data:
            self.data[uid] = {}

        last_claim = self.data[uid].get("last_daily", "")
        if last_claim == today:
            return False

        self.data[uid]["last_daily"] = today
        self.add_coins(user_id, 20)  # デイリーボーナス20コイン
        return True


# インスタンスを1つ作って使い回す
player_data = PlayerData()
