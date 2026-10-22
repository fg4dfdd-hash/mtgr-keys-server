from flask import Flask, request, jsonify
import json
import os
import datetime

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

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Server is running successfully!", "brand": "mtgr_als3adh"})

@app.route('/debug_keys', methods=['GET'])
def debug_keys():
    return jsonify(load_keys())

@app.route('/verify_key', methods=['POST'])
def verify_key():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "بيانات غير صالحة!"})
            
        user_key = data.get("key")
        device_id = data.get("device_id")

        keys = load_keys()

        if user_key not in keys:
            return jsonify({"success": False, "message": "المفتاح غير موجود أو غير صالح!"})

        key_info = keys[user_key]
        registered_device = key_info.get("device_id")
        expires_str = key_info.get("expires")

        if registered_device is not None and registered_device != device_id:
            return jsonify({"success": False, "message": "هذا المفتاح مستخدم ومقفل على جهاز آخر مسبقاً!"})

        now = datetime.datetime.now()

        if registered_device == device_id and expires_str:
            expires_time = datetime.datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
            if now < expires_time:
                return jsonify({
                    "success": True, 
                    "message": "تم التحقق من الجهاز مسبقاً.", 
                    "expires": expires_str
                })
            else:
                return jsonify({"success": False, "message": "انتهت صلاحية هذا المفتاح!"})

        duration_days = key_info.get("duration_days", 7)
        expires_time = now + datetime.timedelta(days=duration_days)
        expires_formatted = expires_time.strftime("%Y-%m-%d %H:%M:%S")
        
        key_info["device_id"] = device_id
        key_info["expires"] = expires_formatted
        save_keys(keys)

        return jsonify({
            "success": True, 
            "message": "تم التفعيل بنجاح وحرق المفتاح!", 
            "expires": expires_formatted
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ في السيرفر: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
