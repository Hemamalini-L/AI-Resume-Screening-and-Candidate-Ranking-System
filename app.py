import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Function to extract text from a PDF
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""  # Safeguard if no text is extracted
    return text

# Function to rank resumes based on job description
def rank_resumes(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    # Calculate cosine similarity
    job_description_vector = vectors[0].reshape(1, -1)
    resume_vectors = vectors[1:]
    cosine_similarities = cosine_similarity(job_description_vector, resume_vectors)

    return cosine_similarities.flatten()  # Convert to a list of scores

# Streamlit app
st.title("AI Resume Screening & Candidate Ranking System")

# Job description input
st.header("Job Description")
job_description = st.text_area("Enter the job description here:")

# File uploader
st.header("Upload Resumes")
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files and job_description:
    st.header("Ranking Resumes")

    resumes = []  # Initialize an empty list
    for file in uploaded_files:
        try:
            text = extract_text_from_pdf(file)
            if text:
                resumes.append(text)
            else:
                st.warning(f"Warning: The file {file.name} has no text content or couldn't be extracted.")
        except Exception as e:
            st.error(f"Error processing file {file.name}: {str(e)}")

    if resumes:  # Ensure there are resumes to rank
        # Rank resumes
        scores = rank_resumes(job_description, resumes)

        # Display results
        results = pd.DataFrame({"Resume": [file.name for file in uploaded_files], "Score": scores})
        results = results.sort_values(by="Score", ascending=False)
        st.write(results)
    else:
        st.warning("No valid resumes to rank.")

