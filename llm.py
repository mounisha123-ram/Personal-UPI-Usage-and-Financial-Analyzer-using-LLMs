import os
import time
import random
import textwrap
import streamlit as st
import PyPDF2
import google.generativeai as genai

# Set up Google Gemini API Key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Streamlit UI setup
st.set_page_config(page_title="AI Personal Finance Assistant", page_icon="💰", layout="wide")

# Background Image URL
background_url = "https://media.licdn.com/dms/image/v2/D5612AQE5ekG3lqgyRw/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1680216784984?e=2147483647&v=beta&t=0ZIXhM9dsA1tuVI0sJjQU4bysnmi5Det7FlWonVeQeU"

# ============ Main Title + Subtitle + Uploader Aligned ===============
st.markdown("""
<div style='text-align: center; padding-top: 20px;'>
    <h1 style='color: black; text-shadow: 2px 2px 5px rgba(76, 175, 80, 0.4); -webkit-text-stroke: 0.8px white;'>
        🤖💸 AI-Powered Personal Finance Assistant
    </h1>
    <p style='font-size: 18px; color: black;'>Upload your UPI Transaction PDF for smart Financial Insights 📊</p>
</div>
""", unsafe_allow_html=True)

# Add vertical space
st.markdown("<br>", unsafe_allow_html=True)

# Center-aligned uploader using columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("📂 Upload PDF File", type=["pdf"], help="Only PDF files are supported")

# ============ Conditional Background CSS ===============
if not uploaded_file:
    css = f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
else:
    css = """
    <style>
    .stApp {
        background-color: white !important;
        background-image: none !important;
    }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

# ============ Styling ===============
style_css = """
<style>
.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: bold;
    color: #4CAF50;
    text-shadow: 2px 2px 5px rgba(76, 175, 80, 0.4);
    -webkit-text-stroke: 0.8px white;
}
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #ddd;
    margin-bottom: 20px;
}
.stButton button {
    background: linear-gradient(to right, #4CAF50, #388E3C);
    color: white;
    font-size: 18px;
    padding: 10px 20px;
    border-radius: 8px;
    transition: 0.3s;
    border: none;
}
.stButton button:hover {
    background: linear-gradient(to right, #388E3C, #2E7D32);
}
.result-card {
    background: rgba(0, 150, 136, 0.1);
    color: black;
    font-weight: bold;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    box-shadow: 0px 2px 8px rgba(0, 150, 136, 0.2);
}
.success-banner {
    background-color: black;        
    color: white;                  
    padding: 15px;
    font-size: 18px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    margin-top: 15px;
    box-shadow: 0px 2px 8px rgba(255, 255, 255, 0.2);  /* Optional white glow */
}
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# ============ Sidebar Instructions ===============
st.sidebar.title("ℹ️ How to Use This Tool?")
st.sidebar.write("- 📂 Upload your UPI Transaction History PDF file.")
st.sidebar.write("- 🧠 AI will analyze your transactions automatically.")
st.sidebar.write("""
- 📊 You'll receive a detailed financial report including:
    - 💸 Income & Expenses  
    - 💰 Savings Percentage  
    - 📂 Category-Wise Spending  
    - 💡 Smart Budgeting Advice
""")
st.sidebar.write("- Use this analysis to plan your finances effectively.")


# ============ Extract Text ===============
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ============ Prompt ===============
def build_financial_prompt(transaction_text: str) -> str:
    return textwrap.dedent(f"""
    You are a financial analyst embedded in an AI-powered UPI savings and budget tracking assistant.
    Below is a full UPI or bank transaction statement text extracted from a PDF:
    {transaction_text}

    Your job is to analyze this thoroughly and generate a clean, professional financial report with clear sections and insights.

    Focus Areas:
    # 📊 AI-Powered Financial Report Prompt
        ---

        ## 📌 TRANSACTION SUMMARY

        - ✅ Total number of transactions  
        - ✅ Total Incoming (Credits) and Outgoing (Debits) in ₹  
        - ✅ Net Cash Flow = Income – Expenses  
        - ✅ Average Transaction Size (₹)  
        - ✅ Peak (Max) and Minimum Transaction Amounts  
        - ✅ Median Transaction Value  
        - ✅ Number of Days with at least one transaction  
        - ✅ Days with **zero** transactions  

        ---

        ## 🔍 DETAILED SPENDING PATTERN ANALYSIS

        - 📅 Daily & Weekly **Average Spend** (₹)  
        - 🕒 Busiest Transaction Days & Hours (weekday + time)  
        - 🔁 High-Frequency Spending Detection  
        - 💸 Amount-Based Categorization:  
        - Micro (₹1–₹50)  
        - Small (₹51–₹200)  
        - Medium (₹201–₹999)  
        - Large (₹1000+)  
        - 🥇 Top 3 **Largest Expense Transactions**  

        ---

        ## 📈 TEMPORAL TREND IDENTIFICATION

        - 📆 Monthly Breakdown:
        - Income & Spending Table  
        - Monthly Savings Estimation = Income – Expense  
        - Month-over-Month (MoM) Variance  
        - 🔥 Time-Based Patterns:
        - Heatmap of Days & Times with Most Transactions (textual insight)  
        - Seasonal Irregularities (end-of-month spikes, festive surges)  

        ---

        ## 🏷️ TRANSACTION CATEGORIZATION (Based on Recipient/Merchant Name)

        Categories:
        - 🍽️ Food & Dining  
        - 🛒 Grocery & Essentials  
        - ⛽ Transport/Fuel  
        - 💡 Bill Payments  
        - 🛍️ Shopping (E-com + Retail)  
        - 📺 Subscriptions & Entertainment  
        - 🏥 Medical/Health  
        - 🎓 Education  
        - 👤 Person-to-Person Transfers  
        - ❓ Miscellaneous  

        For each category:
        - ✅ Total Number of Transactions  
        - ✅ Total Spend (₹)  
        - ✅ % of Total Expense  
        - ✅ Average Transaction Size  
        - ✅ Peak Transaction  
        - ✅ Most Frequent Merchant  
        - ⚠️ Impulsive/Non-Essential Categories  

        ---

        ## 🤝 RECIPIENT ANALYSIS

        - 🏆 Top 10 Most Paid Recipients (by count and amount ₹)  
        - 🧍‍♂️ Personal vs 🏢 Institutional Split  
        - 📉 High-Frequency Low-Value Recipients  
        - 💰 One-Time High-Value Recipients  
        - 🕒 Time Patterns Linked to Each Top Recipient  
        - 🔁 Recurring vs 🔹 Unique Recipients  

        ---

        ## 💼 INCOME ANALYSIS

        - 🧾 Identify Income Sources (keywords: **salary**, **bonus**, **cashback**, etc.)  
        - ✅ Total Income Volume (₹)  
        - 📅 Monthly Income Trend  
        - 🔄 Count of Distinct Income Sources  

        ---

        ## 🚨 WASTEFUL SPENDING ANALYSIS

        - 💸 Repeated Micro-Transactions (₹1–₹50)  
        - 🔁 Duplicate or Quick Re-Payments  
        - 😳 One-Off Unusual Large Payments  
        - 🤯 Impulsive/Unnecessary Spend Categories  
        - 🧊 Non-Essential Spend Patterns  
        - ⚠️ Total Potential Wasteful Spend (₹)  

        **Terms to Use:**  
        `Spending Leakage`, `Expense Redundancy`, `Low-Value Spend Index`, `Transactional Waste`

        ---

        ## 🤖 SMART RECOMMENDATION SYSTEM

        - 💡 Suggest Monthly Budget per Category  
        - ✅ Top 5 Personalized **Cost-Control Ideas**  
        - 🧠 Smart Automation Tips (like SIPs, bill reminders)  
        - 🛑 Flag Suspicious/Fraud Transactions (if any)  
        - 🐢 Lazy Saving Tips (round-ups, stash savings)  
        - 📊 **Financial Health Score** (Color-coded: Red → Green)  

        ---

        ## 📈 VISUALIZATION STRATEGY

        Highlight and annotate:
        - 📊 Notable Trends (e.g., spike in shopping, drop in fuel)  
        - 📅 Monthly Income vs Expense Trends  
        - 🏷️ Category-Wise Spend Distribution  
        - 💰 Savings Rate Over Time  
        - ⚠️ Anomalies or Outliers (festival spikes, refund bursts)  

        ---

        ## ✅ FINAL REPORT: FOCUS AREAS

        - 💵 **Total Income & Expenses Summary**  
        - 🗓️ **Monthly Trends** & Variances  
        - 🏷️ **Category-Wise Spend Breakdown**  
        - 💰 **Savings Rate Estimation**  
        - 🚨 **Noteworthy/Wasteful Spending Alerts**

        ---

        ### 💡 Personalized Financial Advice
        Provide:
        - 🔍 Actionable insights to improve saving
        - 🛑 Ways to reduce non-essential spending
        - 📊 Tips to optimize each budget category
        - ✅ Customized suggestions based on behavior

            Format the report neatly using markdown (use 📌, ✅, 💡, etc. to highlight points).
            """)

# ============ Gemini Model Call ===============
def generate_insights_with_retry(prompt, model_name="models/gemini-1.5-flash", max_retries=3):
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.warning(f"Attempt {attempt+1} failed: {e}")
            time.sleep(random.uniform(2, 4))
    st.error("🚫 Could not generate insights. Please try again later.")
    return None

# ============ Main App Logic ===============
if uploaded_file:
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded successfully!")

    with st.spinner("📓 Extracting text from document..."):
        extracted_text = extract_text_from_pdf(temp_path)

    if not extracted_text:
        st.error("⚠️ Text extraction failed. Please upload a text-based PDF.")
    else:
        progress_bar = st.progress(0)
        with st.spinner("🧠 Analyzing your financial behavior with Gemini AI..."):
            prompt = build_financial_prompt(extracted_text)
            insights = generate_insights_with_retry(prompt)
        progress_bar.progress(100)

        if insights:
            st.subheader("📊 Financial Insights Report")
            st.markdown(f'<div class="result-card"><b>📄 Analysis of: {uploaded_file.name}</b></div>', unsafe_allow_html=True)
            st.markdown(insights, unsafe_allow_html=True)
            st.markdown('<div class="success-banner">🎯 Your Financial Report is Ready! Let your data guide smarter decisions.💼</div>', unsafe_allow_html=True)
            st.snow()

    os.remove(temp_path)
