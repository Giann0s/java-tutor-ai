import streamlit as st

from api.chat_api import get_user_conversations, delete_conversation, send_chat_message

if "access_token" not in st.session_state or not st.session_state['access_token']:
    st.warning("Παρακαλώ συνδεθείτε από την αρχική σελίδα για να έχετε πρόσβαση στο Chat.")
    st.stop()

token = st.session_state['access_token']

if 'current_messages' not in st.session_state:
    st.session_state['current_messages'] = []
if 'current_conversation_id' not in st.session_state:
    st.session_state['current_conversation_id'] = 0


# Τρέχει στο παρασκήνιο όταν πατηθεί το κουμπί
def delete_btn_callback(conv_id_to_delete):
    current_token = st.session_state.get('access_token')
    del_success, del_msg = delete_conversation(current_token, conv_id_to_delete)

    if del_success:
        current_conv_id = st.session_state.get('current_conversation_id') or 0

        if int(current_conv_id) == int(conv_id_to_delete):
            st.session_state['current_conversation_id'] = 0
            st.session_state['current_messages'] = []
    else:
        st.toast(del_msg)


with st.sidebar:
    st.header("Ιστορικό Συζητήσεων")

    if st.button("Νέα Συζήτηση", width="stretch"):  # question for width
        st.session_state['current_conversation_id'] = 0
        st.session_state['current_messages'] = []
        st.rerun()

    st.divider()

    success, conversations = get_user_conversations(token)

    if success and conversations:
        for conv in conversations:
            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(f"{conv['title']}", key=f"load_{conv['id']}", width="stretch"):
                    st.session_state['current_conversation_id'] = conv['conversation_id']
                    # retrieve messages here (TBD)
                    st.info("Επιλέχθηκε η συζήτηση, αλλά περιμένουμε το endpoint των μηνυμάτων!")

            with col2:
                st.button("X", key=f"del_{conv['id']}",
                          help="Διαγραφή",
                          on_click=delete_btn_callback,
                          args=[conv['id']])

    elif not success:
        st.error("Αδυναμία φόρτωσης ιστορικού.")
    else:
        st.info("Δεν υπάρχουν παλιές συζητήσεις.")

st.title("Chat")

for msg in st.session_state['current_messages']:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Γράψε ένα μήνυμα..."):
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state['current_messages'].append({'role': 'user', 'content': prompt})

    with st.spinner("Το AI πληκτρολογεί..."):
        conv_id = st.session_state['current_conversation_id']
        chat_success, result = send_chat_message(token, conv_id, prompt)

    if chat_success:
        ai_reply = result.get("ai_response")
        new_conv_id = result.get("conversation_id")

        st.session_state['current_messages'].append({'role': 'assistant', 'content': ai_reply})

        if st.session_state['current_conversation_id'] == 0:
            st.session_state['current_conversation_id'] = new_conv_id
            st.rerun()  # Refresh για εμφάνιση της συζήτησης στην μπάρα αριστερά

        with st.chat_message("assistant"):
            st.write(ai_reply)

    else:
        st.error(f"Σφάλμα: {result}")
