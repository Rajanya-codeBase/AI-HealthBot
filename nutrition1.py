from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Configure API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Session state
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        'goals': 'Lose 10 pounds in 3 months\nImprove Cardiovascular health',
        'conditions': 'None',
        'routines': '30 minutes walk',
        'preferences': 'Vegetarian\nLow carb',
        'restrictions': 'No dairy\nNo nuts'
    }


# Function to get Gemini Response
def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel('gemini-2.5-flash')

    content = [input_prompt]
    if image_data:
        content.extend(image_data)

    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"


def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None

def create_pdf(text, filename):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = []

    # Split text line by line
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)


# App Layout
st.set_page_config(page_title="AI Health Companion", layout="wide")
st.header("🤖 AI HealthBot")
st.warning("⚠️ This app provides AI-generated guidance and is not a substitute for professional medical advice.")

# Sidebar
with st.sidebar:
    st.subheader("Your Health Profile")

    health_goals = st.text_area("Health Goals", value=st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Medical Conditions", value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Fitness Routines", value=st.session_state.health_profile['routines'])
    food_preferences = st.text_area("Food Preferences", value=st.session_state.health_profile['preferences'])
    restrictions = st.text_area("Dietary Restrictions", value=st.session_state.health_profile['restrictions'])

    if st.button("Update Profile"):
        st.session_state.health_profile = {
            'goals': health_goals,
            'conditions': medical_conditions,
            'routines': fitness_routines,
            'preferences': food_preferences,
            'restrictions': restrictions
        }
        st.success("Profile updated!")


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍽 Meal Planning",
    "📸 Food Analysis",
    "🧠 Health Insights",
    "💪 Workout Planning",
    "📊 Progress Tracking"
])

# =========================
# TAB 1 — MEAL PLANNING
# =========================
with tab1:
    st.subheader("Personalized Meal Planning")

    user_input = st.text_area("Additional Requirements (optional)")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Your Health Profile")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalized Meal Plan"):

        if not any(st.session_state.health_profile.values()):
            st.warning("Please complete your health profile in the sidebar first")
        else:
            with st.spinner("Creating your personalized meal plan..."):

                prompt = f"""
                Create a personalized meal plan based on the following health profile:

                Health Goals: {st.session_state.health_profile['goals']}
                Medical Conditions: {st.session_state.health_profile['conditions']}
                Fitness Routines: {st.session_state.health_profile['routines']}
                Food Preferences: {st.session_state.health_profile['preferences']}
                Dietary Restrictions: {st.session_state.health_profile['restrictions']}

                Additional requirements: {user_input if user_input else "None"}

                Provide:
                1. A 7-Day meal plan with breakfast, lunch, dinner and snacks
                2. Nutritional breakdown for each day (calories, macros)
                3. Contextual explanations for why each meal was chosen
                4. Shopping list organized by category
                5. Preparation tips and time saving suggestions

                Format the output clearly with headings and bullet points.
                """

                response = get_gemini_response(prompt)

                st.subheader("Your Personalized Meal Plan")
                st.markdown(response)

                # Create PDF file
                pdf_file = "meal_plan.pdf"
                create_pdf(response, pdf_file)

                # Download button
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Download Meal Plan as PDF",
                        data=f,
                        file_name="meal_plan.pdf",
                        mime="application/pdf"
                    )


# =========================
# TAB 2 — FOOD ANALYSIS
# =========================
with tab2:
    st.subheader("Food Analysis")

    uploaded_file = st.file_uploader(
        "Upload an image of your food",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)

        if st.button("Analyze Food"):
            with st.spinner("Analyzing your food..."):

                image_data = input_image_setup(uploaded_file)

                prompt = f"""
                You are an expert nutritionist. Analyze this food image.

                Provide detailed information about:
                - Estimated calories
                - Macronutrient breakdown
                - Potential health benefits
                - Any concerns based on common dietary restrictions
                - Suggested portion sizes

                If the food contains multiple items, analyze each separately.
                """

                response = get_gemini_response(prompt, image_data)

                st.subheader("Food Analysis Results")
                st.markdown(response)


# =========================
# TAB 3 — HEALTH INSIGHTS
# =========================
with tab3:
    st.subheader("Health Insights")

    health_query = st.text_input(
        "Ask any health/nutrition-related question",
        placeholder="e.g., How can I improve my gut health?"
    )

    if st.button("Get Expert Insights"):

        if not health_query:
            st.warning("Please enter a health question")
        else:
            with st.spinner("Researching your question..."):

                prompt = f"""
                You are a certified nutritionist and health expert.

                Provide detailed, science-backed insights about:
                {health_query}

                Consider the user's health profile:
                {st.session_state.health_profile}

                Include:
                1. Clear explanation of the science
                2. Practical recommendations
                3. Any relevant precautions
                4. References to studies (when applicable)
                5. Suggested foods/supplements if appropriate

                Use simple language but maintain accuracy.
                """

                response = get_gemini_response(prompt)

                st.subheader("Expert Health Insights")
                st.markdown(response)
                
# =========================
# TAB 4 — WORKOUT PLANNING
# =========================
with tab4:
    st.subheader("AI Weekly Workout Generator")

    fitness_level = st.selectbox(
        "Select Fitness Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    workout_location = st.selectbox(
        "Workout Location",
        ["Home", "Gym"]
    )

    equipment = st.selectbox(
        "Available Equipment",
        ["Bodyweight Only", "Dumbbells", "Full Gym Equipment"]
    )

    workout_goal = st.selectbox(
        "Primary Goal",
        ["Fat Loss", "Muscle Gain", "General Fitness"]
    )

    if st.button("Generate Weekly Workout Plan"):

        with st.spinner("Designing your AI workout program..."):

            prompt = f"""
            Create a structured 7-day workout plan.

            Fitness Level: {fitness_level}
            Location: {workout_location}
            Equipment: {equipment}
            Goal: {workout_goal}

            Provide:

            1. Weekly split (e.g., Push/Pull/Legs or Full Body)
            2. Daily exercise list
            3. Sets and reps
            4. Rest intervals
            5. Estimated workout duration
            6. Safety notes for the given level

            Format clearly using headings and bullet points.
            
            Return workout in this structure:
            ## Day 1
            | Exercise | Sets | Reps | Rest |
            """

            response = get_gemini_response(prompt)

            st.subheader("Your AI Weekly Workout Plan")
            st.markdown(response)

            pdf_file = "workout_plan.pdf"
            create_pdf(response, pdf_file)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="Download Workout Plan as PDF",
                    data=f,
                    file_name="workout_plan.pdf",
                    mime="application/pdf"
                )
            
            
# =========================
# TAB 5 — PROGRESS TRACKING
# =========================
with tab5:
    st.subheader("📊 Health Progress Tracker")

    # Input fields
    weight = st.number_input("Current Weight (kg)", min_value=0.0)
    calories = st.number_input("Calories Consumed Today", min_value=0)
    workout_done = st.selectbox("Workout Completed Today?", ["Yes", "No"])

    if st.button("Save Today's Data"):

        today = datetime.now().strftime("%Y-%m-%d")

        new_data = {
            "Date": today,
            "Weight": weight,
            "Calories": calories,
            "Workout": 1 if workout_done == "Yes" else 0
        }

        try:
            df = pd.read_csv("progress_data.csv")
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        except:
            df = pd.DataFrame([new_data])

        df.to_csv("progress_data.csv", index=False)
        st.success("Data saved successfully!")

    # Show progress
    try:
        df = pd.read_csv("progress_data.csv")

        st.subheader("Weight Progress")
        st.line_chart(df.set_index("Date")["Weight"])

        st.subheader("Calories Intake Trend")
        st.line_chart(df.set_index("Date")["Calories"])

        workout_percentage = (df["Workout"].sum() / len(df)) * 100
        st.subheader("Workout Consistency")
        st.write(f"Consistency: {workout_percentage:.2f}%")

    except:
        st.info("No data available yet. Start tracking today!")