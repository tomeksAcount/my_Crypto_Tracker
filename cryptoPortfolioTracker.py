import os

import requests

from dataclasses import dataclass
from datetime import datetime

from db import get_connection

API_KEY = os.getenv("CG-H52ZY6zyakAqceRFYGfUy9y9")  # reads the key from .env
API_HEADERS = {"x-cg-demo-api-key": API_KEY} if API_KEY else {}


@dataclass
class cryptoRecord:
    id: int =0
    cryptoName: str= ""
    amount: float = 0.0
    date: str = ""
    price_at_purchase: float = 0.0


def get_data():
    cnx = get_connection()
    if cnx is None:
        return []
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM crypto")
    coins = [cryptoRecord(row[0], row[1], float(row[2]), row[3], float(row[4]))
             for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return coins
coins = get_data()


def gettingPrice(coins, crypto_id, date):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/history?date={date}&localization=false'
    try:
        response = requests.get(url, headers=API_HEADERS, timeout=10)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.json().get('market_data', {}).get('current_price', {}).get('usd')

def insertingnewcoin(Crypto,Amount,DateOfPurchase):
    cnx = get_connection()
    if cnx is None:
        return False
    cursor = cnx.cursor()
    query = ("INSERT INTO crypto (Crypto, Amount, DateOfPurchase) VALUES (%s, %s, %s)")
    cursor.execute(query, (Crypto, Amount, DateOfPurchase))

    last_id = cursor.lastrowid

    # Fetch the historical price
    price = gettingPrice(coins, Crypto.lower(), DateOfPurchase)
    if price is None:
        cnx.rollback()  # undo the INSERT so no coin is saved without a price
        cursor.close()
        cnx.close()
        print("Couldn't get the price for that date, so the coin wasn't saved. Try again later.")
        return False

    # Update the record with the fetched price
    update_query = "UPDATE crypto SET price_at_purchase = %s WHERE id = %s"
    cursor.execute(update_query, (price, last_id))

    # Commit the transaction
    cnx.commit()

    # Close the connection
    cursor.close()
    cnx.close()
    print("Coin inserted successfully!")
    return True


def value(coins):
    total_value = 0.0
    for coin in coins:
        current_price = current_prices.get(coin.cryptoName, {}).get("usd", 0)
        total_value += coin.amount * current_price
        finalTot = "{:,}".format(total_value)
        

    return total_value


def calculate_crypto_distribution(coins,total_value):
 
    total_percentage = 0
  
    crypto_values = {}
    for coin in coins:
        name = coin.cryptoName
        value = coin.amount * current_prices.get(name, {}).get("usd", 0)
        if name in crypto_values:
            crypto_values[name] += value
        else:
            crypto_values[name] = value
    
  
    crypto_percentages = {}
    if total_value == 0:

        for name in crypto_values:
            crypto_percentages[name] = 0.0
    else:
        for name, value in crypto_values.items():
            crypto_percentages[name] = round((value / total_value) * 100, 2)
  
        total_percentage = total_percentage + crypto_percentages[name]
        
    
    return crypto_percentages


def fetch_current_prices(crypto_names):
    
    ids = ",".join(crypto_names) 
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    response = requests.get(url, headers=API_HEADERS)
    
    return response.json() if response.status_code == 200 else {}

crypto_names = list(set(crypto.cryptoName for crypto in coins))
current_prices = fetch_current_prices(crypto_names)

def calculate_profits(coins,current_prices,crypto_names):
    
    
    profits = {}
    for crypto in coins:
        name = crypto.cryptoName
        amount = crypto.amount
        price_at_purchase = crypto.price_at_purchase
        current_price = current_prices.get(name, {}).get("usd", 0) 
        profit = (current_price - price_at_purchase) * amount
        if name in profits:
            profits[name] += profit
        else:
            profits[name] = profit
    
    
    return profits


def dis(profits):


    profits1 = [profits[name] for name in profits]
    names1 = [name for name in profits]
    return profits1,names1


def coiorder(coins):
    n = len(coins)
    swapped = True
    while swapped:
        swapped = False
        for i in range(n-1):
            if coins[i].cryptoName.lower() > coins[i+1].cryptoName.lower():  # Sorting by name (case-insensitive)
                coins[i], coins[i+1] = coins[i+1], coins[i]  # Swap the elements
                swapped = True
        n -= 1
    return coins


def bubblesort(profits1,names1):
    n = len(profits1)
    swapped = True
    while swapped:
        swapped = False
        for i in range(n-1):
            if profits1[i] < profits1[i+1]:
                profits1[i],profits1[i+1] = profits1[i+1],profits1[i]
                names1[i],names1[i+1] = names1[i+1],names1[i]
                
                swapped = True
        n -= 1
    return profits1, names1


def profsearch(profits1,names1):
    low = 0
    high = len(names1) - 1
    target = input("Enter the name of the coin you want to find the profit/loss of: ").strip().lower()

    while low <= high:
        mid = (low + high) // 2
        midcoin = names1[mid].lower()# Convert to lowercase for case-insensitive search

        if midcoin == target:
            return f"you have made a profit of {profits1[mid]} on coin {midcoin}"  # Found the coin, return date and amount
        elif midcoin.lower() > target:
            high = mid - 1  
        else:
            low = mid + 1  
    return "Coin not found."


def price_comparison(coins,current_prices,target):
    """Price per coin at each purchase of the target coin vs the price today."""
    today = current_prices.get(target, {}).get("usd")
    lines = []
    for coin in coins:
        if coin.cryptoName.lower() == target:
            line = f"{coin.date}: bought at ${coin.price_at_purchase:,.2f} per coin"
            if today is not None:
                line += f", today ${today:,.2f}"
                if coin.price_at_purchase:
                    change = (today - coin.price_at_purchase) / coin.price_at_purchase * 100
                    line += f" ({change:+.1f}%)"
            lines.append(line)
    return "\n".join(lines)


def coinbinarysearch(coins):
    low = 0
    high = len(coins) - 1
    target = input("Enter the name of the coin you want to find the amount you bought and when: ").strip().lower()

    while low <= high:
        mid = (low + high) // 2  
        mid_coin = coins[mid].cryptoName.lower()  # Convert to lowercase for case-insensitive search

        if mid_coin == target:
            # The list is sorted by name, so other purchases of this coin are right next to it
            first = mid
            while first > 0 and coins[first - 1].cryptoName.lower() == target:
                first -= 1
            purchases = []
            i = first
            while i < len(coins) and coins[i].cryptoName.lower() == target:
                purchases.append(f"you bought {coins[i].amount} of {target} on the {coins[i].date}")
                i += 1
            return "\n".join(purchases)
        elif mid_coin > target:
            high = mid - 1  
        else:
            low = mid + 1  
    
    return "Coin not found"  # If the coin is not found


def orderprice(coins,current_prices,crypto_names):
    arra = []
    names = []
    for name in crypto_names:
 
        price = current_prices.get(name, {}).get("usd",0)
        
        arra.append(price)
        names.append(name)

    n = len(arra)
    swapped = True
    while swapped and n > 0:
        swapped = False
        for i in range(n-1):
            if arra[i] < arra[i+1]:  # most expensive first
             

                arra[i],arra[i+1] = arra[i+1],arra[i]
                names[i],names[i+1] = names[i+1],names[i]
                swapped = True
        n = n -  1
    print(f"{'Coin Name':<15}Price (USD)")
    print("-"*25)
    for i in range(len(names)):  
        print(f"{names[i]} : costs ${arra[i]:,.2f}")


def get_max_supply(crypto_name):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_name}"   
    response = requests.get(url, haeaders=API_HEADERS)
    if response.status_code == 200:
        data = response.json()
        max_suply = data.get("market_data",{}).get("max_supply",None)
        return max_suply


def ask_amount(maxsup):
    while True:
        try:
            Amount = float(input("enter the amount you want to buy: ").strip())
        except ValueError:
            print("Please enter a number, e.g. 0.5")
            continue
        if Amount <= 0:
            print("The amount must be more than 0.")
        elif maxsup is not None and Amount >= float(maxsup):  # some coins have no max supply
            print("you cant have more than total coin supply")
        else:
            return Amount


def ask_date():
    current_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    while True:
        DateOfPurchase = input("Enter the date you purchased (dd-mm-yyyy): ").strip()
        try:
            date = datetime.strptime(DateOfPurchase, "%d-%m-%Y")
        except ValueError:
            print("Enter the date as dd-mm-yyyy using dashes. Example: 14-03-2025")
            continue
        if date >= current_date:
            print("The date must be before today.")
        else:
            return DateOfPurchase


def back_to_menu():
    input("press b to return to main menu")


def menudisplay(coins):
    while True:
    
        print("\nCryptocurrency Portfolio Manager")
        print("1. Insert new coin")
        print("2. display the total portfolio value")
        print("3. find the profit of chosen coin")
        print("4. display distribution of all coins")
        print("5. display profits of all coins")
        print("6. find the amount bought at a certain date of a certain crypto.")
        print("7 show cryptos from most expensive to cheapest")
        print("8. exit the program")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 30,
                "page": 1,
                "sparkline": False
            }
            
            response = requests.get(url, params=params, headers=API_HEADERS)
            if response.status_code == 200:
                data = response.json()
                for idx, coin in enumerate(data, start=1):
                    print(f"{idx}. {coin['name']}")
            else:
                print("Error fetching data:", response.status_code, response.text)
                
            Crypto = input("Enter the name of crypto you want to add: ").strip()
            while Crypto != Crypto.lower(): 
                print("Crypto names need to be in lowercase.")
                Crypto = input("Enter the name of crypto you want to add: ").strip()

            maxsup = get_max_supply(Crypto)
            Amount = ask_amount(maxsup)
            DateOfPurchase = ask_date()

            if insertingnewcoin(Crypto,Amount,DateOfPurchase):
                coins[:] = get_data()  # reload so the new coin shows up straight away
                if Crypto not in crypto_names:
                    crypto_names.append(Crypto)
                current_prices.update(fetch_current_prices([Crypto]))

        elif choice == "2":
            print(value(coins))
            back_to_menu()

        elif choice == "3":
            profits = calculate_profits(coins,current_prices,crypto_names)
            names1 = sorted(profits)  # binary search needs the names in alphabetical order
            profits1 = [profits[name] for name in names1]
            print(profsearch(profits1,names1))

            answer = input("Do you want to see the price you paid per coin vs today's price? (y/n): ").strip().lower()
            if answer == "y":
                target = input("Enter the name of the coin: ").strip().lower()
                comparison = price_comparison(coins,current_prices,target)
                print(comparison if comparison else "Coin not found.")

        elif choice == "4":
            total_value = value(coins)
            print(calculate_crypto_distribution(coins,total_value))
            back_to_menu()

        elif choice == "5":
            profits = calculate_profits(coins,current_prices,crypto_names)
            profits1,names1 = bubblesort(*dis(profits))
            for i in range(len(names1)):
                print(f"{names1[i]} has made a profit of ${round(profits1[i],2)}")

        elif choice == "6":
            for n in range(len(coins)):
                print(coins[n].cryptoName)
            sorted_coins = coiorder(coins)
            print(coinbinarysearch(sorted_coins))
            back_to_menu()

        elif choice == "7":
            orderprice(coins,current_prices,crypto_names)
            back_to_menu()

        elif choice == "8":
            print("Exiting program...")
            break


if __name__ == "__main__":
    menudisplay(coins)
