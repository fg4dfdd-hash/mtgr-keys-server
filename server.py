from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

KEYS_FILE = "keys_database.json"

# دالة لقراءة المفاتيح من قاعدة البيانات
def load_keys():
    if not os.path.exists(KEYS_FILE):
        # مفاتيح تجريبية أولية
        initial_keys = {
            "WEEK-0001-PRO-KEY": {"used": False, "duration_days": 7},
            "WEEK-0002-PRO-KEY": {"used": False, "duration_days": 30}
        }
        save_keys(initial_keys)
        return initial_keys
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# دالة لحفظ المفاتيح في قاعدة البيانات
def save_keys(keys_data):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys_data, f, indent=4)

@app.route('/verify_key', methods=['POST'])
def verify_key():
    data = request.json
    user_key = data.get("key")
    device_id = data.get("device_id")

    keys = load_keys()

    if user_key not in keys:
        return jsonify({"success": False, "message": "المفتاح غير موجود أو غير صالح!"})

    key_info = keys[user_key]

    # التحقق مما إذا كان المفتاح قد استُخدم من قبل
    if key_info["used"]:
        return jsonify({"success": False, "message": "عذراً، هذا المفتاح مستخدم من قبل وتم حرق وإلغاء صلاحيته!"})

    # استخدام المفتاح لمرة واحدة وتحديث حالته في السحابة
    key_info["used"] = True
    key_info["device_id"] = device_id
    save_keys(keys)

    return jsonify({
        "success": True, 
        "duration_days": key_info["duration_days"],
        "message": "تم التفعيل بنجاح وتم قفل المفتاح نهائياً!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)