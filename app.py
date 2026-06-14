from flask import Flask, render_template, request, jsonify
import random
import requests
import os

# บังคับโฟลเดอร์สำหรับ Vercel Serverless
app = Flask(__name__, template_folder='templates', static_folder='static')

# 🔑 คีย์ระบบ LINE Developers (บอทไอดีคือ @048rcoii)
LINE_ACCESS_TOKEN = "XFIIe1DgW2vJNns4pYfPR7mBj8Xqos5Q4KWzTCCam4elq6hxmvBjlOgHKsULgWLTG/Bvypt1aDQdCo5Q9VGA9PAwMJIkRPEg2YGtLOiTvHUrLj7Scf6aIGdyYIaONPBT4Jl7/Q4vSEkPXP5WYJYX0gdB04t89/1O/w1cDnyilFU="

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
# 1. ส่วนเปิดหน้าแอปพลิเคชัน (แก้ปัญหา 500 Internal Error)
# ==========================================
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการโหลดหน้าเว็บ: {str(e)} - โปรดตรวจสอบว่ามีไฟล์ index.html อยู่ในโฟลเดอร์ templates หรือไม่"

@app.route('/index')
@app.route('/index.html')
def index_page():
    return render_template('index.html')

# ==========================================
# 2. ส่วนรับภาพจากกล้อง, ประมวลผล และยิงเข้า LINE
# ==========================================
@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'ไม่พบไฟล์ภาพ'})
    
    file = request.files['image']
    
    health = random.randint(75, 98)
    water = random.randint(40, 85)
    
    mock_diseases = [
        "โรคใบไหม้ (Blight) 🍂\nคำแนะนำ: ให้ตัดใบที่ติดโรคออกและฉีดพ่นเชื้อราไตรโคเดอร์มาเพื่อควบคุมสปอร์",
        "โรคราแป้ง (Powdery Mildew) 🍄\nคำแนะนำ: เพิ่มการระบายอากาศในแปลง และฉีดพ่นน้ำหมักสมุนไพรเปลือกมังคุด",
        "โรครากเน่าโคนเน่า (Root Rot) 💧\nคำแนะนำ: พบความชื้นสะสมบริเวณโคนสูงเกินไป ปรับปรุงการระบายน้ำในดินโดยด่วน"
    ]
    
    if water < 50:
        status = "⚠️ ควรให้น้ำเพิ่ม (ความชื้นต่ำ)"
        diagnosis = "พบภาวะพืชขาดน้ำเฉียบพลัน 🍂 แนะนำให้เปิดระบบสปริงเกอร์เติมความชื้นในดิน"
    elif water > 80:
        status = "⚠️ ระวังเชื้อรา (ความชื้นสูงเกินไป)"
        diagnosis = random.choice(mock_diseases)
    else:
        status = "✅ ปกติดี (Normal)"
        diagnosis = "พืชสุขภาพดีแข็งแรงสมบูรณ์ ✨ สภาพต้นไม้ปกติ ดูแลรดน้ำตามรอบปกติได้เลยครับ"
        
    line_text = f"🚨 แจ้งเตือนจากระบบ SmartPlant\n\n📌 ผลวิเคราะห์แปลงล่าสุด:\n- Status: {status}\n- Health: {health}%\n- Moisture: {water}%\n\n📋 รายละเอียดเทคนิคการดูแล:\n{diagnosis}"
    send_line_broadcast(line_text)

    return jsonify({
        'status': 'success',
        'health_rate': health,
        'water_level': water,
        'plant_status': "ผลตรวจ: " + status if "✅" in status else "ผลตรวจ: " + diagnosis.split('\n')[0]
    })

# ==========================================
# 3. ส่วนส่งข้อมูลให้กราฟสถิติสะสม
# ==========================================
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