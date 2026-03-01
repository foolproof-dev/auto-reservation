from flask import Flask, render_template, request, jsonify
import subprocess
import sys
import os
import json

app = Flask(__name__)

# 施設リスト（「〇〇体育館」の名称を持つ施設のみ・全25施設）
FACILITIES = [
    {"id": "checkShisetsu202001", "value": "202001", "name": "総合体育館"},
    {"id": "checkShisetsu202002", "value": "202002", "name": "南部体育館"},
    {"id": "checkShisetsu202003", "value": "202003", "name": "岡田体育館"},
    {"id": "checkShisetsu202004", "value": "202004", "name": "芳川体育館"},
    {"id": "checkShisetsu202005", "value": "202005", "name": "島内体育館"},
    {"id": "checkShisetsu202006", "value": "202006", "name": "庄内体育館"},
    {"id": "checkShisetsu202007", "value": "202007", "name": "芝沢体育館"},
    {"id": "checkShisetsu202008", "value": "202008", "name": "神林体育館"},
    {"id": "checkShisetsu202009", "value": "202009", "name": "里山辺体育館"},
    {"id": "checkShisetsu202010", "value": "202010", "name": "鎌田体育館"},
    {"id": "checkShisetsu202011", "value": "202011", "name": "今井体育館"},
    {"id": "checkShisetsu202012", "value": "202012", "name": "島立体育館"},
    {"id": "checkShisetsu202013", "value": "202013", "name": "寿体育館"},
    {"id": "checkShisetsu202014", "value": "202014", "name": "寿台体育館"},
    {"id": "checkShisetsu202015", "value": "202015", "name": "本郷体育館"},
    {"id": "checkShisetsu202016", "value": "202016", "name": "内田体育館"},
    {"id": "checkShisetsu202017", "value": "202017", "name": "中央体育館"},
    {"id": "checkShisetsu202018", "value": "202018", "name": "臨空工業団地体育館"},
    {"id": "checkShisetsu202019", "value": "202019", "name": "四賀体育館"},
    {"id": "checkShisetsu202020", "value": "202020", "name": "安曇体育館"},
    {"id": "checkShisetsu202021", "value": "202021", "name": "梓川体育館"},
    {"id": "checkShisetsu202022", "value": "202022", "name": "波田体育館"},
    {"id": "checkShisetsu202023", "value": "202023", "name": "乗鞍体育館"},
    {"id": "checkShisetsu202024", "value": "202024", "name": "奈川寄合渡体育館"},
    {"id": "checkShisetsu202025", "value": "202025", "name": "奈川木曽路原体育館"},
]

@app.route('/')
def index():
    return render_template('index.html', facilities=FACILITIES)

@app.route('/launch', methods=['POST'])
def launch_browser():
    """ブラウザを起動して自動操作を開始する"""
    data = request.json or {}
    facility_ids = data.get('facility_ids', [])
    target_date  = data.get('date', '')

    if not facility_ids:
        return jsonify({"status": "error", "message": "施設を1つ以上選択してください"})
    if not target_date:
        return jsonify({"status": "error", "message": "日付を選択してください"})

    # automation.py を別プロセスで起動（非ブロッキング）
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'automation.py')
    env = os.environ.copy()

    try:
        if sys.platform == 'win32':
            # Windows: 新しいコンソールウィンドウで起動
            subprocess.Popen(
                [
                    sys.executable,
                    script_path,
                    json.dumps(facility_ids),
                    target_date
                ],
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Mac/Linux
            subprocess.Popen(
                [
                    sys.executable,
                    script_path,
                    json.dumps(facility_ids),
                    target_date
                ],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        return jsonify({
            "status": "ok",
            "message": "ブラウザを起動しました。別ウィンドウをご確認ください。"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("=" * 50)
    print(" 松本市 体育館 空き状況チェッカー")
    print(" URL: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
