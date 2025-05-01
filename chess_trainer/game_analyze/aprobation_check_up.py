import pandas as pd
import joblib

best_model = joblib.load('../model/chess_rating_model.pkl')
scaler = joblib.load('../model/scaler.pkl')

data = pd.read_csv('../model/chess_data.csv')

def predict_user_rating(data):
    # Масштабирование данных
    features = data[['first_line_percentage', 'second_line_percentage', 'third_line_percentage', 'bad_moves_percentage']]
    features_scaled = scaler.transform(features)

    # Предсказание рейтинга
    predictions = best_model.predict(features_scaled)
    return predictions

# Применение модели к данным
data['predicted_rating'] = predict_user_rating(data)

# Сохранение результатов в новый CSV файл
data.to_csv('chess_data_with_predictions.csv', index=False)

print("Предсказания добавлены и сохранены в 'chess_data_with_predictions.csv'.")
