import streamlit as st
import requests
import time
import streamlit.components.v1 as components

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = "User"
if "room_id" not in st.session_state:
    st.session_state.room_id = None
if "room_name" not in st.session_state:
    st.session_state.room_name = None
if "show_instructions" not in st.session_state:
    st.session_state.show_instructions = True

#Authorization helper
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# Logout Helper
def logout():

    st.session_state.token = None
    st.session_state.username = "User"
    st.session_state.room_id = None
    st.session_state.room_name = None
    st.rerun()

# Login / Register UI
# Login / Register UI
def show_auth_page():

    st.subheader("📚 E-commerce & Retail (Multimodal RAG Chatbot)")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    # LOGIN
    with login_tab:

        st.subheader("Login")

        login_email = st.text_input("Email",key="login_email")
        login_password = st.text_input("Password",type="password",key="login_password")


        if st.button("Login"):
            response = requests.post(f"{API_URL}/auth/login",data={"username": login_email,"password": login_password})

            if response.status_code == 200:

                data = response.json()
                st.session_state.token = data["access_token"]
                st.success("Login successful!")
                st.rerun()

            else:
                st.error(response.json().get("detail","Login failed"))

    # REGISTER
    with register_tab:

        st.subheader("Create Account")

        register_username = st.text_input("Username",key="register_username")
        register_email = st.text_input("Email",key="register_email")
        register_password = st.text_input("Password",type="password",key="register_password")


        if st.button("Register"):
            response = requests.post(f"{API_URL}/auth/register",json={"username": register_username,"email": register_email,"password": register_password})

            if response.status_code in [200, 201]:
                st.success("Registration successful! " "You can now login.")

            else:
                st.error(response.json().get("detail","Registration failed"))

# Create Rooms 
def show_rooms_page():

    # Header
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("📚 My Chat Rooms")
        st.subheader(f"Welcome, {st.session_state.get('username', 'User')}!")

    with col2:
        st.write("")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    st.divider()


    # Information
    st.info(
        """
### Welcome!

Create separate chat rooms for different projects or datasets.

Inside every room you can:

- 📤 Upload documents
- 💬 Chat with AI
- 📚 View sources
- 🗑️ Delete files
- 🧹 Clear chat history
"""
    )

    # Create Room
    with st.expander("➕ Create New Room"):

        with st.form("create_room_form", clear_on_submit=True):
            room_name = st.text_input("Room Name",placeholder="Enter room name")
            room_description = st.text_area("Description",placeholder="Optional description")
            submitted = st.form_submit_button( "Create Room",use_container_width=True)

            if submitted:
                if not room_name.strip():
                    st.error("Room name cannot be empty.")
                else:
                    try:
                        response = requests.post(f"{API_URL}/rooms/",headers=get_headers(),json={"name": room_name.strip(),"description": room_description.strip()})

                        if response.status_code == 201:
                            st.success("Room created successfully!")
                            time.sleep(0.5)
                            st.rerun()

                        else:
                            st.error(response.json().get("detail","Failed to create room."))

                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend server.")
    st.divider()

    # Load Rooms
    st.subheader("Your Rooms")

    try:

        response = requests.get(f"{API_URL}/rooms/",headers=get_headers())

        if response.status_code == 200:
            rooms = response.json()

            if not rooms:
                st.info("No rooms found.\n\nCreate your first room above.")
                return
            
        elif response.status_code == 401:
            st.error("Session expired.")
            logout()
            return

        else:
            st.error(response.json().get("detail","Failed to load rooms."))
            return

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server.")
        return
    
    # Room Cards
    for i in range(0, len(rooms), 2):
        cols = st.columns(2)

        for col, room in zip(cols, rooms[i:i + 2]):
            with col:
                with st.container(border=True):
                    st.subheader(f"📁 {room['name']}")
                    if room.get("description"):
                        with st.expander("📄 Description"):
                            st.write(room["description"])
                    st.write("")

                    enter_col, edit_col, delete_col = st.columns([2.4, 1.8, 1.9])

                # Enter Room
                with enter_col:
                    if st.button("💬 Enter Room",key=f"enter_{room['id']}",use_container_width=True):
                        st.session_state.room_id = room["id"]
                        st.session_state.room_name = room["name"]
                        st.rerun()

                # Edit Room
                with edit_col:
                    with st.popover("✏️ Edit",use_container_width=True):
                        name = st.text_input("Room Name",value=room["name"],key=f"name_{room['id']}")
                        description = st.text_area("Description",value=room.get("description",""),key=f"description_{room['id']}")
                        if st.button("💾 Save Changes",key=f"save_{room['id']}",use_container_width=True):
                            if not name.strip():
                                st.error("Room name cannot be empty.")
                            else:
                                try:
                                    with st.spinner("Updating room..."):
                                        response = requests.patch(
                                            f"{API_URL}/rooms/{room['id']}",
                                            headers=get_headers(),
                                            json={
                                                "name": name.strip(),
                                                "description": description.strip()
                                            }
                                        )

                                        if response.status_code == 200:
                                            st.success("Room updated successfully!")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error(response.json().get("detail","Failed to update room."))

                                except requests.exceptions.ConnectionError:
                                    st.error("Cannot connect to backend.")

                # Delete Room
                with delete_col:
                    with st.popover( "Delete",use_container_width=True):
                        st.warning("Are you sure you want to delete this room? This action cannot be undone.")
                        if st.button("❌ Confirm Delete",key=f"delete_{room['id']}",use_container_width=True):
                            try:
                                with st.spinner("Deleting room..."):
                                    response = requests.delete(
                                        f"{API_URL}/rooms/{room['id']}",
                                        headers=get_headers()
                                    )

                                    if response.status_code == 200:
                                        st.success("Room deleted successfully!")
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error(response.json().get("detail","Failed to delete room."))

                            except requests.exceptions.ConnectionError:
                                st.error("Cannot connect to backend.") 
# instructions popup close helper 
def close_instructions():
    st.session_state.show_instructions = False
# Instructions Popup                                
@st.dialog("🛍️ Product Assistant Guide", width="small",on_dismiss=close_instructions)
def show_instructions_popup():

    st.markdown( """
                ### 🛍️ Add Your Product Information

Upload your product files, and the assistant will use them to answer your questions.

**What you can upload:**

📄 **Documents** (PDF, DOCX, PPTX), up to 20 MB
Catalogs, product specs, manuals, and policies.

🖼️ **Images** (PNG, JPG, JPEG), up to 10 MB
Product photos, labels, and screenshots.

🎥 **Videos** (MP4, MOV, AVI), up to 200 MB
We pull out the audio and turn it into text.

🎵 **Audio** (MP3, WAV, M4A), up to 30 MB
Speech is automatically written out as text.

📝 **Text files** (TXT, MD, CSV), up to 5 MB
Product descriptions, prices, stock lists, and similar data.

---

### 💬 Ask About Your Products

Once your files are uploaded, just type your question, like you'd ask a teammate.

📚 **Want to see where an answer came from?**
Open the Sources section to see the exact files and text the assistant used.

                """)

    st.divider()

    if st.button("Got it ✓", use_container_width=True):
        st.session_state.show_instructions = False
        st.rerun()


# Room View
def show_room_page():

    room_id = st.session_state.room_id
    room_name = st.session_state.room_name
    headers = get_headers()

    # Show instructions automatically when entering room
    if st.session_state.show_instructions:
        show_instructions_popup()

    # SIDEBAR
    with st.sidebar:

        if st.button("⬅️ Back to Rooms",use_container_width=True):
            st.session_state.room_id = None
            st.session_state.room_name = None
            st.session_state.show_instructions = True
            st.rerun()

        # Instructions button
        if not st.session_state.show_instructions:
            if st.button("📖 Instructions", use_container_width=True):
                st.session_state.show_instructions = True
                st.rerun()

        # Clear Chat History
        if st.button("🗑️ Clear Chat History",use_container_width=True):
            delete_response = requests.delete(f"{API_URL}/chat/{room_id}/history",headers=headers)
            if delete_response.status_code == 200:
                st.success("Chat history cleared!")
                st.rerun()
            else:
                st.error(delete_response.json().get("detail","Failed to clear chat history."))
        

        st.title(f"📁 {room_name}")
        st.divider()

        # Upload File
        st.subheader("📤 Upload File")

        uploaded_file = st.file_uploader(
            "Choose file",
            type=[
                "pdf","docx","csv","txt",
                "md","pptx",
                "jpg","jpeg","png",
                "mp3","wav","m4a",
                "mp4","mov","avi"
            ],
            label_visibility="collapsed"
        )


        if st.button("Upload",use_container_width=True):

            if uploaded_file:
                files = {
                    "file":(
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }
                with st.spinner("⏳ Uploading file... Please wait"):
                    response = requests.post(f"{API_URL}/upload/{room_id}",headers=headers,files=files)

                if response.status_code == 200:
                    st.success("File uploaded!")
                    st.rerun()

                else:
                    st.error(response.json().get("detail","Upload failed"))

        st.divider()

        # Uploaded Files
        st.subheader("📂 Files")
        files_response = requests.get(f"{API_URL}/upload/{room_id}",headers=headers)

        if files_response.status_code == 200:
            uploaded_files = files_response.json()

            if not uploaded_files:
                st.caption("No files uploaded yet.")

            for file in uploaded_files:
                col1, col2 = st.columns([4,1])

                with col1:
                    st.write(f"📄 {file.get('filename')}")

                    status = file.get("status","unknown")


                    if status == "ready":
                        st.success("READY")
                    elif status == "processing":
                        st.warning("PROCESSING")
                    else:
                        st.error("FAILED")

                with col2:

                    if st.button("🗑️",key=f"delete_{file['id']}"):
                        delete_response = requests.delete(f"{API_URL}/upload/{room_id}/{file['id']}",headers=headers)
                        if delete_response.status_code == 200:
                            st.rerun()

    # CHAT AREA
    st.title("💬 Chat with AI")
    history_response = requests.get(f"{API_URL}/chat/{room_id}/history",headers=headers,params={"skip":0,"limit":100})

    if history_response.status_code == 200:
        history = history_response.json()

        for message in history:
            with st.chat_message(message["role"]):
                st.write(message.get("content",""))

                if message["role"] == "assistant":
                    with st.expander("📚 Sources"):
                        sources = message.get("sources",[])

                        if sources:
                            for source in sources:
                                st.write(f"📄 {source.get('filename')} | "f"Chunk: {source.get('chunk_index')}")
                                st.caption(source.get("excerpt",""))
                        else:
                            st.write("No sources found")
    else:
        st.error("Failed to load chat history")

    # Chat Input
    query = st.chat_input("Ask a question about your documents...")

    if query:

        with st.chat_message("user"):
            st.write(query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(f"{API_URL}/chat/{room_id}",headers=headers,json={"query":query})

        if response.status_code == 200:
            st.rerun()
        else:
            st.error("Chat request failed")


# main app routing
if st.session_state.token is None:
    show_auth_page()
elif st.session_state.room_id is None:
    show_rooms_page()
else:
    show_room_page()
