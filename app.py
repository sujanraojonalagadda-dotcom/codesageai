import streamlit as st
import os
import re
from openai import OpenAI

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}
code, pre, .stCode {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hero gradient header */
.hero-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 2rem 2.5rem 1.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(100,80,255,0.35) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-header h1 {
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.3rem;
    letter-spacing: -1px;
}
.hero-header p {
    color: #a89fce;
    font-size: 1.05rem;
    margin: 0;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1640 100%);
}
[data-testid="stSidebar"] * {
    color: #d4cff0 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* Feature badge */
.feature-badge {
    display: inline-block;
    background: rgba(100, 80, 255, 0.18);
    border: 1px solid rgba(100, 80, 255, 0.4);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.82rem;
    margin: 3px 2px;
    color: #c4b8ff !important;
}

/* Tab tweaks */
button[data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600;
}

/* Footer */
.footer {
    text-align: center;
    padding: 1.5rem;
    margin-top: 3rem;
    color: #7a7a9a;
    font-size: 0.9rem;
    border-top: 1px solid #2a2550;
}
</style>
""", unsafe_allow_html=True)

# ── OpenAI client ─────────────────────────────────────────────────────────────
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# ── Helper: call AI ───────────────────────────────────────────────────────────
def call_ai(prompt: str, system: str = "You are an expert software engineer and coding tutor.") -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# ── Language detection ────────────────────────────────────────────────────────
def detect_language(code: str) -> str:
    code_lower = code.lower()
    if any(kw in code_lower for kw in ["def ", "import ", "print(", "elif ", "lambda ", "self."]):
        return "Python"
    if any(kw in code for kw in ["#include", "printf", "scanf", "int main"]):
        return "C"
    if any(kw in code for kw in ["public class", "System.out.println", "public static void main"]):
        return "Java"
    if any(kw in code_lower for kw in ["function ", "const ", "let ", "var ", "console.log", "=>"]):
        return "JavaScript"
    if any(kw in code_lower for kw in ["func ", "fmt.print", "package main"]):
        return "Go"
    if any(kw in code_lower for kw in ["fn ", "println!", "let mut", "use std"]):
        return "Rust"
    if any(kw in code_lower for kw in ["<html", "<div", "<body", "<!doctype"]):
        return "HTML"
    return "Unknown"

# ── Core AI functions ─────────────────────────────────────────────────────────
def analyze_code(code: str, language: str) -> str:
    prompt = f"""Analyze this {language} code and identify issues.
For each issue, prefix with severity:
🔴 HIGH – for bugs/security issues
🟡 MEDIUM – for performance/logic issues
🟢 LOW – for style/quality issues

Format as bullet points. Be specific.

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt)


def fix_code(code: str, language: str) -> str:
    prompt = f"""Fix all bugs, security issues, and improve this {language} code.
Return ONLY the corrected code (no explanation, no markdown fences).

Code:
{code}"""
    return call_ai(prompt)


def generate_tests(code: str, language: str) -> str:
    prompt = f"""Generate comprehensive test cases for this {language} code.
Include:
1. Unit tests (normal cases)
2. Edge cases
3. Input/Output examples table

Format clearly with headers.

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt)


def tutor_explanation(code: str, language: str) -> str:
    system = (
        "You are CodeMentor AI 👨‍🏫, a friendly, encouraging coding tutor. "
        "Always start with appreciation, explain what went wrong, why it happens, "
        "how to fix it, and end with a pro tip. Use emojis, be beginner-friendly and warm."
    )
    prompt = f"""A student wrote this {language} code. Give them a warm, structured tutoring session.

Structure:
1. 👏 Appreciation – praise their effort
2. 🔍 What went wrong
3. 💡 Why it happens
4. 🛠 How to fix it (with corrected snippet)
5. 🚀 Pro tip

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt, system=system)


def explain_concept(code: str, language: str) -> str:
    prompt = f"""Explain the core programming concept demonstrated in this {language} code.
- Use simple plain English
- Include a real-life analogy
- Explain step by step
- Mention where this concept is used in real projects

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt)


def generate_practice_questions(code: str, language: str) -> str:
    prompt = f"""Based on the concept in this {language} code, generate practice problems:

🟢 EASY (2 problems)
🟡 MEDIUM (2 problems)
🔴 HARD (1 problem)

For each: problem statement + expected output hint.

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt)


def generate_quiz(code: str, language: str) -> str:
    prompt = f"""Create a 3-question multiple-choice quiz based on this {language} code.

For each question:
- Question text
- 4 options (A, B, C, D)
- ✅ Correct answer with brief explanation

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt)


def learning_tips(code: str, language: str) -> str:
    prompt = f"""Based on this {language} code, provide:

📌 BEST PRACTICES (3–4 points)
⚠️ COMMON MISTAKES to avoid (3 points)
📈 IMPROVEMENT TIPS for the developer (3 points)

Code:
```{language.lower()}
{code}
```"""
    return call_ai(prompt)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Code Assistant")
    st.markdown("*Learn • Build • Improve with AI*")
    st.markdown("---")
    st.markdown("### ✨ Features")
    features = [
        "🔍 Bug & Security Analysis",
        "🛠 Auto Code Fixer",
        "🧪 Test Case Generator",
        "👨‍🏫 AI Tutor (CodeMentor)",
        "📖 Concept Explainer",
        "🧠 Practice Problems",
        "❓ Auto Quiz Generator",
        "💡 Learning Tips",
        "🌐 Multi-language Support",
    ]
    for f in features:
        st.markdown(f'<span class="feature-badge">{f}</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🌐 Supported Languages")
    st.markdown("Python · C · Java · JavaScript · Go · Rust · HTML")
    st.markdown("---")
    st.caption("Powered by GPT-4o Mini · OpenAI")

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🤖 AI Code Assistant</h1>
    <p>Learn • Build • Improve with AI — your intelligent coding companion</p>
</div>
""", unsafe_allow_html=True)

# ── Code Input Section ────────────────────────────────────────────────────────
st.markdown("### 📝 Paste Your Code")

code_input = st.text_area(
    label="Code input",
    placeholder="# Paste your code here...\ndef greet(name):\n    print('Hello, ' + name)\n\ngreet('World')",
    height=220,
    label_visibility="collapsed",
)

# Language detection & dropdown
detected_lang = detect_language(code_input) if code_input.strip() else "Python"
lang_options = ["Python", "C", "Java", "JavaScript", "Go", "Rust", "HTML", "Unknown"]
default_idx = lang_options.index(detected_lang) if detected_lang in lang_options else 0

col_lang, col_spacer = st.columns([1, 3])
with col_lang:
    selected_language = st.selectbox(
        "🌐 Language",
        lang_options,
        index=default_idx,
    )

if code_input.strip():
    if detected_lang != "Unknown":
        st.info(f"🔎 Auto-detected language: **{detected_lang}**")
    else:
        st.warning("⚠️ Could not auto-detect language. Please select manually.")

st.markdown("---")

# ── Action Buttons ────────────────────────────────────────────────────────────
st.markdown("### ⚡ Actions")
b1, b2, b3, b4, b5 = st.columns(5)
run_analyze  = b1.button("📊 Analyze",     use_container_width=True)
run_fix      = b2.button("🛠 Fix Code",    use_container_width=True)
run_tests    = b3.button("🧪 Test Cases",  use_container_width=True)
run_tutor    = b4.button("👨‍🏫 AI Tutor",   use_container_width=True)
run_study    = b5.button("📚 Study",       use_container_width=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analysis",
    "🛠 Fixed Code",
    "🧪 Test Cases",
    "👨‍🏫 AI Tutor",
    "📚 Study Environment",
])

# ── Tab 1: Analysis ───────────────────────────────────────────────────────────
with tab1:
    st.markdown("## 📊 Code Analysis")
    st.markdown("Detects bugs, security issues, performance problems, and code quality issues.")
    st.markdown("---")
    if run_analyze:
        if not code_input.strip():
            st.warning("⚠️ Please paste some code before analyzing.")
        else:
            with st.spinner("🔍 Analyzing your code..."):
                result = analyze_code(code_input, selected_language)
            st.success("✅ Analysis complete!")
            st.markdown(result)
    else:
        st.info("👆 Click **📊 Analyze** to run analysis on your code.")

# ── Tab 2: Fixed Code ─────────────────────────────────────────────────────────
with tab2:
    st.markdown("## 🛠 Fixed Code")
    st.markdown("AI rewrites your code with bugs fixed and best practices applied.")
    st.markdown("---")
    if run_fix:
        if not code_input.strip():
            st.warning("⚠️ Please paste some code to fix.")
        else:
            with st.spinner("🛠 Fixing your code..."):
                result = fix_code(code_input, selected_language)
            st.success("✅ Code fixed successfully!")
            lang_map = {
                "Python": "python", "C": "c", "Java": "java",
                "JavaScript": "javascript", "Go": "go", "Rust": "rust", "HTML": "html"
            }
            st.code(result, language=lang_map.get(selected_language, "text"))
    else:
        st.info("👆 Click **🛠 Fix Code** to get an improved version of your code.")

# ── Tab 3: Test Cases ─────────────────────────────────────────────────────────
with tab3:
    st.markdown("## 🧪 Test Cases")
    st.markdown("Generates unit tests, edge cases, and input/output examples.")
    st.markdown("---")
    if run_tests:
        if not code_input.strip():
            st.warning("⚠️ Please paste some code to generate tests for.")
        else:
            with st.spinner("🧪 Generating test cases..."):
                result = generate_tests(code_input, selected_language)
            st.success("✅ Test cases generated!")
            st.markdown(result)
    else:
        st.info("👆 Click **🧪 Test Cases** to generate tests for your code.")

# ── Tab 4: AI Tutor ───────────────────────────────────────────────────────────
with tab4:
    st.markdown("## 👨‍🏫 CodeMentor AI")
    st.markdown("> *\"Hey! Great attempt 👏 Let's improve this together 😊\"*")
    st.markdown("---")
    if run_tutor:
        if not code_input.strip():
            st.warning("⚠️ Please paste some code for the tutor to review.")
        else:
            with st.spinner("👨‍🏫 CodeMentor is reviewing your code..."):
                result = tutor_explanation(code_input, selected_language)
            st.success("✅ Your tutoring session is ready!")
            st.markdown(result)
    else:
        st.info("👆 Click **👨‍🏫 AI Tutor** for a friendly, beginner-focused code review.")

# ── Tab 5: Study Environment ──────────────────────────────────────────────────
with tab5:
    st.markdown("## 📚 Study Environment")
    st.markdown("Deep-dive into the concept behind your code.")
    st.markdown("---")

    sub1, sub2, sub3, sub4 = st.tabs([
        "📖 Concept Explanation",
        "🧠 Practice Questions",
        "❓ Quiz",
        "💡 Learning Tips",
    ])

    with sub1:
        st.markdown("### 📖 Concept Explanation")
        st.markdown("Understand the *why* behind your code — in plain English with real-life analogies.")
        if run_study:
            if not code_input.strip():
                st.warning("⚠️ Please paste some code first.")
            else:
                with st.spinner("📖 Explaining the concept..."):
                    result = explain_concept(code_input, selected_language)
                st.success("✅ Concept explanation ready!")
                st.markdown(result)
        else:
            st.info("👆 Click **📚 Study** to activate the study environment.")

    with sub2:
        st.markdown("### 🧠 Practice Questions")
        st.markdown("Sharpen your skills with graded practice problems.")
        if run_study:
            if not code_input.strip():
                st.warning("⚠️ Please paste some code first.")
            else:
                with st.spinner("🧠 Generating practice problems..."):
                    result = generate_practice_questions(code_input, selected_language)
                st.success("✅ Practice problems ready!")
                st.markdown(result)
        else:
            st.info("👆 Click **📚 Study** to activate practice questions.")

    with sub3:
        st.markdown("### ❓ Quiz")
        st.markdown("Test your understanding with 3 auto-generated multiple-choice questions.")
        if run_study:
            if not code_input.strip():
                st.warning("⚠️ Please paste some code first.")
            else:
                with st.spinner("❓ Generating quiz questions..."):
                    result = generate_quiz(code_input, selected_language)
                st.success("✅ Quiz ready!")
                st.markdown(result)
        else:
            st.info("👆 Click **📚 Study** to generate a quiz.")

    with sub4:
        st.markdown("### 💡 Learning Tips")
        st.markdown("Best practices, common pitfalls, and improvement advice tailored to your code.")
        if run_study:
            if not code_input.strip():
                st.warning("⚠️ Please paste some code first.")
            else:
                with st.spinner("💡 Gathering learning tips..."):
                    result = learning_tips(code_input, selected_language)
                st.success("✅ Tips ready!")
                st.markdown(result)
        else:
            st.info("👆 Click **📚 Study** to get personalized learning tips.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with ❤️ for Hackathon &nbsp;|&nbsp; Powered by GPT-4o Mini &nbsp;|&nbsp; 🤖 AI Code Assistant
</div>
""", unsafe_allow_html=True)
