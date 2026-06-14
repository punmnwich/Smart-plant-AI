import os
import random
import numpy as np

# ชื่อไฟล์โมเดลในอนาคต (ตอนนี้ยังไม่มีไม่เป็นไร)
MODEL_PATH = "keras_model.h5"

def analyze_plant_image(image_path):
    """
    วิเคราะห์สุขภาพพืช: รองรับทั้งระบบโมเดลจริง และระบบจำลอง (Mockup) 
    เพื่อให้รันหน้าเว็บและ LINE ทดสอบได้ทันที!
    """
    try:
        # 1. ตรวจสอบว่ามีไฟล์โมเดล Teachable Machine จริงไหม?
        if os.path.exists(MODEL_PATH):
            import cv2
            import tensorflow as tf
            
            print("🤖 [AI Mode] กำลังวิเคราะห์ภาพด้วยสมองกล Teachable Machine...")
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("อ่านไฟล์ภาพไม่ได้")
                
            image_resized = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
            image_array = np.asarray(image_resized, dtype=np.float32)
            normalized_image_array = (image_array / 127.5) - 1
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            data[0] = normalized_image_array

            prediction = model.predict(data)
            index = np.argmax(prediction)
            confidence_score = prediction[0][index]

            if index == 0:    # ปกติ (Healthy)
                water_level = round(float(80 + (confidence_score * 15)), 1)
                health_rate = round(float(water_level + random.uniform(-2, 2)), 1)
            elif index == 1:  # เริ่มขาดน้ำ (Mild)
                water_level = round(float(60 + (confidence_score * 18)), 1)
                health_rate = round(float(water_level - 3), 1)
            else:             # ขาดน้ำรุนแรง (Severe)
                water_level = round(float(15 + (confidence_score * 35)), 1)
                health_rate = round(float(water_level - 5), 1)

        # 2. ถ้ายังไม่เทรนโมเดล ให้เปิด [ระบบจำลอง] ทำงานแทนอัตโนมัติ
        else:
            print("🎲 [Simulation Mode] ไม่พบไฟล์โมเดล ระบบกำลังจำลองผลลัพธ์ให้เพื่อทดสอบระบบ...")
            
            # สุ่มเลือกสถานะพืชแบบเมคขึ้นมา (เพื่อดูว่าหน้าเว็บ และ LINE เปลี่ยนตามไหม)
            status_choice = random.choice(["healthy", "mild", "severe"])
            
            if status_choice == "healthy":
                water_level = round(random.uniform(80.0, 98.0), 1)
                health_rate = round(water_level + random.uniform(-2, 2), 1)
            elif status_choice == "mild":
                water_level = round(random.uniform(60.0, 78.0), 1)
                health_rate = round(water_level - random.uniform(1, 4), 1)
            else:
                water_level = round(random.uniform(15.0, 45.0), 1)
                health_rate = round(water_level - random.uniform(3, 6), 1)

        # ควบคุมค่าไม่ให้เพี้ยนเกิน 0-100
        water_level = min(100.0, max(0.0, water_level))
        health_rate = min(100.0, max(0.0, health_rate))

        return health_rate, water_level

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e} -> ใช้ค่าเซฟโซนเริ่มต้น")
        return 85.0, 80.0 