from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

KEYS_FILE = "keys_database.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}

def save_keys(keys_data):
    try:
        with open(KEYS_FILE, "w", encoding="utf-8") as f:
            json.dump(keys_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving keys: {e}")

@app.route('/verify_key', methods=['POST'])
def verify_key():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "بيانات غير صالحة!"})
        
    user_key = data.get("key")
    device_id = data.get("device_id")

    keys = load_keys()

    if user_key not in keys:
        return jsonify({"success": False, "message": "المفتاح غير موجود أو غير صالح!"})

    key_info = keys[user_key]

    # التحقق مما إذا كان المفتاح مسجلاً على جهاز آخر مسبقاً
    registered_device = key_info.get("device_id")
    if registered_device is not None:
        if registered_device != device_id:
            return jsonify({"success": False, "message": "هذا المفتاح مستخدم على جهاز آخر مسبقاً!"})
        else:
            return jsonify({"success": True, "message": "تم التحقق مسبقاً لهذا الجهاز.", "duration_days": 7})

    # ربط المفتاح بالجهاز الحالي وتثبيته
    key_info["device_id"] = device_id
    save_keys(keys)

    return jsonify({"success": True, "message": "تم التفعيل بنجاح!", "duration_days": 7})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
