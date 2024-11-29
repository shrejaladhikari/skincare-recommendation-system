from flask import Flask, request, jsonify, render_template
import pandas as pd

# Load the dataset
dataset_path = 'data/cosmetic_p.csv'
skincare_data = pd.read_csv(dataset_path)

# Preprocess the dataset
skincare_data['price'] = pd.to_numeric(skincare_data['price'], errors='coerce')
skincare_data['rank'] = pd.to_numeric(skincare_data['rank'], errors='coerce')
skincare_data = skincare_data.dropna(subset=['price', 'rank'])
skin_types = ['Combination', 'Dry', 'Normal', 'Oily', 'Sensitive']
for skin_type in skin_types:
    skincare_data[skin_type] = skincare_data[skin_type].astype(bool)

# Recommendation logic
def recommend_products(skin_type, min_price=0, max_price=1000, min_rank=0):
    filtered_data = skincare_data[skincare_data[skin_type]]
    filtered_data = filtered_data[(filtered_data['price'] >= min_price) & (filtered_data['price'] <= max_price)]
    filtered_data = filtered_data[filtered_data['rank'] >= min_rank]
    recommendations = filtered_data.sort_values(by='rank', ascending=False)
    return recommendations[['Label', 'brand', 'name', 'price', 'rank', 'ingredients']]

# Initialize Flask app
app = Flask(__name__)

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Define the recommendation API endpoint
@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        skin_type = request.args.get('skin_type', type=str)
        min_price = request.args.get('min_price', default=0, type=float)
        max_price = request.args.get('max_price', default=1000, type=float)
        min_rank = request.args.get('min_rank', default=0, type=float)

        if skin_type not in skin_types:
            return jsonify({'error': 'Invalid skin type'}), 400

        recommendations = recommend_products(skin_type, min_price, max_price, min_rank)
        return recommendations.to_json(orient='records')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
