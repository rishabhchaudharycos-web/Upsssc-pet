import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="UPSSSC PET Note Summarizer", layout="wide")

# Sidebar for API Key
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")
st.sidebar.markdown("""
**How to get an API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account.
3. Click "Create API Key" and generate a new key.
""")

# Main Content
st.title("📚 UPSSSC PET Note Summarizer")
st.markdown("""
Upload images of your Geography, History, Polity, or Static GK notes. 
The AI will scan the image and extract the most crucial points (facts, dates, figures) 
specifically relevant to the **UPSSSC PET syllabus**.
""")

uploaded_file = st.file_uploader("Upload an image of your notes...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Notes", use_container_width=True)
    
    st.markdown("### Analysis")
    
    if st.button("Summarize Notes"):
        if not api_key:
            st.error("Please enter your Google Gemini API Key in the sidebar.")
        else:
            try:
                st.info("AI is processing the image. This may take a few seconds...")
                genai.configure(api_key=api_key)
                # Using the latest multimodal model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = """
                You are an expert tutor and summarizer specifically for the UPSSSC PET (Uttar Pradesh Subordinate Services Selection Commission Preliminary Eligibility Test) examination.
                
                I have uploaded an image of my study notes. The notes are mostly related to Geography, History, Polity, or Static GK.
                
                Please carefully read the notes in the image and perform the following tasks:
                1. Identify the subject of the notes (e.g., History, Geography, Polity, or Static GK).
                2. Extract and summarize the most critical points from these notes.
                3. Focus exclusively on facts, dates, key figures, articles, and concepts that are highly relevant to the UPSSSC PET syllabus.
                4. Present the summary in a clear, well-organized format using bullet points or numbered lists.
                5. If there is any irrelevant or fluff information in the notes, ignore it.
                6. If the notes are unclear, state what you can clearly read and interpret.
                
                Do not make up information that is not in the notes, but you can briefly provide context if it's crucial for understanding the UPSSSC PET syllabus.
                """
                
                response = model.generate_content([prompt, image])
                
                st.success("Summary Generated!")
                st.session_state['summary'] = response.text
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Render summary unconditionally if it exists
if 'summary' in st.session_state:
    st.markdown(st.session_state['summary'])

# Render chat interface if summary exists
if 'summary' in st.session_state:
    st.markdown("---")
    st.markdown("### 💬 Ask Questions About These Notes")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question about the notes..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        if not api_key:
            st.error("Please enter your Google Gemini API Key to chat.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Construct full conversation history
                chat_history = f"System Context: The user uploaded an image of notes, and you previously provided this summary:\n{st.session_state['summary']}\n\n"
                
                for msg in st.session_state.messages[:-1]: # Exclude the current prompt
                    role = "User" if msg["role"] == "user" else "Assistant"
                    chat_history += f"{role}: {msg['content']}\n\n"
                
                chat_history += f"User: {prompt}\n\nAssistant:"
                
                chat_prompt = f"{chat_history}\n\nPlease answer the user's question based on the notes summary and conversation history provided above. If the information is not in the notes, say so."
                
                response = model.generate_content(chat_prompt)
                
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"An error occurred during chat: {e}")
