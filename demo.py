import streamlit as st
import random
import pandas as pd
from datetime import datetime
import os

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="FaceABC – Ethical Facial Recognition", layout="wide")

THRESHOLD = 0.85  # confidence threshold for automatic approval
base_path = os.path.dirname(__file__)
db_img = os.path.join(base_path, "static", "database.png")

# ---------------------------------------------------------
# SESSION STATE SETUP
# ---------------------------------------------------------
if "logs" not in st.session_state:
    st.session_state.logs = []
if "complaints" not in st.session_state:
    st.session_state.complaints = []
if "incident_counter" not in st.session_state:
    st.session_state.incident_counter = 1000
if "customer_image" not in st.session_state:
    st.session_state.customer_image = None
if "page" not in st.session_state:
    st.session_state.page = "Camera Dashboard"

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def generate_incident_id():
    st.session_state.incident_counter += 1
    return f"INC-{st.session_state.incident_counter}"

def add_log(event, action, confidence, actor="System", incident_id=None):
    if not incident_id:
        incident_id = generate_incident_id()
    st.session_state.logs.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Incident ID": incident_id,
        "Event": event,
        "Action": action,
        "Confidence": f"{confidence:.2f}",
        "Handled By": actor
    })
    return incident_id

def add_complaint(user, contact, incident_id, text):
    st.session_state.complaints.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User": user,
        "Contact": contact,
        "Incident ID": incident_id,
        "Complaint": text,
        "Status": "Pending"
    })

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
page = st.sidebar.radio("Go to:", [
    "Camera Dashboard",
    "Human Review Board",
    "System Logs",
    "User Complaint Portal",
    "Complaint Review"
], key="sidebar_nav")

st.sidebar.markdown("---")
st.sidebar.info("Logged in as: **Staff – Mike**")

# ---------------------------------------------------------
# PAGE 1 – CAMERA DASHBOARD
# ---------------------------------------------------------
if page == "Camera Dashboard":
    st.title("🎥 Camera One – Live Feed Simulation")
    st.markdown("Upload an image to simulate the live camera feed.")

    uploaded_file = st.file_uploader("Upload camera frame:", type=["png", "jpg", "jpeg"], key="camera_upload")

    if uploaded_file:
        st.session_state.customer_image = uploaded_file
        st.image(uploaded_file, caption="Live Camera Feed", use_container_width=True)

        # Random confidence score to simulate detection
        confidence = random.uniform(0.2, 0.99)
        st.metric("AI Confidence Score", f"{confidence:.2f}")

        # Visual color bar indicator
        if confidence >= 0.85:
            st.progress(confidence)
            st.success("✅ System confident with match.")
        elif confidence >= 0.5:
            st.progress(confidence)
            st.warning("⚠️ Medium confidence – human verification suggested.")
        else:
            st.progress(confidence)
            st.error("❌ Low confidence – requires immediate human review.")

        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Run Face Check", key="btn_run_check"):
                incident_id = generate_incident_id()
                st.session_state["current_incident"] = incident_id
                st.session_state["alarm_confidence"] = confidence

                if confidence < THRESHOLD:
                    st.warning(f"⚠️ Confidence {confidence:.2f} < {THRESHOLD}. Redirecting for human review.")
                    add_log("Uncertain Match", "Human Review Required", confidence, incident_id=incident_id)
                    st.session_state.page = "Human Review Board"
                    st.rerun()
                else:
                    st.success(f"✅ Confidence {confidence:.2f} ≥ {THRESHOLD}. Logged automatically.")
                    add_log("Match Logged", "High Confidence", confidence, incident_id=incident_id)

        with col2:
            if st.button("🚨 Force Audit (Testing)", key="btn_force"):
                confidence = 0.45
                incident_id = generate_incident_id()
                st.session_state["current_incident"] = incident_id
                st.session_state["alarm_confidence"] = confidence
                add_log("Manual Trigger", "Forced Human Review", confidence, incident_id=incident_id)
                st.session_state.page = "Human Review Board"
                st.rerun()
    else:
        st.info("Please upload a camera image to start the recognition simulation.")

# ---------------------------------------------------------
# PAGE 2 – HUMAN REVIEW BOARD
# ---------------------------------------------------------
elif page == "Human Review Board":
    st.title("🧍 Human-in-the-Loop Decision Dashboard")
    st.markdown("Compare the detected customer image with a database record and decide ethically.")

    if st.session_state.customer_image:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Customer Image (Uploaded)")
            st.image(st.session_state.customer_image, caption="Detected individual")
        with col2:
            st.subheader("Database Match")
            st.image(db_img, caption="Database record")
    else:
        st.warning("⚠️ No uploaded image found. Please upload one on the Camera Dashboard first.")

    confidence = st.session_state.get("alarm_confidence", random.uniform(0.2, 0.99))
    incident_id = st.session_state.get("current_incident", generate_incident_id())
    st.metric("System Confidence", f"{confidence:.2f}")
    st.info(f"Incident ID: {incident_id}")

    decision = st.radio("Decision:", ["Approve Match", "Reject", "Send to Review Board"], key="review_decision")

    if st.button("Submit Decision", key="btn_submit_decision"):
        add_log("Human Review", decision, confidence, "Reviewer", incident_id)
        if decision == "Approve Match":
            st.error("🚨 Match Approved – alert triggered.")
        elif decision == "Reject":
            st.success("✅ False Positive – cleared and logged.")
        else:
            st.warning("🕵️ Case Escalated to Review Board.")
        st.success(f"Decision recorded successfully for {incident_id}.")

# ---------------------------------------------------------
# PAGE 3 – SYSTEM LOGS
# ---------------------------------------------------------
elif page == "System Logs":
    st.title("📑 FaceABC Transparency Logs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df)
        st.download_button("⬇️ Download Logs as CSV", df.to_csv(index=False).encode("utf-8"),
                           file_name="faceabc_logs.csv", mime="text/csv", key="download_logs")
    else:
        st.info("No logs available yet.")

# ---------------------------------------------------------
# PAGE 4 – USER COMPLAINT PORTAL
# ---------------------------------------------------------
elif page == "User Complaint Portal":
    st.title("💬 Submit Complaint – FaceABC Fairness System")
    st.markdown("If you believe you were wrongly identified, please submit a complaint below.")
    user = st.text_input("Your Name:", key="complaint_name")
    contact = st.text_input("Contact Number:", key="complaint_contact")
    incident_id = st.text_input("Incident ID (e.g., INC-1001):", key="complaint_incident")
    text = st.text_area("Describe your issue:", key="complaint_text")

    if st.button("Submit Complaint", key="btn_submit_complaint"):
        if user and contact and incident_id and text:
            add_complaint(user, contact, incident_id, text)
            st.success("✅ Complaint submitted successfully. Our ethics team will review it soon.")
        else:
            st.warning("Please fill out all fields before submitting.")

# ---------------------------------------------------------
# PAGE 5 – COMPLAINT REVIEW BOARD
# ---------------------------------------------------------
elif page == "Complaint Review":
    st.title("🧾 Complaint Review Board – Staff Access Only")
    pending = [c for c in st.session_state.complaints if c["Status"] == "Pending"]

    if pending:
        for i, comp in enumerate(pending):
            st.markdown(f"### Complaint #{i+1}")
            st.write(f"🕒 Time: {comp['Time']}")
            st.write(f"👤 User: {comp['User']} ({comp['Contact']})")
            st.write(f"📄 Incident ID: {comp['Incident ID']}")
            st.write(f"📝 {comp['Complaint']}")

            if st.session_state.customer_image:
                st.image(st.session_state.customer_image, caption="Customer Image (From Incident)")
            st.image(db_img, caption="Database Record")

            action = st.radio(f"Action for Complaint #{i+1}",
                              ["None", "Confirm Error & Compensate", "Dismiss Complaint"],
                              key=f"complaint_action_{i}")

            if st.button(f"Submit Decision for #{i+1}", key=f"btn_comp_{i}"):
                if action == "Confirm Error & Compensate":
                    comp["Status"] = "Compensated"
                    add_log("Complaint Reviewed", "Compensation Issued", 0, "Ethics Board", comp["Incident ID"])
                    st.success(f"✅ Compensation approved for {comp['Incident ID']}.")
                elif action == "Dismiss Complaint":
                    comp["Status"] = "Dismissed"
                    add_log("Complaint Reviewed", "Dismissed", 0, "Ethics Board", comp["Incident ID"])
                    st.warning(f"Complaint dismissed for {comp['Incident ID']}.")
    else:
        st.info("No pending complaints at this time.")
