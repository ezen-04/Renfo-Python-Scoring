# Importaion des différentes bibliothèques
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text

# Dictionnaire des tickers et leurs tables correspondantes
tickers = {
    "AAPL": "prices_AAPL", # Apple Inc.
    "MSFT": "prices_MSFT", # Microsoft Corporation
    "BP.L": "prices_BP_L", # BP plc
    "HSBA.L": "prices_HSBA_L", # HSBC Holdings plc
    "7203.T": "prices_7203_T", # Toyota Motor Corporation
    "6758.T": "prices_6758_T", # Sony Corporation
    "TTE.PA": "prices_TTE_PA", # TotalEnergies SE
    "MC.PA": "prices_MC_PA", # LVMH Moët Hennessy Louis Vuitton SE
    "SIE.DE": "prices_SIE_DE", # Siemens AG
    "BMW.DE": "prices_BMW_DE" # Bayerische Motoren Werke AG
}

# Connection à la base de données MySQL
engine = create_engine("mysql+pymysql://root:@localhost/market_db")


# Création des tables pour chaque ticker dans la base de données
with engine.connect() as conn:
    for table_name in tickers.values():
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            open DECIMAL(15,4),
            high DECIMAL(15,4),
            low DECIMAL(15,4),
            close DECIMAL(15,4),
            adj_close DECIMAL(15,4),
            volume BIGINT
        );
        """
        conn.execute(text(create_table_sql))
        print(f"✅ Table {table_name} créée.")

# Téléchargement et insertion des données pour chaque ticker
for ticker, table_name in tickers.items():
    print(f"📥 Téléchargement de {ticker}...")
    stock = yf.Ticker(ticker)
    data = stock.history(start="2010-01-01", end="2026-04-30")
    
    if data.empty:
        print(f"⚠️ Pas de données pour {ticker}, ignoré.")
        continue
    
    df = pd.DataFrame({
        "date": data.index,
        "open": data["Open"].values,
        "high": data["High"].values,
        "low": data["Low"].values,
        "close": data["Close"].values,
        "adj_close": data["Close"].values if "Adj Close" not in data.columns else data["Adj Close"].values,
        "volume": data["Volume"].values
    })
    
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"✅ Données insérées dans {table_name}")
