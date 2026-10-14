from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import streamlit as st
import os
import sqlite3

import re
from google import genai

# Initialize Gemini client
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Convert English questions into SQL queries
def get_gemini_response(question, prompt):
    if client is None:
        raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    response = client.models.generate_content(
        model="gemini-pro",
        contents=f"{prompt[0]}\n\nQuestion: {question}\nSQL Query:"
    )

    if not response.text:
        raise ValueError("Gemini did not return an SQL query.")

    sql = response.text.strip()
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.IGNORECASE).strip()

    return sql.rstrip(";") + ";"


# Execute SQL queries against SQLite
def read_sql_query(sql, db):
    # Allow read-only queries to prevent database modifications
    if not re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    conn = sqlite3.connect(f"file:{os.path.abspath(db)}?mode=ro", uri=True)

    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()


# Prompt for SQL generation
prompt = [
    """
    You are an expert in converting English questions into SQLite queries.
    The database contains a table named STUDENT with these columns:
    NAME, CLASS, SECTION, MARKS.

    Examples:
    Question: How many records are in the STUDENT table?
    SQL Query: SELECT COUNT(*) FROM STUDENT;

    Question: Show all students studying in 10th class.
    SQL Query: SELECT * FROM STUDENT WHERE CLASS = '10th';

    Return only one valid SQLite query without Markdown code fences.
    Generate read-only SELECT queries only.
    Do not invent table or column names.
    """
]

# Streamlit interface
st.set_page_config(page_title="Text to SQL Query Generator", page_icon="🗃️")
st.title("Text-to-SQL Query Generator")
st.header("Ask questions about your student database")

question = st.text_input(
    "Enter your question:",
    placeholder="e.g., Show all students scoring above 80 marks"
)

if st.button("Ask the question"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Generating SQL and fetching results..."):
                sql_query = get_gemini_response(question, prompt)
                data = read_sql_query(sql_query, "students.db")

            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            st.subheader("Query Results")
            if data:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("The query executed successfully but returned no records.")

        except Exception as e:
            st.error(f"Error: {e}")

