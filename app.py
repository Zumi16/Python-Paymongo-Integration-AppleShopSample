from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

products = [
    {
        "id": 1,
        "name": "iPhone 15 Pro",
        "description": "The ultimate iPhone experience with A16 Bionic chip",
        "image": "iphone_15_pro.jpg",
        "price": 79900.00,
        "panel_class": "panel-primary"
    },
    {
        "id": 2,
        "name": "MacBook Air M2",
        "description": "Ultra-light and powerful with M2 chip",
        "image": "macbook_air_m2.jpg",
        "price": 59900.00,  
        "panel_class": "panel-primary"
    },
    {
        "id": 3,
        "name": "iPad Pro 11\"",
        "description": "The most powerful iPad, perfect for professionals",
        "image": "ipad_pro.jpg",
        "price": 36900.00,  
        "panel_class": "panel-primary"
    },
    {
        "id": 4,
        "name": "Apple Watch Series 8",
        "description": "The best smartwatch for health and fitness tracking",
        "image": "apple_watch_series_9.jpg",
        "price": 28900.00,  
        "panel_class": "panel-primary"
    },
    {
        "id": 5,
        "name": "AirPods Pro",
        "description": "Active Noise Cancellation and Transparency mode",
        "image": "airpods_pro.jpg",
        "price": 17900.00,  
        "panel_class": "panel-primary"
    },
    {
        "id": 6,
        "name": "iMac 24\"",
        "description": "Stunning 4.5K Retina display and powerful performance",
        "image": "imac_24.jpg",
        "price": 119900.00,  
        "panel_class": "panel-primary"
    }
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    product = next((item for item in products if item["id"] == product_id), None)
    if product:
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] += 1
                flash(f'{product["name"]} quantity increased to {item["quantity"]}!')
                break
        else:
            product_copy = product.copy()
            product_copy['quantity'] = 1
            session['cart'].append(product_copy)
            flash(f'{product["name"]} added to cart!')

    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        flash('Product removed from cart!')

    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'cart' in session:
        for item in session['cart']:
            item_id = str(item['id'])
            item['quantity'] = int(request.form.get(f'quantity_{item_id}', item['quantity']))

    flash('Cart updated!')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))

@app.route('/checkout')
def checkout():
    PAYMONGO_API_KEY = 'Your-Own-KEY'
    url = 'https://api.paymongo.com/v1/links'
    
    total_amount = sum(item['price'] * item['quantity'] for item in session.get('cart', [])) * 100
    
    payload = {
        "data": {
            "attributes": {
                "amount": int(total_amount),
                "description": "Apple Products Online Store Purchase",
                "remarks": "Thank you for your purchase!",
                "currency": "PHP",
                "redirect": {
                    "success": url_for('success', _external=True),
                    "failed": url_for('failed', _external=True)
                }
            }
        }
    }
    
    api_key_encoded = base64.b64encode(f'{PAYMONGO_API_KEY}:'.encode('utf-8')).decode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {api_key_encoded}'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print(response_data)

        payment_url = response_data['data']['attributes']['checkout_url']
        return redirect(payment_url)
    except requests.exceptions.RequestException as e:
        flash(f'Error with payment: {e}')
        return redirect(url_for('cart'))
    except KeyError:
        flash('Unexpected response structure from PayMongo')
        return redirect(url_for('cart'))

@app.route('/success')
def success():
    flash('Payment successful!')
    session.pop('cart', None)
    return redirect(url_for('index'))

@app.route('/failed')
def failed():
    flash('Payment failed. Please try again.')
    return redirect(url_for('cart'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        flash(f'Thank you for signing up for our deals, {email}!')
        return redirect(url_for('index'))
    else:
        flash('Invalid email address.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
