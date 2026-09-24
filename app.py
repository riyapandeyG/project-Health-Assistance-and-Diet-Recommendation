import streamlit as st
import os
from dotenv import load_dotenv

from diet import (
    bmi_calculator,
    bmr_calculator,
    tdee_calculator,
    calorie_target
)

from rag import load_rag
from openai import OpenAI
from dotenv import load_dotenv


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

HF_token = os.getenv("HF_TOKEN")

if not HF_token:
    try:
        HF_token = st.secrets["HF_TOKEN"]
    except Exception:
        HF_token = None

if not HF_token:
    st.error("HF_TOKEN is not configured.")
    st.stop()

if not HF_token:
    st.error("HF_TOKEN is not configured.")
    st.stop()


# =====================================================
# HUGGING FACE LLM
# =====================================================

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_token
)


# =====================================================
# STREAMLIT PAGE
# =====================================================

st.set_page_config(layout="wide")

st.title("AI HEALTH ASSISTANT 🏋️")

st.write(
    "Personal Health Assistance and Diet Recommendation Agent"
)

st.header("Health Information")


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("🤷‍♂️ Your Information")

gender = st.sidebar.selectbox(
    "Gender",
    ["Male", "Female"]
)

age = st.sidebar.number_input(
    "Age",
    min_value=1,
    max_value=100,
    value=20
)

weight = st.sidebar.number_input(
    "Weight (Kg)",
    min_value=1,
    max_value=120,
    value=60
)

height = st.sidebar.number_input(
    "Height (cm)",
    min_value=100,
    max_value=200,
    value=160
)

activity = st.sidebar.selectbox(
    "Activity",
    [
        "Sedentary",
        "Lightly Active",
        "Moderately Active",
        "Very Active",
        "Extra Active"
    ]
)

aim = st.sidebar.selectbox(
    "AIM",
    [
        "weight maintain",
        "weight loss",
        "weight gain"
    ]
)

diet_type = st.sidebar.selectbox(
    "Diet Type",
    [
        "Vegetarian",
        "Non Vegetarian"
    ]
)

allergies = st.sidebar.text_input(
    "Food Allergy",
    placeholder="e.g. Peanut, Milk, None"
)


# =====================================================
# CALCULATIONS
# =====================================================

bmi = bmi_calculator(weight, height)

bmr = bmr_calculator(
    gender,
    age,
    weight,
    height
)

tdee = tdee_calculator(
    bmr,
    activity
)

calories = calorie_target(
    tdee,
    aim
)


# =====================================================
# METRICS
# =====================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "BMI",
    bmi
)

col2.metric(
    "BMR",
    f"{bmr} Kcal"
)

col3.metric(
    "TDEE",
    f"{tdee} Kcal"
)

col4.metric(
    "Calorie Target",
    f"{calories} Kcal"
)


# =====================================================
# TABS
# =====================================================

tab1, tab2 = st.tabs(
    [
        "Diet Recommendation",
        "Health Assistance"
    ]
)


# =====================================================
# TAB 1 - DIET RECOMMENDATION
# =====================================================

with tab1:

    if st.button("Recommend Diet"):

        with st.spinner("Creating Diet..."):

            try:

                db = load_rag()

                search_query = f"""
                Diet Type: {diet_type}

                Healthy food

                Protein

                Food Allergy: {allergies}
                """

                docs = db.similarity_search(
                    search_query,
                    3
                )

                context = "\n\n".join(
                    [
                        doc.page_content
                        for doc in docs
                    ]
                )

                prompt = f"""
You are a helpful AI nutrition assistant.

Use the following nutrition knowledge
to create a simple one-day diet plan.

NUTRITION KNOWLEDGE:

{context}


USER INFORMATION:

Age: {age}

Gender: {gender}

Height: {height} cm

Weight: {weight} kg

Activity Level: {activity}

Aim: {aim}

Diet Type: {diet_type}

Food Allergy: {allergies}

Estimated BMI: {bmi}

Estimated BMR: {bmr} kcal/day

Estimated TDEE: {tdee} kcal/day

Estimated Daily Calorie Target:
{calories} kcal/day


Create the following:

1. Breakfast
2. Morning Snack
3. Lunch
4. Evening Snack
5. Dinner


For every meal provide:

- Food
- Portion
- Approximate calories
- Approximate protein


IMPORTANT RULES:

- Respect the user's diet type.
- Do not recommend foods containing the stated allergy.
- Use the provided nutrition knowledge when possible.
- Keep the plan simple and practical.
- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not claim to cure diseases.
- This is general wellness information, not medical advice.
"""

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                answer = response.choices[0].message.content

                st.markdown(answer)

            except Exception as e:

                st.error(
                    f"Diet recommendation error: {e}"
                )


# =====================================================
# TAB 2 - HEALTH ASSISTANCE
# =====================================================

with tab2:
    st.subheader("🩺 Health Assistance")

    question = st.text_area(
        "Ask your health question:",
        placeholder="Example: What are good sources of vegetarian protein?",
        height=120
    )

    if st.button("🤖 Ask AI", key="health_ai_button"):
        if not question.strip():
            st.warning("Please enter your question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    db = load_rag()

                    docs = db.similarity_search(question, 3)

                    context = "\n\n".join(
                        [doc.page_content for doc in docs]
                    )

                    prompt = f"""
You are a helpful health and nutrition assistant.

Answer the user's question using the provided nutrition
knowledge whenever possible.

Nutrition knowledge:
{context}

User question:
{question}

Give a simple, clear and useful answer.
Do not provide a medical diagnosis.
"""

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )

                    answer = response.choices[0].message.content

                    st.success("AI Response")
                    st.markdown(answer)

                except Exception as e:
                    st.error(f"Health assistance error: {e}")