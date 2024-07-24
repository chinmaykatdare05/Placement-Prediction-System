import streamlit as st
import pandas as pd
import pickle
import google.generativeai as genai
import asyncio

with open("./api.txt", "r") as file:
    api_key = file.read()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")


async def display(placed):
    return st.balloons() if placed == "Yes" else st.snow()


async def feedback(prompt):
    response = model.generate_content(prompt, stream=True)
    response.resolve()
    messages.chat_message("assistant").write(response.text)


st.set_page_config(
    page_title="Placement Prediction System",
    page_icon="💼",
)

# Main Page
st.title("Placement Prediction System 🎓")
st.divider()
st.write(
    "Ready to peek into your professional crystal ball? Gone are the days of blind job hunting, simply toss in your details and voilà!"
)
st.write(
    "We'll predict your future placement and even sprinkle in a salary forecast. Who needs a fortune cookie when you've got algorithms on your side? 🍪"
)
st.write(
    "Don't leave your future to chance — Join the ranks of countless satisfied users of our Placement Prediction System."
)
st.divider()


# Sidebar
st.sidebar.header("📋 User Input Features")
st.sidebar.write("Please complete the form for a successful prediction")

ssc_marks = st.sidebar.slider("SSC Marks", 50, 100, 75, 1)
hsc_marks = st.sidebar.slider("HSC Marks", 50, 100, 75, 1)

data = {
    "CGPA": st.sidebar.slider("CGPA", 6.5, 10.0, 7.5, 0.1),
    "Internships": st.sidebar.number_input(
        "Internships", min_value=0, max_value=2, value=0
    ),
    "Projects": st.sidebar.number_input("Projects", min_value=0, max_value=3, value=1),
    "Workshops/Certifications": st.sidebar.number_input(
        "Certifications", min_value=0, max_value=3, value=0
    ),
    "AptitudeTestScore": st.sidebar.slider("Technical Skills", 50, 100, 75, 5),
    "SoftSkillsRating": st.sidebar.slider("Soft Skills", 3.0, 5.0, 4.0, 0.1),
    "ExtracurricularActivities": (
        1
        if st.sidebar.radio("Extracurricular Activities", ["Yes", "No"]) == "Yes"
        else 0
    ),
    "PlacementTraining": (
        1 if st.sidebar.radio("Placement Training", ["Yes", "No"]) == "Yes" else 0
    ),
    "SSC_HSC_Avg": (ssc_marks + hsc_marks) / 2,
}

features = pd.DataFrame(data, index=[0])

# Load models
placement_model = pickle.load(open("Placement.pkl", "rb"))
salary_model = pickle.load(open("Salary.pkl", "rb"))

# Predict button
if st.sidebar.button("Predict", use_container_width=True):
    placed = int(placement_model.predict(features))
    if placed == 1:
        features["PlacementStatus"] = 1
        placed = "Yes"
        prompt = f"I am Engineering Student having CGPA {data['CGPA']}, {data['Internships']} internships, {data['Projects']} projects, {data['Workshops/Certifications']} certificates, {data['AptitudeTestScore']} technical_skills (out of 100), {data['SoftSkillsRating']} soft_skills (out of 5). What should I improve on so that I can get a good placement? Please do not mention my details in your answer."
    else:
        placed = "No"
        prompt = f"I am Engineering Student having CGPA {data['CGPA']}, {data['Internships']} internships, {data['Projects']} projects, {data['Workshops/Certifications']} certificates, {data['AptitudeTestScore']} technical_skills (out of 100), {data['SoftSkillsRating']} soft_skills (out of 5). There are very few chances of my placement. What should I improve on so that I can get a good placement? Please do not mention my details in your answer."

    st.subheader("Prediction:")
    col1, col2 = st.columns(2)
    col1.metric("Placement", placed)
    try:
        col2.metric("Salary", "₹ " + str(int(salary_model.predict(features))), "±4%")
    except:
        pass

    st.divider()
    st.subheader("Areas of Improvement:")

    messages = st.container(height=700)
    asyncio.run(display(placed))
    asyncio.run(feedback(prompt))
