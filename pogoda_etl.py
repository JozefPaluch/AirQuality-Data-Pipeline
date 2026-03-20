import requests
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

cities = {
    "Warszawa": {"lat": 52.2298, "lon": 21.0118},
    "Kraków": {"lat": 50.0614, "lon": 19.9366},
    "Wrocław": {"lat": 51.1079, "lon": 17.0385},
    "Łódź": {"lat": 51.7592, "lon": 19.4560},
    "Poznań": {"lat": 52.4064, "lon": 16.9252},
    "Gdańsk": {"lat": 54.3520, "lon": 18.6466},
    "Szczecin": {"lat": 53.4289, "lon": 14.5530},
    "Bydgoszcz": {"lat": 53.1235, "lon": 18.0084},
    "Lublin": {"lat": 51.2465, "lon": 22.5684},
    "Katowice": {"lat": 50.2584, "lon": 19.0275}
}

all_data = []

for city, coords in cities.items():
    
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={coords['lat']}&longitude={coords['lon']}&current=pm10,pm2_5&timezone=Europe/Warsaw"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()

        pm10 = data['current']['pm10']
        pm2_5 = data['current']['pm2_5']
        czas = data['current']['time']
        
        all_data.append({
            "miasto": city,
            "data_pomiaru": czas,
            "pm10": pm10,
            "pm2_5": pm2_5
        })

df = pd.DataFrame(all_data)

print(df)

DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)

    cur = conn.cursor()

    tworzenie_tabeli_sql = """
    CREATE TABLE IF NOT EXISTS historia_smogu (
        id SERIAL PRIMARY KEY,
        miasto VARCHAR(50),
        data_pomiaru TIMESTAMP,
        pm10 NUMERIC,
        pm2_5 NUMERIC,
        UNIQUE (miasto, data_pomiaru)
    );
    """
    cur.execute(tworzenie_tabeli_sql)
    print("Sprawdzono tabelę 'historia_smogu'.")

    insert_sql = """
    INSERT INTO historia_smogu (miasto, data_pomiaru, pm10, pm2_5)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (miasto, data_pomiaru) DO NOTHING;
    """

    for index, row in df.iterrows():
        cur.execute(insert_sql, (row['miasto'], row['data_pomiaru'], row['pm10'], row['pm2_5']))

    conn.commit()

except Exception as e:

    print(f"Błąd: {e}")
    
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()    
        print("Połączenie z bazą zakończone.")