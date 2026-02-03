#!/usr/bin/env python3
"""
楽天市場API変更検出スクリプト
ページ構造の変更を検出し、メール通知を送信
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging
import requests
from bs4 import BeautifulSoup

# ロギング設定
log_dir = Path(os.getenv('DATA_DIR', '.')) / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'api_detection_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 監視対象URL
MONITORING_URLS = {
    "ranking": "https://ranking.rakuten.co.jp/daily/",
    "search": "https://search.rakuten.co.jp/search/mall/",
}

# 重要なセレクタ
CRITICAL_SELECTORS = {
    "ranking": [
        "a.ranking-item",
        "span.price",
        "span.review-count",
        "span.rating",
    ],
    "search": [
        "a.item-name",
        "span.item-price",
        "span.item-review",
    ]
}

class APIChangeDetector:
    def __init__(self):
        self.data_dir = Path(os.getenv('DATA_DIR', '.')) / 'api-monitoring'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_file = self.data_dir / 'baseline.json'
        self.change_log_file = self.data_dir / 'changes.log'
        self.load_baseline()
    
    def load_baseline(self):
        """ベースラインを読み込む"""
        if self.baseline_file.exists():
            with open(self.baseline_file, 'r', encoding='utf-8') as f:
                self.baseline = json.load(f)
        else:
            self.baseline = {}
    
    def save_baseline(self):
        """ベースラインを保存"""
        with open(self.baseline_file, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, ensure_ascii=False, indent=2)
    
    def get_page_hash(self, url: str, selectors: list) -> Optional[str]:
        """ページの特定要素のハッシュを取得"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 指定されたセレクタから要素を抽出
            elements_text = ""
            for selector in selectors:
                elements = soup.select(selector)
                for elem in elements[:5]:  # 最初の5要素のみ
                    elements_text += elem.get_text(strip=True)
            
            # ハッシュを計算
            page_hash = hashlib.md5(elements_text.encode()).hexdigest()
            return page_hash
        
        except Exception as e:
            logger.error(f"ページ取得エラー ({url}): {str(e)}")
            return None
    
    def detect_changes(self) -> Dict:
        """API変更を検出"""
        changes = {
            "detection_time": datetime.now().isoformat(),
            "detected_changes": [],
            "status": "ok"
        }
        
        logger.info("=" * 70)
        logger.info("🔍 楽天市場API変更検出を開始")
        logger.info(f"⏰ 検出時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S (JST)')}")
        logger.info("=" * 70 + "\n")
        
        for page_name, url in MONITORING_URLS.items():
            logger.info(f"📍 監視中: {page_name}")
            
            selectors = CRITICAL_SELECTORS.get(page_name, [])
            current_hash = self.get_page_hash(url, selectors)
            
            if current_hash is None:
                logger.warning(f"   ⚠️ ページ取得失敗\n")
                continue
            
            # ベースラインと比較
            baseline_hash = self.baseline.get(page_name)
            
            if baseline_hash is None:
                # 初回実行
                logger.info(f"   ℹ️ 初回実行 - ベースラインを保存\n")
                self.baseline[page_name] = current_hash
            elif baseline_hash != current_hash:
                # 変更検出
                logger.warning(f"   🚨 変更検出!")
                logger.warning(f"   前回: {baseline_hash}")
                logger.warning(f"   現在: {current_hash}\n")
                
                changes["detected_changes"].append({
                    "page": page_name,
                    "url": url,
                    "previous_hash": baseline_hash,
                    "current_hash": current_hash,
                    "detected_at": datetime.now().isoformat()
                })
                
                changes["status"] = "changes_detected"
                self.baseline[page_name] = current_hash
            else:
                logger.info(f"   ✓ 変更なし\n")
        
        # ベースラインを保存
        self.save_baseline()
        
        # 変更ログに記録
        self.log_changes(changes)
        
        logger.info("=" * 70)
        if changes["status"] == "changes_detected":
            logger.warning(f"⚠️ API変更が検出されました!")
            logger.warning(f"   検出件数: {len(changes['detected_changes'])}")
            logger.warning(f"   メール通知を送信します")
        else:
            logger.info(f"✓ API変更は検出されませんでした")
        logger.info("=" * 70 + "\n")
        
        return changes
    
    def log_changes(self, changes: Dict):
        """変更をログに記録"""
        with open(self.change_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{json.dumps(changes, ensure_ascii=False, indent=2)}\n")
    
    def run(self) -> bool:
        """検出を実行"""
        changes = self.detect_changes()
        
        # 変更が検出された場合は終了コード1で終了（メール通知トリガー）
        if changes["status"] == "changes_detected":
            return False
        
        return True

if __name__ == "__main__":
    detector = APIChangeDetector()
    success = detector.run()
    exit(0 if success else 1)
