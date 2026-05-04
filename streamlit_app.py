# -*- coding: utf-8 -*-
"""
Created on Sun May  4 03:52:14 2026
@author: SajjadHussain
"""
import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import zipfile
import io
import re
import smtplib
from email.mime.text import MIMEText

# --- 1. CONFIGURATION & SESSION STATE ---
st.set_page_config(
    page_title="ProPDF Intelligence | Professional PDF Tools",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ADSENSE PLACEHOLDER: When you get your code from Google in 4-5 months, 
# you will paste the <script> tag inside this function.
def inject_adsense():
    # Example: st.components.v1.html(""" <script async src="..."></script> """, height=0)
    pass

if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

def set_page(page_name):
    st.session_state.page = page_name

# --- 2. CORE ENGINES ---

def send_contact_email(user_name, user_email, user_message):
    """Sends contact form data via SMTP using the professional domain email."""
    # Updated to your new professional admin email
    admin_email = "admin@propdfintelligence.com"
    # Note: Ensure your SMTP provider (Gmail/Outlook/Host) is configured for this address
    # FETCH SECURELY FROM STREAMLIT SECRETS
    app_password = st.secrets["EMAIL_PASSWORD"]
    
    msg_content = f"New Support Request from ProPDFIntelligence.com:\n\nName: {user_name}\nEmail: {user_email}\n\nMessage:\n{user_message}"
    msg = MIMEText(msg_content)
    msg['Subject'] = f"ProPDF Support Ticket: {user_name}"
    msg['From'] = admin_email
    msg['To'] = admin_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(admin_email, app_password)
            server.sendmail(admin_email, admin_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Mail Delivery Failed: {e}")
        return False

def resize_pdf_smart(input_bytes, target_kb, start_quality):
    target_bytes = target_kb * 1024
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    current_pdf = doc.tobytes(garbage=4, deflate=True, clean=True)
    if len(current_pdf) > target_bytes:
        test_quality = start_quality
        while len(current_pdf) > target_bytes and test_quality >= 10:
            new_doc = fitz.open()
            zoom = test_quality / 100
            mat = fitz.Matrix(zoom, zoom)
            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("jpg")
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(page.rect, stream=img_data)
            current_pdf = new_doc.tobytes(garbage=4, deflate=True)
            new_doc.close()
            test_quality -= 10
    doc.close()
    return current_pdf

def audit_document(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    total_words, total_chars, page_stats = 0, 0, []
    for i, page in enumerate(doc):
        text = page.get_text()
        words = len(re.findall(r'\w+', text))
        chars = len(text)
        total_words += words
        total_chars += chars
        page_stats.append({"Page": i+1, "Words": words, "Chars": chars})
    doc.close()
    return {"total_words": total_words, "total_chars": total_chars, "details": page_stats}

# --- 3. UI STYLING ---
def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        .stApp {
            background-color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }

        .service-card {
            background: white; 
            border-radius: 12px; 
            padding: 24px; 
            min-height: 200px;
            border: 1px solid #e2e8f0; 
            transition: all 0.25s ease-in-out;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            margin-bottom: 10px;
        }
        .service-card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 12px 20px -10px rgba(37, 99, 235, 0.15); 
            border-color: #2563eb; 
        }
        .service-card h3 { 
            color: #0f172a; 
            font-size: 1.15rem; 
            font-weight: 700; 
            margin-bottom: 12px;
            display: flex;
            align-items: center;
        }
        .service-card p { color: #64748b; font-size: 0.9rem; line-height: 1.5; }

        .stButton > button {
            background: #2563eb; 
            color: white !important; 
            border-radius: 8px !important;
            font-weight: 600; 
            letter-spacing: -0.01em;
            transition: 0.2s;
            border: none;
            width: 100%;
        }
        .stButton > button:hover { 
            background: #1d4ed8; 
            box-shadow: 0 4px 12px rgba(37,99,235,0.2); 
        }

        .footer { 
            text-align: center; 
            padding: 30px 0; 
            color: #94a3b8; 
            font-size: 0.8rem; 
            border-top: 1px solid #e2e8f0; 
            margin-top: 60px; 
        }
        </style>
    """, unsafe_allow_html=True)

apply_styles()
inject_adsense()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #0f172a; margin-bottom: 0;'>🛡️ ProPDF Intelligence</h2>", unsafe_allow_html=True)
    st.caption("Strategic Document Hub Pro")
    st.divider()
    
    st.subheader("Navigation")
    main_menu = ["Dashboard", "AI Document Summary", "Resize PDF to KB", "Merge PDFs", "Extract Pages", "Split PDF", "Secure & Encrypt", "Unlock PDF", "Document Audit"]
    
    if st.session_state.page in main_menu:
        current_index = main_menu.index(st.session_state.page)
    else:
        current_index = 0
        
    choice = st.selectbox("Select Tool", main_menu, index=current_index)
    if choice != st.session_state.page and st.session_state.page in main_menu:
        set_page(choice)
        st.rerun()
    
    st.divider()
    st.subheader("AI Configuration")
    with st.expander("🔑 Get a Gemini API Key"):
        st.write("1. Sign in to Google AI Studio.")
        st.link_button("Create Free Key", "https://aistudio.google.com/app/apikey")
        
    user_api_key = st.text_input("Enter API Key", type="password", help="Your key is only used for this session.")
    
    st.divider()
    if st.button("🏢 About Us"): set_page("About Us"); st.rerun()
    if st.button("🔒 Privacy Policy"): set_page("Privacy Policy"); st.rerun()
    if st.button("⚖️ Terms of Service"): set_page("Terms of Service"); st.rerun()
    if st.button("✉️ Contact Us"): set_page("Contact"); st.rerun()

# --- 5. PAGE ROUTING & GLOBAL NAVIGATION ---

if st.session_state.page != "Dashboard":
    if st.button("← Back to Dashboard"):
        set_page("Dashboard"); st.rerun()
    st.divider()

# --- DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.title("Strategic PDF Hub")
    st.markdown("<p style='color:#64748b; font-size:1.1rem;'>Intelligent document manipulation and automated synthesis tools at www.propdfintelligence.com.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown('<div class="service-card"><h3>📉 Smart PDF Resizer</h3><p>Shrink large reports to hit strict portal limits while maintaining visual integrity.</p></div>', unsafe_allow_html=True)
        st.button("Open Resizer", on_click=set_page, args=("Resize PDF to KB",), key="d1")
        
        st.markdown('<div class="service-card"><h3>🔓 Unlock PDF</h3><p>Remove passwords and restrictions for easy editing or digital archival.</p></div>', unsafe_allow_html=True)
        st.button("Open Unlocker", on_click=set_page, args=("Unlock PDF",), key="d2")
        
    with col2:
        st.markdown('<div class="service-card"><h3>🤖 AI PDF Audit</h3><p>Leverage Gemini AI to summarize reports and extract key metrics instantly.</p></div>', unsafe_allow_html=True)
        st.button("Open AI Audit", on_click=set_page, args=("AI Document Summary",), key="d3")
        
        st.markdown('<div class="service-card"><h3>✂️PDF Page Master</h3><p>Isolate specific ranges or split massive files into modular components.</p></div>', unsafe_allow_html=True)
        st.button("Open Page Master", on_click=set_page, args=("Extract Pages",), key="d4")
        
    with col3:
        st.markdown('<div class="service-card"><h3>🔗 PDF Fusion Merge</h3><p>Combine multiple data exports into a single consolidated professional PDF.</p></div>', unsafe_allow_html=True)
        st.button("Open Merger", on_click=set_page, args=("Merge PDFs",), key="d5")
        
        st.markdown('<div class="service-card"><h3>📊 Pro Audit PDF</h3><p>Forensic analysis of word counts, metadata, and character density.</p></div>', unsafe_allow_html=True)
        st.button("Open Audit", on_click=set_page, args=("Document Audit",), key="d6")

# --- ABOUT US ---
elif st.session_state.page == "About Us":
    st.title("🏢 About ProPDF Intelligence")
    st.markdown("""
    ### The Vision Behind the Intelligence
    **ProPDF Intelligence** was born out of a simple necessity: the need for a document management tool that doesn’t just "handle" files, but understands them. We built this suite to bridge the gap between static document storage and **intelligent data synthesis**.

    ### What Sets Us Apart?
    Unlike standard PDF utilities, ProPDF Intelligence integrates state-of-the-art Large Language Models (LLMs) with forensic-level document manipulation.

    #### 1. AI-Driven Analytics
    Leveraging the power of **Gemini 1.5 Flash**, we transform long-form PDFs into actionable intelligence. Our "AI Audit" feature doesn't just summarize; it identifies core data points, saving hours of manual review.

    #### 2. Forensic Precision
    Our **Document Audit** engine provides a deep-dive into structural integrity. From character density analysis to word-counts and metadata tracking, we provide total transparency for your documents.

    #### 3. Smart Optimization
    Standard compression often destroys quality. Our **Smart Target Resizer** uses iterative logic to shrink your files to specific KB targets while maintaining professional-grade clarity.

    ### Core Capabilities
    *   **Fusion Merging:** Seamlessly consolidate multiple data streams into a single report.
    *   **Security & Encryption:** Industry-standard protection to ensure your data remains yours.
    *   **Privacy-First Processing:** By utilizing in-memory processing, your documents are never stored permanently on our servers.
    """, unsafe_allow_html=True)
    st.info("Built with passion for technical automation and data excellence by ProPDF Intelligence Team.")

# --- PRIVACY POLICY ---
elif st.session_state.page == "Privacy Policy":
    st.title("🔒 Privacy Policy & Data Integrity")
    st.markdown("""
    ### Our Commitment to Your Privacy
    At **ProPDF Intelligence**, we believe that your documents are your business. Our platform is engineered with a **Privacy-First** architecture.

    ### 1. Data Processing (In-Memory)
    *   **Live Session Processing:** All PDF manipulations are performed **in-memory**. Once you close your browser or refresh, data is purged from temporary memory.
    *   **No Database Storage:** We do not maintain a database of your uploaded documents.

    ### 2. AI Analysis & Third-Party API
    *   **Gemini API:** Text content is sent securely to Google’s Gemini API for processing only if you provide your own API key.
    *   **End-to-End Encryption:** Data transmitted to the AI engine is encrypted in transit.

    ### 3. Contact Form & Communications
    *   We collect your name and email address solely to respond to support tickets via **admin@propdfintelligence.com**. Data is never sold.

    ### 4. Security Measures
    *   **SSL/TLS Encryption:** All traffic between your browser and our tool is encrypted.
    *   **Session Isolation:** Each user session is isolated; users cannot access each other's data.

    ### 5. User Responsibilities
    *   **API Key Safety:** Your API key is stored only in your local session state. Never share your key.
    *   **Sensitive Data:** Users should exercise caution when uploading highly sensitive PII.

    *Last Updated: May 2026*
    """, unsafe_allow_html=True)
    st.success("✅ Your files stay in your session. We don't store them. We don't see them.")

# --- TERMS OF SERVICE ---
elif st.session_state.page == "Terms of Service":
    st.title("⚖️ Terms of Service")
    st.markdown("""
    ### 1. Acceptance of Terms
    By accessing **ProPDF Intelligence**, you agree to be bound by these terms. This platform is provided "as-is" for professional document manipulation.

    ### 2. User Responsibility
    Users are solely responsible for the content of the documents they upload. You must ensure you have the legal right to modify or analyze the files processed through our tools.

    ### 3. Usage Limitations
    *   You may not use this service for any illegal activities or to process restricted government documents.
    *   Automated "scraping" or bulk-requesting our AI Audit tool is prohibited.

    ### 4. Limitation of Liability
    ProPDF Intelligence is a processing utility. We are not liable for any data loss or errors resulting from the use of our PDF optimization or AI summary engines.
    
    *Effective Date: May 2026*
    """, unsafe_allow_html=True)

# --- CONTACT ---
elif st.session_state.page == "Contact":
    st.title("Secure Support")
    st.write("For official inquiries: admin@propdfintelligence.com")
    with st.form("contact_form"):
        u_name = st.text_input("Name")
        u_email = st.text_input("Email")
        u_msg = st.text_area("Support Request")
        if st.form_submit_button("Submit Ticket"):
            if u_name and u_email and u_msg:
                if send_contact_email(u_name, u_email, u_msg):
                    st.success("Ticket Sent! We will respond shortly via admin@propdfintelligence.com.")
            else:
                st.warning("All fields are required.")

# --- TOOL PAGES ---
elif st.session_state.page == "AI Document Summary":
    st.title("🤖 AI Report Intelligence")
    if not user_api_key:
        st.info("💡 To use AI features, please enter your Gemini API Key in the sidebar.")
    up_file = st.file_uploader("Analyze Report", type="pdf")
    if up_file and st.button("Generate KPI Summary"):
        if not user_api_key: st.error("API Key missing.")
        else:
            with st.spinner("AI is auditing the document..."):
                genai.configure(api_key=user_api_key)
                doc = fitz.open(stream=up_file.read(), filetype="pdf")
                text = "".join([p.get_text() for p in doc])
                model = genai.GenerativeModel('gemini-1.5-flash')
                st.markdown(model.generate_content(f"Summarize main data points: {text[:15000]}").text)

elif st.session_state.page == "Resize PDF to KB":
    st.title("📉 Smart Target Resizer")
    up_file = st.file_uploader("Upload PDF", type="pdf")
    c_a, c_b = st.columns(2)
    target = c_a.number_input("Target KB", 50, 5000, 500)
    q_init = c_b.slider("Initial Quality %", 10, 100, 80)
    if up_file and st.button("Compress to Target"):
        out = resize_pdf_smart(up_file.read(), target, q_init)
        st.success(f"Optimized Size: {len(out)/1024:.1f} KB")
        st.download_button("📥 Download PDF", out, "optimized.pdf")

elif st.session_state.page == "Document Audit":
    st.title("📊 Document Analytics")
    up_file = st.file_uploader("Audit PDF", type="pdf")
    if up_file and st.button("Run Forensic Audit"):
        res = audit_document(up_file.getvalue())
        st.metric("Total Words Found", f"{res['total_words']:,}")
        st.dataframe(res["details"], use_container_width=True)

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        <p>© 2026 ProPDF Intelligence | <a href="http://www.propdfintelligence.com" target="_blank">www.propdfintelligence.com</a></p>
        <p>Support: admin@propdfintelligence.com</p>
    </div>
""", unsafe_allow_html=True)