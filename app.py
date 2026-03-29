import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="أفراح أبو ليله", page_icon="💍", layout="centered")

# --- 2. اتصال Firebase (تم الإصلاح هنا) ---
@st.cache_resource
def init_db():
    if not firebase_admin._apps:
        try:
            # ✅ تم التعديل هنا
            key_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error("❌ خطأ في إعداد Firebase Secrets")
            st.error(e)
            st.stop()
    return firestore.client()

# تشغيل قاعدة البيانات
try:
    db = init_db()
except:
    st.warning("جاري تهيئة قاعدة البيانات...")

# إدارة حالة فتح الكارت
if 'opened' not in st.session_state:
    st.session_state.opened = False

# --- 3. تصميم الكارت ---
card_html = """
<div style="direction: rtl; text-align: center; font-family: 'Amiri', serif; background: white; padding: 15px; border-radius: 15px; border: 4px double #D4AF37; color: #333; max-width: 95%; margin: auto;">
    <style>@import url('https://fonts.googleapis.com/css2?family=Amiri&family=Reem+Kufi&display=swap');</style>
    <div style="color: #D4AF37; font-size: 1.2rem; font-weight: bold;">﷽</div>
    <p>يتشرف الأستاذ/ <b>صابر عبده</b></p>
    <p>بدعوتكم لحضور حفل زفاف شقيقه</p>
    <div style="color: #D4AF37; font-size: 2rem;">محمد عبده</div>
    <p>📍 قاعة ميراج - بشما</p>
    <p>📅 الجمعة 10 / 4 / 2026</p>
    <p style="color: #D4AF37;">فرحتنا تكتمل بوجودكم ❤️</p>
</div>
"""

# --- 4. العرض ---
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>أفراح أبو ليله</h1>",
            unsafe_allow_html=True)

if not st.session_state.opened:
    if os.path.exists("wedding.jpg"):
        st.image("wedding.jpg", use_container_width=True)
    if st.button("تفضلوا بفتح الدعوة ✨", use_container_width=True):
        st.session_state.opened = True
        st.rerun()
else:
    st.balloons()
    components.html(card_html, height=400)
    st.divider()

    # --- 5. التهاني ---
    st.subheader("💌 سجل كلمة للذكرى")
    name = st.text_input("الاسم الكريم:")
    msg = st.text_area("رسالة تهنئة للعريس:")

    if st.button("إرسال التهنئة ❤️", use_container_width=True):
        if name and msg:
            try:
                db.collection("wishes").add({
                    "name": name,
                    "message": msg,
                    "time": datetime.now()
                })
                st.success("تم الإرسال بنجاح! 😍")
                st.rerun()
            except Exception as e:
                st.error("❌ فشل الإرسال")
        else:
            st.warning("برجاء ملء الاسم والرسالة")

    st.divider()
    st.markdown("### 💜 دفتر المهنئين:")

    try:
        wishes = db.collection("wishes").order_by("time", direction=firestore.Query.DESCENDING).limit(10).get()
        if not wishes:
            st.info("كن أول المهنئين! ✨")
        else:
            for w in wishes:
                d = w.to_dict()
                st.markdown(f"""
                <div style="background:#f9f9f9; padding:10px; border-radius:10px; margin-bottom:10px; direction:rtl;">
                    <b>{d.get('name')}</b>: {d.get('message')}
                </div>
                """, unsafe_allow_html=True)
    except:
        st.write("جاري تحميل التهاني...")

    if st.button("رجوع"):
        st.session_state.opened = False
        st.rerun()