
import os
import json
import base64
from io import BytesIO

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "GEMINI_API_KEY is missing. "
        "Create a .env file and add GEMINI_API_KEY=your_key"
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

# Use a currently available Gemini multimodal model.
MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI INVENTOR",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .hero {
        padding: 30px;
        border-radius: 20px;
        background:
            linear-gradient(
                135deg,
                rgba(37, 99, 235, 0.18),
                rgba(147, 51, 234, 0.18)
            );
        border: 1px solid rgba(255,255,255,0.10);
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 19px;
        opacity: 0.8;
    }

    .feature-card {
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.04);
        margin-bottom: 12px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .result-box {
        padding: 20px;
        border-radius: 16px;
        background: rgba(37, 99, 235, 0.08);
        border: 1px solid rgba(37, 99, 235, 0.25);
        margin-bottom: 15px;
    }

    .metric-box {
        padding: 15px;
        border-radius: 14px;
        background: rgba(255,255,255,0.05);
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            💡 AI INVENTOR
        </div>

        <div class="hero-subtitle">
            Turn ordinary objects into extraordinary inventions.
        </div>

        <br>

        <div>
            📸 Upload an image → 🤖 AI understands it →
            💡 Generate a new invention
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Inventor Settings")

    invention_style = st.selectbox(
        "Innovation Style",
        [
            "Practical and useful",
            "Crazy and futuristic",
            "Eco-friendly",
            "Low-cost DIY",
            "Smart technology",
            "Emergency / safety",
            "Home automation",
            "Student innovation",
        ],
    )

    budget = st.selectbox(
        "Budget",
        [
            "Under ₹100",
            "₹100 – ₹500",
            "₹500 – ₹1,000",
            "₹1,000 – ₹5,000",
            "₹5,000+",
        ],
    )

    skill_level = st.selectbox(
        "Build Difficulty",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
    )

    st.divider()

    st.markdown("### 🧠 What AI INVENTOR does")

    st.markdown(
        """
        **1. Detects objects**

        Finds useful objects/materials in your image.

        **2. Connects ideas**

        Looks for unusual combinations.

        **3. Creates an invention**

        Generates a realistic product concept.

        **4. Explains construction**

        Gives materials and build steps.

        **5. Estimates cost**

        Provides an approximate budget.

        **6. Checks safety**

        Highlights potential risks.
        """
    )

    st.divider()

    st.caption("AI INVENTOR • Powered by Gemini")


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">📸 Show Me What You Have</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload a photo containing objects, materials, tools, or everyday items.",
    type=["jpg", "jpeg", "png", "webp"],
)


# ============================================================
# EXAMPLE IDEAS
# ============================================================

if uploaded_file is None:

    st.info(
        "💡 Tip: Take a photo of several ordinary objects together. "
        "AI INVENTOR will try to combine them into a useful invention."
    )

    cols = st.columns(3)

    with cols[0]:
        st.markdown(
            """
            <div class="feature-card">
            🏠 <b>Home Objects</b><br>
            Bottles, boxes, wires, containers, etc.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[1]:
        st.markdown(
            """
            <div class="feature-card">
            🔧 <b>Tools & Materials</b><br>
            Old electronics, tools, plastic, metal, etc.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[2]:
        st.markdown(
            """
            <div class="feature-card">
            ♻️ <b>Waste Objects</b><br>
            Turn unused objects into something useful.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DISPLAY IMAGE
# ============================================================

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1])

    with col1:

        st.subheader("📷 Your Image")

        st.image(
            image,
            use_container_width=True,
        )

    with col2:

        st.subheader("🎯 Invention Parameters")

        st.write(
            f"**Style:** {invention_style}"
        )

        st.write(
            f"**Budget:** {budget}"
        )

        st.write(
            f"**Difficulty:** {skill_level}"
        )

        st.write(
            "The AI will analyze the objects and create an invention."
        )

        generate = st.button(
            "🚀 INVENT SOMETHING",
            type="primary",
            use_container_width=True,
        )


    # ========================================================
    # GEMINI ANALYSIS
    # ========================================================

    if generate:

        with st.spinner(
            "🔍 Analyzing your objects and designing an invention..."
        ):

            try:

                # Convert image to supported format
                image_bytes = BytesIO()
                image.save(image_bytes, format="JPEG")
                image_data = image_bytes.getvalue()

                # ------------------------------------------------
                # AI PROMPT
                # ------------------------------------------------

                prompt = f"""
You are AI INVENTOR, an expert invention designer.

Your job is to look at the uploaded image and identify objects,
materials, tools, components, or resources that could be combined
into a useful invention.

INVENTION PREFERENCES:

Innovation style:
{invention_style}

Budget:
{budget}

Build difficulty:
{skill_level}

IMPORTANT:

Do not simply describe the objects.

CREATE A NEW INVENTION using one or more objects visible in the image.

The invention should be:

- Creative
- Useful
- Technically believable
- Buildable
- Appropriate for the selected budget
- Appropriate for the selected difficulty
- Safe to build
- Different from an obvious/common use of the objects

Think like an inventor, engineer, product designer, and startup
founder simultaneously.

Return the result as VALID JSON ONLY.

Use exactly this structure:

{{
    "objects_detected": [
        "object 1",
        "object 2"
    ],

    "invention_name": "Creative invention name",

    "tagline": "One short memorable tagline",

    "problem": "What real-world problem does this invention solve?",

    "idea": "Explain the invention clearly.",

    "how_it_works": [
        "Step 1 of operation",
        "Step 2 of operation",
        "Step 3 of operation"
    ],

    "materials": [
        {{
            "item": "Material name",
            "purpose": "Why it is needed",
            "estimated_cost": "₹ amount"
        }}
    ],

    "build_steps": [
        "Step 1",
        "Step 2",
        "Step 3",
        "Step 4",
        "Step 5"
    ],

    "estimated_cost": "₹ amount",

    "difficulty": "Beginner / Intermediate / Advanced",

    "build_time": "Approximate time",

    "safety": [
        "Safety consideration 1",
        "Safety consideration 2"
    ],

    "eco_impact": "Explain environmental benefit.",

    "alternatives": [
        "Alternative material or approach 1",
        "Alternative material or approach 2"
    ],

    "real_world_applications": [
        "Application 1",
        "Application 2",
        "Application 3"
    ],

    "future_upgrades": [
        "Future upgrade 1",
        "Future upgrade 2",
        "Future upgrade 3"
    ],

    "startup_potential": "Explain whether this could become a product or startup."
}}

Make the invention genuinely creative.

Avoid unsafe instructions involving explosives, weapons,
dangerous chemicals, electrical mains voltage, or other hazardous
activities.
"""


                # ------------------------------------------------
                # GEMINI REQUEST
                # ------------------------------------------------

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        types.Part.from_bytes(
                            data=image_data,
                            mime_type="image/jpeg",
                        ),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.9,
                    ),
                )


                # ------------------------------------------------
                # PARSE RESPONSE
                # ------------------------------------------------

                result_text = response.text.strip()

                # Remove markdown JSON fences if Gemini adds them
                if result_text.startswith("```"):
                    result_text = result_text.replace(
                        "```json", ""
                    ).replace(
                        "```", ""
                    ).strip()

                result = json.loads(result_text)


                # Save result in session state
                st.session_state["invention"] = result


            except json.JSONDecodeError:

                st.error(
                    "The AI returned an unexpected format. "
                    "Please try again."
                )

                st.code(
                    result_text if "result_text" in locals() else "",
                    language="text",
                )


            except Exception as e:

                st.error(
                    "Something went wrong while generating the invention."
                )

                st.exception(e)


# ============================================================
# DISPLAY INVENTION
# ============================================================

if "invention" in st.session_state:

    result = st.session_state["invention"]

    st.divider()

    st.markdown(
        '<div class="section-title">💡 Your Invention</div>',
        unsafe_allow_html=True,
    )


    # ========================================================
    # MAIN IDEA
    # ========================================================

    st.markdown(
        f"""
        <div class="result-box">

        <h1>🚀 {result.get("invention_name", "Untitled Invention")}</h1>

        <h3>
        "{result.get("tagline", "")}"
        </h3>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # METRICS
    # ========================================================

    metric1, metric2, metric3 = st.columns(3)

    with metric1:

        st.metric(
            "💰 Estimated Cost",
            result.get(
                "estimated_cost",
                "Not available",
            ),
        )

    with metric2:

        st.metric(
            "🧠 Difficulty",
            result.get(
                "difficulty",
                "Not available",
            ),
        )

    with metric3:

        st.metric(
            "⏱️ Build Time",
            result.get(
                "build_time",
                "Not available",
            ),
        )


    # ========================================================
    # OBJECTS
    # ========================================================

    st.markdown(
        '<div class="section-title">🔍 Objects Detected</div>',
        unsafe_allow_html=True,
    )

    objects = result.get("objects_detected", [])

    if objects:

        cols = st.columns(min(len(objects), 4))

        for i, obj in enumerate(objects):

            with cols[i % len(cols)]:

                st.info(f"🔹 {obj}")


    # ========================================================
    # PROBLEM
    # ========================================================

    st.markdown(
        '<div class="section-title">🎯 Problem</div>',
        unsafe_allow_html=True,
    )

    st.write(
        result.get(
            "problem",
            "No problem description available.",
        )
    )


    # ========================================================
    # IDEA
    # ========================================================

    st.markdown(
        '<div class="section-title">💡 The Big Idea</div>',
        unsafe_allow_html=True,
    )

    st.write(
        result.get(
            "idea",
            "No invention description available.",
        )
    )


    # ========================================================
    # HOW IT WORKS
    # ========================================================

    st.markdown(
        '<div class="section-title">⚙️ How It Works</div>',
        unsafe_allow_html=True,
    )

    how_it_works = result.get(
        "how_it_works",
        [],
    )

    for i, step in enumerate(how_it_works, 1):

        st.markdown(
            f"""
            **{i}.** {step}
            """
        )


    # ========================================================
    # MATERIALS
    # ========================================================

    st.markdown(
        '<div class="section-title">🧰 Materials Required</div>',
        unsafe_allow_html=True,
    )

    materials = result.get(
        "materials",
        [],
    )

    for material in materials:

        if isinstance(material, dict):

            item = material.get(
                "item",
                "Unknown",
            )

            purpose = material.get(
                "purpose",
                "",
            )

            cost = material.get(
                "estimated_cost",
                "",
            )

            st.markdown(
                f"""
                **🔹 {item}**

                Purpose: {purpose}

                Estimated cost: {cost}
                """
            )

            st.divider()

        else:

            st.write(f"🔹 {material}")


    # ========================================================
    # BUILD STEPS
    # ========================================================

    st.markdown(
        '<div class="section-title">🔨 How To Build It</div>',
        unsafe_allow_html=True,
    )

    build_steps = result.get(
        "build_steps",
        [],
    )

    for i, step in enumerate(build_steps, 1):

        st.markdown(
            f"""
            ### Step {i}

            {step}
            """
        )


    # ========================================================
    # SAFETY
    # ========================================================

    st.markdown(
        '<div class="section-title">⚠️ Safety</div>',
        unsafe_allow_html=True,
    )

    safety = result.get(
        "safety",
        [],
    )

    for item in safety:

        st.warning(
            f"⚠️ {item}"
        )


    # ========================================================
    # ECO IMPACT
    # ========================================================

    st.markdown(
        '<div class="section-title">♻️ Environmental Impact</div>',
        unsafe_allow_html=True,
    )

    st.write(
        result.get(
            "eco_impact",
            "No information available.",
        )
    )


    # ========================================================
    # ALTERNATIVES
    # ========================================================

    st.markdown(
        '<div class="section-title">🔄 Alternative Materials / Ideas</div>',
        unsafe_allow_html=True,
    )

    alternatives = result.get(
        "alternatives",
        [],
    )

    for item in alternatives:

        st.write(
            f"🔹 {item}"
        )


    # ========================================================
    # REAL WORLD APPLICATIONS
    # ========================================================

    st.markdown(
        '<div class="section-title">🌍 Real-World Applications</div>',
        unsafe_allow_html=True,
    )

    applications = result.get(
        "real_world_applications",
        [],
    )

    for item in applications:

        st.success(
            f"🚀 {item}"
        )


    # ========================================================
    # FUTURE UPGRADES
    # ========================================================

    st.markdown(
        '<div class="section-title">🚀 Future Upgrades</div>',
        unsafe_allow_html=True,
    )

    upgrades = result.get(
        "future_upgrades",
        [],
    )

    for item in upgrades:

        st.write(
            f"🔮 {item}"
        )


    # ========================================================
    # STARTUP POTENTIAL
    # ========================================================

    st.markdown(
        '<div class="section-title">💰 Startup Potential</div>',
        unsafe_allow_html=True,
    )

    st.write(
        result.get(
            "startup_potential",
            "No startup analysis available.",
        )
    )


    # ========================================================
    # DOWNLOAD RESULT
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">📥 Save Your Invention</div>',
        unsafe_allow_html=True,
    )

    downloadable_text = f"""
AI INVENTOR
===========

INVENTION
---------
{result.get("invention_name", "")}

TAGLINE
-------
{result.get("tagline", "")}

OBJECTS DETECTED
----------------
{chr(10).join("- " + x for x in result.get("objects_detected", []))}

PROBLEM
-------
{result.get("problem", "")}

IDEA
----
{result.get("idea", "")}

HOW IT WORKS
------------
{chr(10).join(str(i + 1) + ". " + x for i, x in enumerate(result.get("how_it_works", [])))}

MATERIALS
---------
{chr(10).join("- " + str(x) for x in result.get("materials", []))}

BUILD STEPS
-----------
{chr(10).join(str(i + 1) + ". " + x for i, x in enumerate(result.get("build_steps", [])))}

ESTIMATED COST
--------------
{result.get("estimated_cost", "")}

DIFFICULTY
----------
{result.get("difficulty", "")}

BUILD TIME
----------
{result.get("build_time", "")}

SAFETY
------
{chr(10).join("- " + x for x in result.get("safety", []))}

ECO IMPACT
----------
{result.get("eco_impact", "")}

ALTERNATIVES
------------
{chr(10).join("- " + x for x in result.get("alternatives", []))}

REAL WORLD APPLICATIONS
-----------------------
{chr(10).join("- " + x for x in result.get("real_world_applications", []))}

FUTURE UPGRADES
---------------
{chr(10).join("- " + x for x in result.get("future_upgrades", []))}

STARTUP POTENTIAL
-----------------
{result.get("startup_potential", "")}
"""

    st.download_button(
        label="📄 Download Invention Report",
        data=downloadable_text,
        file_name="ai_invention_report.txt",
        mime="text/plain",
        use_container_width=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; opacity:0.65; padding:20px;">
        💡 AI INVENTOR<br>
        <small>
        Imagine it. Build it. Invent it.
        </small>
    </div>
    """,
    unsafe_allow_html=True,
)
