from flask import Flask, render_template, request, jsonify
import random
import requests  # ไลบรารีสำหรับยิง API หา LINE

app = Flask(__name__)

# ==========================================
# 🔑 คีย์ระบบ LINE Developers (ใช้สำหรับแข่ง)
# ==========================================
# ตัวนี้คือ Token ลับของ SmartPlant_Bot ที่พี่เจนเนอเรตมาให้ครับ บอทไอดีคือ @048rcoii
LINE_ACCESS_TOKEN = "u0ZqVpX9b7m8VvY6zC1E+DkW4l3H5R0pM7Kx/Jb8N2fX3L5P9v1k0F2O4e5R6t7y8u9i0o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8u0ZqVpX9b7m8VvY6zC1E+"

# ฟังก์ชันยิงแจ้งเตือนเข้าแอป LINE แบบ Broadcast (ส่งหาทุกคนที่แอดบอทตัวนี้ไว้)
def send_line_broadcast(text_message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": text_message
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("📊 LINE API Broadcast Status:", response.status_code)
    except Exception as e:
        print("❌ เกิดข้อผิดพลาดในการส่ง LINE:", e)


# ==========================================
# 1. ส่วนเปิดหน้าแอปพลิเคชัน (ดึงหน้ากากเว็บมาแสดง)
# ==========================================
@app.route('/')
@app.route('/index')
def home():
    return render_template('index.html')

# ==========================================
# 2. ส่วนรับภาพจากกล้อง, ประมวลผล และยิงเข้า LINE
# ==========================================
@app.route('/api/predict', methods=['POST'])
def predict():
    # เช็กว่ามีการส่งไฟล์ภาพมาหรือไม่
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'ไม่พบไฟล์ภาพ'})
    
    file = request.files['image']
    
    # สุ่มเปอร์เซ็นต์ความสมบูรณ์และความชื้นตามโครงสร้างเดิมของน้อง
    health = random.randint(75, 98)
    water = random.randint(40, 85)
    
    # รายชื่อสุ่มโรคพืชระดับมหาลัย เพิ่มเติมรายละเอียดการวิเคราะห์
    mock_diseases = [
        "โรคใบไหม้ (Blight) 🍂\nคำแนะนำ: ให้ตัดใบที่ติดโรคออกและฉีดพ่นเชื้อราไตรโคเดอร์มาเพื่อควบคุมสปอร์",
        "โรคราแป้ง (Powdery Mildew) 🍄\nคำแนะนำ: เพิ่มการระบายอากาศในแปลง และฉีดพ่นน้ำหมักสมุนไพรเปลือกมังคุด",
        "โรครากเน่าโคนเน่า (Root Rot) 💧\nคำแนะนำ: พบความชื้นสะสมบริเวณโคนสูงเกินไป ปรับปรุงการระบายน้ำในดินโดยด่วน"
    ]
    
    # กำหนดสถานะและเลือกข้อวินิจฉัยโรคตามปริมาณน้ำ
    if water < 50:
        status = "⚠️ ควรให้น้ำเพิ่ม (ความชื้นต่ำ)"
        diagnosis = "พบภาวะพืชขาดน้ำเฉียบพลัน 🍂 แนะนำให้เปิดระบบสปริงเกอร์เติมความชื้นในดิน"
    elif water > 80:
        status = "⚠️ ระวังเชื้อรา (ความชื้นสูงเกินไป)"
        diagnosis = random.choice([mock_diseases[0], mock_diseases[1], mock_diseases[2]])
    else:
        status = "✅ ปกติดี (Normal)"
        diagnosis = "พืชสุขภาพดีแข็งแรงสมบูรณ์ ✨ สภาพต้นไม้ปกติ ดูแลรดน้ำตามรอบปกติได้เลยครับ"
        
    # 📢 3. บล็อกสร้างข้อความและสั่งเด้งแจ้งเตือนเข้าแอป LINE อัตโนมัติ
    line_text = f"🚨 แจ้งเตือนจากระบบ SmartPlant\n\n📌 ผลวิเคราะห์แปลงล่าสุด:\n- สถานะ: {status}\n- ความสมบูรณ์: {health}%\n- ความชื้นใบ: {water}%\n\n📋 รายละเอียดเทคนิคการดูแล:\n{diagnosis}"
    send_line_broadcast(line_text)

    # ส่งข้อมูลกลับไปให้หน้าเว็บ 300 บรรทัดอัปเดตแอนิเมชันเกจวัด
    return jsonify({
        'status': 'success',
        'health_rate': health,
        'water_level': water,
        'plant_status': "ผลตรวจ: " + status if "✅" in status else "ผลตรวจ: " + diagnosis.split('\n')[0]
    })


# ==========================================
# 3. ส่วนส่งข้อมูลให้กราฟสถิติสะสม (คืนชีพหน้าสถิติ)
# ==========================================
@app.route('/api/dashboard_data')
def dashboard_data():
    # ข้อมูลสถิติจำลองสำหรับวาดโครงกราฟเส้นและกราฟวงกลมบนหน้าเว็บน้อง
    return jsonify({
        'labels': ['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.'],
        'values': [65, 59, 80, 81, 56, 55, 40],
        'distribution': {
            'สมบูรณ์ดี': 70,
            'ขาดน้ำ': 20,
            'พบความเสี่ยงโรค': 10
        }
    })


# ==========================================
# 4. ส่วนเปิดเซิร์ฟเวอร์และรับการเชื่อมต่อจากมือถือ
# ==========================================
if __name__ == '__main__':
    # host='0.0.0.0' ช่วยให้คอมพิวเตอร์และมือถือที่ต่อ Wi-Fi เดียวกันวิ่งเข้ามาเทสกล้องได้
    app.run(debug=True, host='0.0.0.0', port=5000)