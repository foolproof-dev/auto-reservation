#!/usr/bin/env python3
"""
松本市 公共施設予約システム 自動操作スクリプト
- 施設選択と日付指定で検索結果画面まで自動遷移する
"""

import sys
import json
import re
import time
from datetime import datetime

def run(facility_ids: list, target_date: str):
    """
    Args:
        facility_ids: チェックボックスのID一覧 例: ["checkShisetsu202001"]
        target_date:  日付文字列 例: "2026-03-10"
    """
    from playwright.sync_api import sync_playwright

    dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_year  = dt.year
    target_month = dt.month
    target_day   = dt.day

    print(f"[自動操作開始]")
    print(f"  施設ID : {facility_ids}")
    print(f"  対象日 : {target_year}年{target_month}月{target_day}日")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--no-sandbox']
        )
        context = browser.new_context(no_viewport=True)
        page    = context.new_page()

        # ─── STEP 1: トップページ ───────────────────────────
        print("\n[STEP 1/5] トップページへアクセス中...")
        page.goto(
            'https://yoyaku.city.matsumoto.lg.jp/WebR/Home/WgR_ModeSelect',
            wait_until='networkidle',
            timeout=30000
        )
        print(f"  URL: {page.url}")

        # ─── STEP 2: 体育施設カテゴリー選択 ─────────────────
        print("\n[STEP 2/5] 体育施設カテゴリーをクリック...")
        page.click('#category_10')
        page.wait_for_load_state('networkidle', timeout=15000)
        print(f"  URL: {page.url}")

        # 「さらに読み込む」ボタンがあればクリック（全20施設表示）
        try:
            more_btn = page.query_selector('text=さらに読み込む')
            if more_btn and more_btn.is_visible():
                more_btn.click()
                page.wait_for_timeout(1500)
                print("  全施設を表示しました")
        except Exception:
            pass

        # ─── STEP 3: 施設選択 ────────────────────────────────
        print("\n[STEP 3/5] 施設を選択中...")
        selected_names = []
        for fid in facility_ids:
            try:
                label = page.query_selector(f'label[for="{fid}"]')
                if label and label.is_visible():
                    name = label.inner_text().strip()
                    label.click()
                    page.wait_for_timeout(200)
                    # チェック確認
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

        # ─── STEP 4: 施設別空き状況ページへ ─────────────────
        print("\n[STEP 4/5] 空き状況ページへ移行中...")
        with page.expect_navigation(wait_until='networkidle', timeout=15000):
            page.evaluate("__doPostBack('next','')")
        print(f"  URL: {page.url}")

        # ─── STEP 5: 対象月に移動して日付を選択 ─────────────
        print(f"\n[STEP 5/5] {target_year}年{target_month}月{target_day}日を検索中...")

        found_date = False
        for nav_count in range(15):
            # 現在の表示月を確認
            month_el = page.query_selector('.pagination .month')
            if not month_el:
                print("  ⚠️ 月表示が見つかりません")
                break

            month_text = month_el.inner_text().strip()
            print(f"  現在表示中: {month_text}")

            m = re.search(r'(\d{4})年(\d{1,2})月', month_text)
            if not m:
                print("  ⚠️ 年月を解析できません")
                break

            cur_y = int(m.group(1))
            cur_m = int(m.group(2))

            # 目標月に到達したか確認
            if cur_y == target_year and cur_m == target_month:
                # 対象日付のチェックボックスを探す
                date_str = f"{target_year}{target_month:02d}{target_day:02d}"
                checkboxes = page.query_selector_all('input[name="checkdate"]')
                print(f"  チェックボックス数: {len(checkboxes)}")

                for cb in checkboxes:
                    val = cb.get_attribute('value') or ''
                    if val.startswith(date_str):
                        cb_id = cb.get_attribute('id')
                        label = page.query_selector(f'label[for="{cb_id}"]')
                        if label:
                            label_text = label.inner_text().strip()
                            if label_text in ['○', '△']:
                                label.click()
                                page.wait_for_timeout(300)
                                found_date = True
                                print(f"  ✓ {date_str} を選択しました（状態: {label_text}）")
                                break
                            else:
                                print(f"  ⚠️ {date_str} は選択不可（状態: {label_text}）")

                if not found_date:
                    print(f"  ⚠️ {date_str} の選択可能なセルが見つかりませんでした")
                    print("     空き状況カレンダーをそのまま表示します")
                break

            # 月を移動
            target_month_num = target_year * 12 + target_month
            cur_month_num    = cur_y * 12 + cur_m

            if cur_month_num < target_month_num:
                print(f"  → 次の月へ")
                with page.expect_navigation(wait_until='networkidle', timeout=10000):
                    page.evaluate("__doPostBack('period','next')")
            else:
                print(f"  ← 前の月へ")
                with page.expect_navigation(wait_until='networkidle', timeout=10000):
                    page.evaluate("__doPostBack('period','prev')")

        # 日付が選択できた場合は「次へ進む」で詳細へ
        if found_date:
            print("\n[検索結果へ移行中...]")
            with page.expect_navigation(wait_until='networkidle', timeout=15000):
                page.evaluate("__doPostBack('next','')")
            print(f"  最終URL: {page.url}")
            print("\n=== 検索結果を表示しました ===")
        else:
            print("\n=== 空き状況カレンダーを表示しています ===")

        print("\nブラウザを開いたままにしています。")
        print("操作が完了したら、ブラウザウィンドウを閉じてください。")

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
