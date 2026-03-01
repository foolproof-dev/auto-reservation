#!/usr/bin/env python3
"""
松本市 公共施設予約システム 自動操作スクリプト
- 施設選択 → 施設別空き状況ページ → 表示開始日入力 → 表示ボタン押下
"""

import sys
import json
from datetime import datetime


def run(facility_ids: list, target_date: str):
    """
    Args:
        facility_ids: チェックボックスのID一覧 例: ["checkShisetsu202001"]
        target_date:  日付文字列 例: "2026-03-10"
    """
    from playwright.sync_api import sync_playwright

    dt = datetime.strptime(target_date, "%Y-%m-%d")
    # サイトの日付フォーマットに合わせる（例: "2026/3/10"）
    date_for_form = f"{dt.year}/{dt.month}/{dt.day}"

    print(f"[自動操作開始]")
    print(f"  施設ID  : {facility_ids}")
    print(f"  表示開始日: {date_for_form}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--no-sandbox']
        )
        context = browser.new_context(no_viewport=True)
        page    = context.new_page()

        # ─── STEP 1: トップページ ─────────────────────────────
        print("\n[STEP 1/4] トップページへアクセス中...")
        page.goto(
            'https://yoyaku.city.matsumoto.lg.jp/WebR/Home/WgR_ModeSelect',
            wait_until='networkidle',
            timeout=30000
        )
        print(f"  URL: {page.url}")

        # ─── STEP 2: 体育施設カテゴリー選択 ───────────────────
        print("\n[STEP 2/4] 体育施設カテゴリーをクリック...")
        page.click('#category_10')
        page.wait_for_load_state('networkidle', timeout=15000)
        print(f"  URL: {page.url}")

        # 「さらに読み込む」ボタンを最大2回クリック（〇〇体育館が全て表示される）
        click_count = 0
        while click_count < 2:
            try:
                more_btn = page.query_selector('text=さらに読み込む')
                if more_btn and more_btn.is_visible():
                    more_btn.click()
                    page.wait_for_timeout(1000)
                    click_count += 1
                else:
                    break
            except Exception:
                break
        if click_count > 0:
            print(f"  「さらに読み込む」を{click_count}回クリック → 体育館一覧を表示しました")

        # ─── STEP 3: 施設選択 ──────────────────────────────────
        print("\n[STEP 3/4] 施設を選択中...")
        selected_names = []
        for fid in facility_ids:
            try:
                label = page.query_selector(f'label[for="{fid}"]')
                if label and label.is_visible():
                    name = label.inner_text().strip()
                    label.click()
                    page.wait_for_timeout(200)
                    cb = page.query_selector(f'#{fid}')
                    if cb and cb.is_checked():
                        selected_names.append(name)
                        print(f"  ✓ {name}")
                    else:
                        print(f"  ✗ チェック失敗: {name}")
                else:
                    print(f"  ✗ 施設が見つかりません: {fid}")
            except Exception as e:
                print(f"  ✗ エラー ({fid}): {e}")

        if not selected_names:
            print("  ⚠️ 施設が1件も選択できませんでした。処理を続行します。")

        # ─── STEP 4: 施設別空き状況ページ → 表示開始日入力 → 表示 ───
        print("\n[STEP 4/4] 空き状況ページへ移行中...")
        with page.expect_navigation(wait_until='networkidle', timeout=15000):
            page.evaluate("__doPostBack('next','')")
        print(f"  URL: {page.url}")

        # 表示開始日フィールドに日付を入力
        print(f"  表示開始日に「{date_for_form}」を入力中...")
        page.fill('#dpStartDate', date_for_form)
        page.wait_for_timeout(300)

        # 「表示」ボタンを押下
        print(f"  「表示」ボタンを押下中...")
        with page.expect_navigation(wait_until='networkidle', timeout=15000):
            page.evaluate("__doPostBack('hyouji','')")
        print(f"  URL: {page.url}")

        print(f"\n=== {date_for_form} からの空き状況を表示しました ===")
        print("\nブラウザを開いたままにしています。")
        print("確認が終わったらブラウザウィンドウを閉じてください。")

        # ブラウザを開いたままにする（終了を待機）
        try:
            page.wait_for_event('close', timeout=0)
        except Exception:
            pass

        try:
            browser.close()
        except Exception:
            pass


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python automation.py '<facility_ids_json>' '<date>'")
        print("Example: python automation.py '[\"checkShisetsu202001\"]' '2026-03-15'")
        sys.exit(1)

    fids = json.loads(sys.argv[1])
    date = sys.argv[2]
    run(fids, date)
