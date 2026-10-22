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
        expires_str = key_info.get("expires")

        # 1. إذا كان المفتاح مستخدماً مسبقاً على جهاز آخَر (محظور تماماً)
        if registered_device is not None and registered_device != device_id:
            return jsonify({"success": False, "message": "هذا المفتاح مستخدم ومقفل على جهاز آخر مسبقاً!"})

        # 2. إذا كان المفتاح مستخدماً مسبقاً على نفس الجهاز أو يتم تفعيله لأول مرة
        now = datetime.datetime.now()

        if registered_device == device_id and expires_str:
            # المفتاح مسجل مسبقاً على نفس الجهاز، نتحقق هل انتهى وقته الثابت أم لا؟
            expires_time = datetime.datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
            if now < expires_time:
                # حساب الساعات المتبقية الفعلية بدقة وثبات
                remaining_seconds = int((expires_time - now).total_seconds())
                return jsonify({
                    "success": True, 
                    "message": "تم التحقق من الجهاز مسبقاً.", 
                    "remaining_seconds": remaining_seconds,
                    "expires": expires_str
                })
            else:
                return jsonify({"success": False, "message": "انتهت صلاحية هذا المفتاح!"})

        # 3. تفعيل لأول مرة (حرق المفتاح وربطه نهائياً بالجهاز وتثبيت وقت الانتهاء)
        duration_days = key_info.get("duration_days", 7)
        expires_time = now + datetime.timedelta(days=duration_days)
        expires_formatted = expires_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # حفظ البيانات في السيرفر
        key_info["device_id"] = device_id
        key_info["expires"] = expires_formatted
        save_keys(keys)

        remaining_seconds = int((expires_time - now).total_seconds())
        return jsonify({
            "success": True, 
            "message": "تم التفعيل بنجاح وحرق المفتاح!", 
            "remaining_seconds": remaining_seconds,
            "expires": expires_formatted
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ في السيرفر: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
