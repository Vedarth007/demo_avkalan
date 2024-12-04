import streamlit as st
import os
from backend import Backend
import openai

openai.api_key = st.secrets["API_KEY"]

class StreamlitApp:
    def __init__(self):
        # Ensure session state variables are initialized only once
        if 'backend' not in st.session_state:
            st.session_state.backend = Backend()

        # Initialize session state variables only if they don't exist already
        if 'categories' not in st.session_state:
            st.session_state.categories = [
                'All',
                'aGC: Landscape',
                'aGC: Trial A & Trial B: Value & Trial Design Assessment',
                '[Payer] aGC: Trial A & Trial B : HTA Assessment',
                '[Payer] aGC: Trial A & Trial B: Standalone Price Assessment',
                '[Payer] aGC: Trial C: Impact on HTA & Price',
                'mNSCLC: Landscape',
                'mNSCLC: Value & Trial Design Assessment',
                '[Payer] mNSCLC: HTA Assessment',
                '[Payer] mNSCLC: Standalone Price Assessment',
                '[Payer] mNSCLC: Impact of Trial 4',
                'Cross-Indication Assessment (~20 min)'
            ]  # Your categories here
        if 'stakeholders' not in st.session_state:
            st.session_state.stakeholders = [
                'All',
                'GC_KOL', 'NSCLC_KOL', 'FR_Payer', 
                'DE_Payer', 'IT_Payer', 'ES_Payer'
            ]  # Your stakeholders here
        if 'countries' not in st.session_state:
            st.session_state.countries = ['All', 'DAI-475' ]  # Your countries here
        if 'users' not in st.session_state:
            st.session_state.users = [
                'All',
                'Aziz Zanaan', 'Peter Thuss-Patience',
                'Javier Gallego Plazas', 'Giuseppe Aprile', 
                'Nicolas Girard', 'Christian Grohe', 'Mariano Provencio Pulla',
                'Arsela Prelaj', 'Eric Baseilhac', 'Jean-Francois Bergmann',
                'Marc Bardou', 'Jean-Marc Grognet', 'Stefan Lhachimi',
                'Peter Kolominsky-Rabas', 'Maywald', 'Flume', 'Claudio Ferri', 
                'Fabrizio Gianfrate', 'Stefano Capri', 'Entela Xoxi', 'Josep Darba',
                'Mestre Ferrandiz', 'Joan Antoni Valles Callol', 'Jaime Espin'
            ]  # Your users here
        if 'CountryGrouping' not in st.session_state:
            st.session_state.CountryGrouping = ['All','EU', 'FR', 'DE', 'IT', 'ES']
   # Your country groupings here

    def apply_styles(self):

        st.markdown("""
<style>
            [data-testid="stSidebar"]{
                background-color: #ADD8E6 !important;
                border-right: 2px solid #4F94D4 !important;
            }
            .title {
                text-align: center;
                font-size: 40px;
                font-weight: bold;
                margin-top: 10px;
            }
            .subtitle {
                text-align: center;
                font-size: 20px;
                margin-bottom: 20px;
              
            }
            
             .stSelectbox div[data-baseweb="select"], 
                    .stTextInput {
                border: 2px solid #4F94D4 !important;
                    border-radius: 10px !important; padding: 5px;
            }
                    
              .stButton button {
                background-color: lightblue !important;
                border-radius: 5px;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

#     def apply_styles(self):
#         st.markdown("""
# <style>
                    
#         [data-testid="stSidebar"] {
#                 background-color: #ADD8E6 !important;
#                 border-right: 2px solid #4F94D4 !important;
#             }
                    
#             .title {
#                 text-align: center;
#                 font-size: 40px;
#                 font-weight: bold;
#                 margin-top: 10px;
#             }
#             .subtitle {
#                 text-align: center;
#                 font-size: 20px;
#                 margin-bottom: 20px;
#             }
#             .stSelectbox div[data-baseweb="select"], 
#                     .stTextInput {
#                 border: 2px solid #4F94D4 !important;
#                     border-radius: 10px !important; padding: 5px;
#             }
                    
#             .stButton button {
#                 background-color: lightblue !important;
#                 border-radius: 5px;
#                 font-weight: bold;
#             }
# </style>
#         """, unsafe_allow_html=True)



    def setup_layout(self):
        with st.sidebar:
            st.title("Menu")
            st.radio("Navigation", ["Chat Application", "Settings", "Help","FAQ"])

        col1, col2, col3 = st.columns(3)
        with col2:
            logo_path = "/Users/jyotscharan/Desktop/project copy/PHOTO-2024-12-04-20-48-13.jpg"
            if os.path.exists(logo_path):
                st.image(logo_path, width=200, use_container_width=True)

            # else:
            #     st.warning(f"Logo not found at: {logo_path}")

        st.markdown('<div class="title">How can I help you?</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Please fill out these filters</div>', unsafe_allow_html=True)

    def create_filters(self):
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox('Select Category:', st.session_state.categories)
        with col2:
            stakeholder = st.selectbox('Select Stakeholder:', st.session_state.stakeholders)
        with col3:
            country = st.selectbox('Select Project:', st.session_state.countries)

        
        # Second row with two filters
        col4, col5 = st.columns(2)
        with col4:
            user = st.selectbox('Select User:', st.session_state.users)
        with col5:
            country_grouping = st.selectbox('Select User Grouping:', st.session_state.CountryGrouping)
        return category, stakeholder, country, user, country_grouping

    def process_query(self, query, category, stakeholder, country, user, country_grouping):
        if not query:
            return

        try:
            # category_filter = None if not category == 'All' else category
            # country_filter = None if not country == 'All' else country
        
            filtered_df = st.session_state.backend.filter_questions(category)

            if filtered_df.empty:
                st.warning("No questions found")
                return

            search_results = st.session_state.backend.semantic_search(query, filtered_df)

            if not search_results:
                st.info("No similar questions found")
                return

            question_ids = [str(filtered_df.iloc[idx]['question_id']) for _, idx in search_results]
            #st.write("Retrieved Question IDs:", question_ids)

            user_ids = st.session_state.backend.get_user_ids(stakeholder, user, country_grouping)
            #st.write("Retrieved User IDs:", user_ids)

            if not user_ids:
                st.warning("No results found in the database")
                return

            filtered_answers = st.session_state.backend.get_answers(question_ids, user_ids)

            if filtered_answers.empty:
                st.info("No answers found.")
                return

            # st.dataframe(filtered_answers)

            # Pass the first answer to OpenAI for processing
            if not filtered_answers.empty:
                answer = filtered_answers.iloc[0]['answer']
                  # Assuming 'answer' is the column name
                #st.write("answerss", filtered_answers)
                processed_answer = self.process_with_openai(answer)
                st.write("Assistant:", processed_answer)

        except Exception as e:
            st.error(f"An error occurred while processing your query: {str(e)}")

    def process_with_openai(self, answer):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": '''You are a drug advisor and you will be provided some user answers and you need to . Some rules you must follow:
                    1. First if the input is a single word then return it as it is.
                    2. If it is a single sentence then make sure it is grammatically correct and makes sense but only provide what is written in it and don't make things by yourself.
                    3. If it is a paragraph answer then summarize it to cover the complete context and make sure it has all the nouns present in the original content. '''},
                    {"role": "user", "content": answer}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            st.error(f"An error occurred while processing with OpenAI: {str(e)}")
            return None

    def run(self):
        self.apply_styles()
        self.setup_layout()

        category, stakeholder, country, user, country_grouping = self.create_filters()
        query = st.text_input("Enter your query:")
        submit = st.button("Search")
        if submit:
            self.process_query(query, category, stakeholder, country, user, country_grouping)

if __name__ == '__main__':
    app = StreamlitApp()
    app.run()
