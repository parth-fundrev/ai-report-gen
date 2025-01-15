import streamlit as st
import requests  # For making API calls

# Streamlit title
st.title("AI Insights")

# Input field for user query
user_input = st.text_input("Enter your query:", placeholder="Type something...")

# Add a "Generate" button
generate_button = st.button("Generate")

# Session state setup for Enter key detection
if "triggered" not in st.session_state:
    st.session_state["triggered"] = False

# When Enter key is pressed, set the trigger
# (Streamlit re-runs on every action, so if there's input
#  but the button wasn't clicked, we consider it an "Enter" press.)
if user_input and not generate_button:
    st.session_state["triggered"] = True


def stream_api_call(query: str):
    """
    Makes a POST request to the backend API with the user query
    and yields the response line by line (streaming).
    """
    api_url = "https://api.fundrev.ai/ai/getReport"  # Your backend API URL
    try:
        response = requests.post(api_url, json={"prompt": query}, stream=True)
        if response.status_code == 200:
            partial_markdown = ""
            # Iterate over streamed lines
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # Append the new line to partial_markdown
                    partial_markdown += line + "\n"
                    # Yield the entire assembled Markdown so far
                    yield partial_markdown
        else:
            st.error(f"API call failed with status code: {response.status_code}")
            st.write("Response Text:", response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")


# Handle input and API call only if user pressed Enter or clicked Generate
if (st.session_state["triggered"] or generate_button) and user_input.strip():
    # Create a placeholder for partial streaming updates
    placeholders = st.empty()

    with st.spinner("Generating insights..."):
        # Stream the response line by line
        for chunk in stream_api_call(user_input.strip()):
            # Update the placeholder each time a new line arrives
            placeholders.markdown(chunk)

    # Reset the trigger so we don't repeatedly call the API
    st.session_state["triggered"] = False

elif (st.session_state["triggered"] or generate_button) and not user_input.strip():
    st.warning("Please enter a query before generating insights.")
    st.session_state["triggered"] = False
