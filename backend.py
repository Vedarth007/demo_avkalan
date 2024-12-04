import faiss
import pandas as pd
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer
import logging

class Backend:
    def __init__(self, db_path='database.db'):
        self.logger = self.setup_logging()
        self.db_path = db_path
        self.model = self.load_model()
        self.conn = self.create_db_connection()
        self.vector_index = None
        self.initialize_data()

    def setup_logging(self):
        logger = logging.getLogger('Backend')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def load_model(self):
        try:
            return SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise

    def create_db_connection(self):
        try:
            return sqlite3.connect(self.db_path, check_same_thread=False)  # Allow access from different threads
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise

    def initialize_data(self):
        try:
            self.questions_df = self.load_questions()
            self.setup_database()
            self.setup_vector_index()
        except Exception as e:
            self.logger.error(f"Error during initialization: {str(e)}")
            raise

    def load_questions(self):
        try:
            df = pd.read_csv('data/WCG_data.csv', encoding='ISO-8859-1')
            df.columns = df.columns.str.strip()
            df.rename(columns={'Question': 'question', 'Question Id': 'question_id'}, inplace=True)
            df['question'] = df['question'].str.strip()
            return df
        except Exception as e:
            self.logger.error(f"Error loading questions: {str(e)}")
            raise

    def setup_database(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                question_id TEXT PRIMARY KEY,
                question TEXT,
                category TEXT,
                country TEXT
            )''')

            for _, row in self.questions_df.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO questions 
                (question_id, question, category, country)
                VALUES (?, ?, ?, ?)
                ''', (row['question_id'], row['question'], row['Category'], row['Country']))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error setting up database: {str(e)}")
            self.conn.rollback()
            raise

    def setup_vector_index(self):
        try:
            questions = self.questions_df['question'].tolist()
            embeddings = np.array([self.model.encode(q) for q in questions]).astype(np.float32)
            self.vector_index = faiss.IndexFlatL2(embeddings.shape[1])
            self.vector_index.add(embeddings)
        except Exception as e:
            self.logger.error(f"Error setting up vector index: {str(e)}")
            raise

    def filter_questions(self, category):
        try:
            if category.lower() == 'all':
                query = "SELECT * FROM questions"
                return pd.read_sql(query, self.conn)
                
            query = """
            SELECT * FROM questions 
            WHERE category = :category 
            """
            return pd.read_sql(query, self.conn, params={'category': category})
        except Exception as e:
            self.logger.error(f"Error filtering questions: {str(e)}")
            raise

    def semantic_search(self, query, filtered_df):
        try:
            filtered_questions = filtered_df['question'].tolist()
            filtered_embeddings = np.array([self.model.encode(q) for q in filtered_questions]).astype(np.float32)
            query_embedding = self.model.encode(query).astype(np.float32).reshape(1, -1)

            index = faiss.IndexFlatL2(filtered_embeddings.shape[1])
            index.add(filtered_embeddings)
            distances, indices = index.search(query_embedding, k=len(filtered_embeddings))

            max_similarity = 1 / (1 + distances[0][0])
            lower_bound = max_similarity * 0.95
            results = [
                (1 / (1 + distances[0][i]), indices[0][i]) 
                for i in range(len(distances[0])) 
                if 1 / (1 + distances[0][i]) >= lower_bound
            ]
            return results
        except Exception as e:
            self.logger.error(f"Error in semantic search: {str(e)}")
            raise

    # def get_user_ids(self, stakeholder, user , country_grouping):
    #     try:
    #         users_df = pd.read_csv('data/user_table.csv')
    #         filtered_df = users_df[
    #             (users_df['stakeholder_type'] == stakeholder) & 
    #             (users_df['Country_grouping'] == country_grouping) &
    #             (users_df['username'] == user)
    #         ]
    #         return filtered_df['user_id'].tolist()
    #     except Exception as e:
    #         self.logger.error(f"Error getting user IDs: {str(e)}")
    #         raise

    # def get_user_ids(self, stakeholder, user, country_grouping):
    #     try:
    #         users_df = pd.read_csv('data/user_table.csv')
            
    #         # If username is None, don't filter by 'username', just by stakeholder and country_grouping
    #         if user=='none':
    #             filtered_df = users_df[
    #                 (users_df['stakeholder_type'] == stakeholder) & 
    #                 (users_df['Country_grouping'] == country_grouping)
    #             ]
    #         else:
    #             filtered_df = users_df[
    #                 (users_df['stakeholder_type'] == stakeholder) & 
    #                 (users_df['Country_grouping'] == country_grouping) & 
    #                 (users_df['username'] == user)
    #             ]
            
    #         return filtered_df['user_id'].tolist()
    #     except Exception as e:
    #         self.logger.error(f"Error getting user IDs: {str(e)}")
    #         raise
    def get_user_ids(self, stakeholder=None, user=None, country_grouping=None):
        try:
            users_df = pd.read_csv('data/user_table.csv')
            
            conditions = []
            if stakeholder and stakeholder != 'All':
                conditions.append(users_df['stakeholder_type'] == stakeholder)
            if country_grouping and country_grouping != 'All':
                conditions.append(users_df['Country_grouping'] == country_grouping)
            if user and user != 'All':
                conditions.append(users_df['username'] == user)
                
            filtered_df = users_df if not conditions else users_df[pd.concat(conditions, axis=1).all(axis=1)]
            return filtered_df['user_id'].tolist()
            
        except Exception as e:
            self.logger.error(f"Error getting user IDs: {str(e)}")
            raise

    # def get_answers(self, question_ids, user_ids):
    #     try:
    #         answers_df = pd.read_csv('data/answer_table.csv')
    #         return answers_df[
    #             (answers_df['question_id'].isin(question_ids)) & 
    #             (answers_df['user_id'].isin(user_ids))
    #         ]
    #     except Exception as e:
    #         self.logger.error(f"Error getting answers: {str(e)}")
    #         raise

    def get_answers(self, question_ids, user_ids):
            try:
                # Read the answers from the CSV file
                answers_df = pd.read_csv('data/answer_table.csv')
                
                # Filter answers based on the given question_ids and user_ids
                filtered_answers = answers_df[
                    (answers_df['question_id'].isin(question_ids)) & 
                    (answers_df['user_id'].isin(user_ids))
                ]
                
                return filtered_answers
            
            except Exception as e:
                self.logger.error(f"Error getting answers: {str(e)}")
                raise
            
    def _del_(self):
        if hasattr(self, 'conn'):
            self.conn.close()
