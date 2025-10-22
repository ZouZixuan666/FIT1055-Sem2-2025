import streamlit as st
import random
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="FaceABC Ethical Facial Recognition", layout="wide")

# ---- Session Setup ----
if "logs" not in st.session_state:
    st.session_state.logs = []
if "complaints" not in st.session_state:
    st.session_state.complaints = []
if "incident_counter" not in st.session_state:
    st.session_state.incident_counter = 1000
if "customer_image" not in st.session_state:
    st.session_state.customer_image = None  # store uploaded face

THRESHOLD = 0.85
base_path = os.path.dirname(__file__)
db_img = os.path.join(base_path, "static", "database.png")


# ---- Helper Functions ----
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


# ---- Sidebar Navigation ----
st.sidebar.title("📋 FaceABC Menu")
page = st.sidebar.radio("Go to:", [
    "Camera Dashboard",
    "Alarm & Review",
    "Human Review Board",
    "System Logs",
    "User Complaint Portal",
    "Complaint Review"
])
st.sidebar.markdown("---")
st.sidebar.info("Logged in as: **Staff - Mike**")

# ---- PAGE 1: Camera Dashboard ----
if page == "Camera Dashboard":
    st.title("🎥 Camera One – Live Feed Simulation")
    uploaded_file = st.file_uploader("Upload camera frame:", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        # Store uploaded file so we can use it later
        st.session_state.customer_image = uploaded_file
        st.image(uploaded_file, caption="Live Camera Feed", use_container_width=True)

        confidence = random.uniform(0.2, 0.99)
        st.metric("AI Confidence Score", f"{confidence:.2f}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Simulate Recognition"):
                if confidence >= THRESHOLD:
                    st.warning("⚠️ High Confidence Detected! Alarm Triggered Automatically.")
                    incident_id = add_log("Potential Match", "Auto Alarm Raised", confidence)
                    st.session_state["alarm_confidence"] = confidence
                    st.session_state["current_incident"] = incident_id
                    st.info(f"Incident recorded: {incident_id}")
                else:
                    st.success("✅ Low confidence - No action taken. Data deleted for privacy.")
                    add_log("Scan Complete", "No Action", confidence)
        with col2:
            if st.button("🚨 Raise Alarm Manually (Testing)"):
                confidence = 0.87
                incident_id = add_log("Manual Alarm Triggered", "Testing Alarm", confidence)
                st.session_state["alarm_confidence"] = confidence
                st.session_state["current_incident"] = incident_id
                st.warning(f"Manual alarm triggered! Incident ID: {incident_id}")

    else:
        st.info("Please upload a camera image to begin.")
    st.markdown("---")
    st.write(f"📊 Total logs recorded: {len(st.session_state.logs)}")

# ---- PAGE 2: Alarm & Review ----
elif page == "Alarm & Review":
    st.title("🚨 Active Alarms")
    if "alarm_confidence" in st.session_state:
        confidence = st.session_state["alarm_confidence"]
        incident_id = st.session_state.get("current_incident", "N/A")
        st.warning(f"Alarm raised! Incident ID: {incident_id} | Confidence: {confidence:.2f}")
        if st.button("Open Human Review Dashboard"):
            st.session_state["review_confidence"] = confidence
            st.session_state["review_incident"] = incident_id
            add_log("Alarm Acknowledged", "Audit Opened", confidence)
            st.success(f"Redirected to Human Review Board → (Incident {incident_id})")
    else:
        st.info("No active alarms at this moment.")

# ---- PAGE 3: Human Review ----
elif page == "Human Review Board":
    st.title("🧍 Human-in-the-Loop Decision Dashboard")
    st.markdown("Compare the detected customer with database record and decide ethically.")

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

    confidence = st.session_state.get("review_confidence", random.uniform(0.75, 0.95))
    incident_id = st.session_state.get("review_incident", generate_incident_id())
    st.metric("System Confidence", f"{confidence:.2f}")
    st.info(f"Incident ID: {incident_id}")

    decision = st.radio("Decision:", ["Approve Match", "Reject", "Send to Review Board"])

    if st.button("Submit Decision"):
        add_log("Human Review", decision, confidence, "Reviewer", incident_id)
        if decision == "Approve Match":
            st.error("🚨 Match Approved – Alert triggered.")
        elif decision == "Reject":
            st.success("✅ False Positive – Cleared and logged.")
        else:
            st.warning("🕵️ Case Escalated to Review Board.")
        st.success(f"Decision recorded successfully for {incident_id}.")

# ---- PAGE 4: Logs ----
elif page == "System Logs":
    st.title("📑 FaceABC Transparency Logs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df)
    else:
        st.info("No system logs yet.")

# ---- PAGE 5: Complaint Portal ----
elif page == "User Complaint Portal":
    st.title("💬 Submit Complaint – FaceABC Fairness System")
    user = st.text_input("Your Name:")
    contact = st.text_input("Contact Number:")
    incident_id = st.text_input("Incident ID (e.g., INC-1001):")
    text = st.text_area("Describe your issue:")
    if st.button("Submit Complaint"):
        if user and contact and incident_id and text:
            add_complaint(user, contact, incident_id, text)
            st.success("✅ Complaint submitted successfully. Our review board will respond soon.")
        else:
            st.warning("Please fill out all fields before submitting.")

# ---- PAGE 6: Complaint Review ----
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

            # Show both images for context
            if st.session_state.customer_image:
                st.image(st.session_state.customer_image, caption="Customer (From Incident)")
            st.image(db_img, caption="Database Record")

            action = st.radio(f"Action for Complaint #{i+1}",
                              ["None", "Confirm Error & Compensate", "Dismiss Complaint"],
                              key=f"complaint_{i}")

            if st.button(f"Submit Decision for #{i+1}"):
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
