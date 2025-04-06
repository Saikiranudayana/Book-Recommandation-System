from flask import Flask,render_template,request
import pickle
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    popular_df = pickle.load(open('popular.pkl','rb'))
    pt = pickle.load(open('pt.pkl','rb'))
    books = pickle.load(open('books.pkl','rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))
except Exception as e:
    print(f"Error loading pickle files: {str(e)}")
    raise

app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    try:
        user_input = request.form.get('user_input')
        if not user_input:
            return render_template('recommend.html', error="Please enter a book title")
            
        if user_input not in pt.index:
            return render_template('recommend.html', error="Book not found in database")
            
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)

        return render_template('recommend.html', data=data)
    except Exception as e:
        return render_template('recommend.html', error=str(e))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)