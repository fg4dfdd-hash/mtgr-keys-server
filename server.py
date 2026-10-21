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

        # إذا كان المفتاح مستخدماً مسبقاً على جهاز آخر
        if registered_device is not None:
            if registered_device != device_id:
                return jsonify({"success": False, "message": "هذا المفتاح مستخدم ومقفل على جهاز آخر مسبقاً!"})
            else:
                # إذا كان مستخدماً مسبقاً على نفس الجهاز، نتحقق من صلاحيته
                expires_str = key_info.get("expires")
                if expires_str:
                    expires_time = datetime.datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
                    if datetime.datetime.now() < expires_time:
                        return jsonify({"success": True, "message": "تم التحقق مسبقاً لهذا الجهاز.", "duration_days": key_info.get("duration_days", 7)})
                return jsonify({"success": False, "message": "انتهت صلاحية هذا المفتاح!"})

        # حرق المفتاح لأول مرة وربطه بالجهاز وحساب وقت الانتهاء بدقة
        duration_days = key_info.get("duration_days", 7)
        expires_time = datetime.datetime.now() + datetime.timedelta(days=duration_days)
        
        key_info["device_id"] = device_id
        key_info["expires"] = expires_time.strftime("%Y-%m-%d %H:%M:%S")
        
        save_keys(keys)

        return jsonify({"success": True, "message": "تم التفعيل بنجاح وحرق المفتاح!", "duration_days": duration_days})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ في السيرفر: {str(e)}"})

@app.route('/check_keys', methods=['GET'])
def check_keys():
    keys = load_keys()
    return jsonify({"total_keys": len(keys), "keys_database": keys})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
