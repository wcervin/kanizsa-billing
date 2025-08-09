#!/usr/bin/env python3
"""
Kanizsa Billing Service API
Provides billing and payment processing capabilities
"""

import os
import time
from flask import Flask, jsonify, request
import stripe
import paypalrestsdk

app = Flask(__name__)

# Initialize payment gateways
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": os.environ.get('PAYPAL_CLIENT_ID', ''),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET', '')
})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'kanizsa-billing'
    })

@app.route('/payment/process', methods=['POST'])
def process_payment():
    """Process payment through Stripe"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        payment_method = data.get('payment_method')
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            confirm=True
        )
        
        return jsonify({
            'status': 'success',
            'payment_intent_id': intent.id,
            'amount': amount,
            'currency': currency
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400

@app.route('/subscriptions/create', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        plan_id = data.get('plan_id')
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': plan_id}]
        )
        
        return jsonify({
            'status': 'success',
            'subscription_id': subscription.id,
            'customer_id': customer_id,
            'plan_id': plan_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400

@app.route('/invoices/generate', methods=['POST'])
def generate_invoice():
    """Generate an invoice"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        period = data.get('period')
        
        # Generate invoice
        invoice = stripe.Invoice.create(
            subscription=subscription_id,
            collection_method='charge_automatically'
        )
        
        return jsonify({
            'status': 'success',
            'invoice_id': invoice.id,
            'subscription_id': subscription_id,
            'period': period
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Kanizsa Billing Service',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'process_payment': '/payment/process',
            'create_subscription': '/subscriptions/create',
            'generate_invoice': '/invoices/generate'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
