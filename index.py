import streamlit as st
import requests

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
if user_input and not generate_button:
    st.session_state["triggered"] = True


def stream_api_call(query: str):
    """
    Makes a POST request to the backend API with the user query
    and yields the response line by line (streaming).
    """
    api_url = "https://api.fundrev.ai/ai/getReport"  # Your backend API URL
    try:
        with requests.post(api_url, json={"prompt": query}, stream=True) as response:
            # Check if the response status is successful
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        yield line  # Yield each line of the response as it arrives
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
        partial_markdown = ""
        for line in stream_api_call(user_input.strip()):
            # Append the new line to the accumulated Markdown
            partial_markdown += line + "\n"
            # Update the placeholder each time a new line arrives
            placeholders.markdown(partial_markdown)

    # Reset the trigger so we don't repeatedly call the API
    st.session_state["triggered"] = False

elif (st.session_state["triggered"] or generate_button) and not user_input.strip():
    st.warning("Please enter a query before generating insights.")
    st.session_state["triggered"] = False
