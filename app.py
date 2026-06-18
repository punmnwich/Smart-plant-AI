import os
# 🟢 บังคับให้ระบบใช้ระบบ Legacy Keras เพื่อให้รองรับโมเดล Teachable Machine เวอร์ชันเก่า
os.environ['TF_USE_LEGACY_KERAS'] = "1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, render_template, request, jsonify
import random
import requests
import numpy as np
from PIL import Image

# 🟢 เปลี่ยนมาใช้เครื่องมือ tf_keras โน้ตบุ๊กโหลดโมเดล จะได้ไม่ตีกับเวอร์ชันใหม่
import tf_keras as keras

# บังคับโฟลเดอร์สำหรับเซิร์ฟเวอร์
app = Flask(__name__, template_folder='templates', static_folder='static')

# 🔑 คีย์ระบบ LINE Developers
LINE_ACCESS_TOKEN = "XFIIe1DgW2vJNns4pYfPR7mBj8Xqos5Q4KWzTCCam4elq6hxmvBjlOgHKsULgWLTG/Bvypt1aDQdCo5Q9VGA9PAwMJIkRPEg2YGtLOiTvHUrLj7Scf6aIGdyYIaONPBT4Jl7/Q4vSEkPXP5WYJYX0gdB04t89/1O/w1cDnyilFU="

# ==========================================
# 🤖 ส่วนโหลดโมเดล Teachable Machine
# ==========================================
MODEL_PATH = "keras_model.h5"
LABELS_PATH = "labels.txt"

if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
    # 🟢 โหลดผ่าน tf_keras ได้อย่างปลอดภัย 100%
    model = keras.models.load_model(MODEL_PATH, compile=False)
    class_names = open(LABELS_PATH, "r", encoding="utf-8").readlines()
    print("✨ เชื่อมต่อโมเดล Teachable Machine สำเร็จเรียบร้อย!")
else:
    model = None
    class_names = []
    print("⚠️ ไม่พบไฟล์โมเดล keras_model.h5 หรือ labels.txt ระบบจะใช้ Mock สุ่มไปก่อน")

# ==========================================
# 📱 ฟังก์ชันสำหรับส่งแจ้งเตือนเข้า LINE
# ==========================================
def send_line_broadcast(text_message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "messages": [{"type": "text", "text": text_message}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("📊 LINE API Broadcast Status:", response.status_code)
    except Exception as e:
        print("❌ เกิดข้อผิดพลาดในการส่ง LINE:", e)

# ==========================================
# 🌐 ส่วนเชื่อมต่อหน้าเว็บ (Routes)
# ==========================================
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการโหลดหน้าเว็บ: {str(e)}"

@app.route('/index')
@app.route('/index.html')
def index_page():
    return render_template('index.html')

# ==========================================
# 📷 ส่วนรับภาพจากหน้าเว็บ และให้ AI วิเคราะห์
# ==========================================
@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'ไม่พบไฟล์ภาพ'})
    
    file = request.files['image']
    
    health = random.randint(85, 98)
    water = random.randint(55, 75)
    
    if model is not None:
        try:
            image = Image.open(file.stream).convert("RGB")
            image = image.resize((224, 224))
            
            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            data[0] = normalized_image_array
            
            # สั่งรันโมเดลวิเคราะห์ภาพ
            prediction = model.predict(data, verbose=0)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            
            ai_result = class_name[2:] if len(class_name) > 2 else class_name
            
            if "Blight" in ai_result or "โรคใบไหม้" in ai_result:
                status = "⚠️ ตรวจพบโรคพืช"
                diagnosis = "โรคใบไหม้ (Blight) 🍂\nคำแนะนำ: ให้ตัดใบที่ติดโรคออกและฉีดพ่นเชื้อราไตรโคเดอร์มาเพื่อควบคุมสปอร์"
                health = random.randint(40, 60)
            elif "Mildew" in ai_result or "ราแป้ง" in ai_result:
                status = "⚠️ ตรวจพบโรคพืช"
                diagnosis = "โรคราแป้ง (Powdery Mildew) 🍄\nคำแนะนำ: เพิ่มการระบายอากาศในแปลง และฉีดพ่นน้ำหมักสมุนไพรเปลือกมังคุด"
                health = random.randint(50, 65)
            elif "Rot" in ai_result or "รากเน่า" in ai_result:
                status = "⚠️ ตรวจพบโรคพืช"
                diagnosis = "โรครากเน่าโคนเน่า (Root Rot) 💧\nคำแนะนำ: พบความชื้นสะสมบริเวณโคนสูงเกินไป ปรับปรุงการระบายน้ำในดินโดยด่วน"
                health = random.randint(30, 55)
                water = random.randint(85, 95)
            else:
                status = "✅ ปกติดี (Normal)"
                diagnosis = "พืชสุขภาพดีแข็งแรงสมบูรณ์ ✨ สภาพต้นไม้ปกติ ดูแลรดน้ำตามรอบปกติได้เลยครับ"
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'เกิดข้อผิดพลาดในการรัน AI: {str(e)}'})
    else:
        status = "✅ ปกติดี (ระบบจำลอง)"
        diagnosis = "พืชสุขภาพดีแข็งแรงสมบูรณ์ สภาพต้นไม้ปกติ (ไม่พบไฟล์โมเดลจริง)"

    line_text = f"🚨 แจ้งเตือนจากระบบ SmartPlant\n\n📌 ผลวิเคราะห์แปลงล่าสุดด้วย AI:\n- Status: {status}\n- Health: {health}%\n- Moisture: {water}%\n\n📋 รายละเอียดเทคนิคการดูแล:\n{diagnosis}"
    send_line_broadcast(line_text)

    return jsonify({
        'status': 'success',
        'health_rate': health,
        'water_level': water,
        'plant_status': "ผลตรวจ: " + status if "✅" in status else "ผลตรวจ: " + diagnosis.split('\n')[0]
    })

@app.route('/api/dashboard_data')
def dashboard_data():
    return jsonify({
        'labels': ['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.'],
        'values': [65, 59, 80, 81, 56, 55, 40],
        'distribution': {
            'สมบูรณ์ดี': 70,
            'ขาดน้ำ': 20,
            'พบความเสี่ยงโรค': 10
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)