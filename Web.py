#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
AQUAZAR - Water Booking & Delivery System
A futuristic, cyber-space themed, single-file Flask Application built to 
replicate the exact "QUAZAR" aesthetic, adapted for a water delivery business.
================================================================================
"""

import sqlite3
import json
import os
import datetime
from flask import Flask, render_template_string, request, jsonify

# ==============================================================================
# 1. APPLICATION SETUP & CONFIGURATION
# ==============================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aquazar_cyber_water_2026'
DATABASE = 'aquazar.db'

# ==============================================================================
# 2. DATABASE LAYER (SQLITE HELPER FUNCTIONS)
# ==============================================================================
def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema for the Water Delivery System."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop tables for clean seeding (safe for demonstration)
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS subscriptions")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS users")

    # Table: Users (Registered customers)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table: Orders (Water delivery bookings)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            can_size TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            delivery_date TEXT NOT NULL,
            delivery_time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'Processing',
            total_price REAL NOT NULL,
            ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Table: Subscriptions (Smart IoT Refills)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            can_size TEXT NOT NULL,
            frequency_days INTEGER NOT NULL,
            quantity_per_delivery INTEGER NOT NULL,
            next_delivery_date TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Table: Contact Messages (Feedback/Inquiries)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[INFO] Database schema initialized successfully.")

def seed_db():
    """Seed the database with rich dummy data to make the app instantly usable."""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("[INFO] Seeding database with futuristic water delivery data...")
    
    # 1. Seed Users (3 Users)
    users_data = [
        ('Alex Mercer', 'alex@cybermail.com', '+1-555-0101', 'Neo City, District 7, Starlight Tower Apt 404'),
        ('Sarah Vance', 'sarah@waternet.com', '+1-555-0202', 'Eco-Sector, Liquid Avenue, Block B'),
        ('Dr. Aris Thorne', 'aris@purelab.org', '+1-555-0303', 'Research Dome 9, Hydra Campus')
    ]
    cursor.executemany('INSERT INTO users (name, email, phone, address) VALUES (?, ?, ?, ?)', users_data)
    
    # 2. Seed Orders (Mock active orders)
    orders_data = [
        (1, '20L Premium RO', 3, '2026-08-21', 'Morning (8am-12pm)', 'Dispatched', 18.00),
        (2, '15L Dispenser', 2, '2026-08-22', 'Afternoon (12pm-4pm)', 'Processing', 10.00),
        (3, '5L Pet Bottle', 10, '2026-08-20', 'Evening (4pm-8pm)', 'Delivered', 15.00),
        (1, '20L Premium RO', 5, '2026-08-23', 'Morning (8am-12pm)', 'Processing', 30.00)
    ]
    cursor.executemany('INSERT INTO orders (user_id, can_size, quantity, delivery_date, delivery_time_slot, status, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)', orders_data)
    
    # 3. Seed Subscriptions (Smart IoT Refills)
    subs_data = [
        (2, '20L Premium RO', 7, 4, '2026-08-28', 1),
        (3, '15L Dispenser', 3, 6, '2026-08-24', 1)
    ]
    cursor.executemany('INSERT INTO subscriptions (user_id, can_size, frequency_days, quantity_per_delivery, next_delivery_date, active) VALUES (?, ?, ?, ?, ?, ?)', subs_data)
    
    conn.commit()
    conn.close()
    print("[INFO] Database seeding completed successfully.")

def get_recent_orders():
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT orders.*, users.name as user_name 
        FROM orders 
        JOIN users ON orders.user_id = users.id 
        ORDER BY ordered_at DESC LIMIT 5
    ''').fetchall()
    conn.close()
    return [dict(o) for o in orders]

# ==============================================================================
# 3. MASSIVE HTML TEMPLATE STRING (INCLUDING CSS & JS)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AQUAZAR | Futuristic Pure Water Delivery</title>
    <style>
        /* ====================================================================
               CSS RESET & GLOBAL STYLES
               ==================================================================== */
        *,
        *::before,
        *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: #0b0e1a;
            color: #f0f4ff;
            line-height: 1.6;
            overflow-x: hidden;
            /* Deep space-blue gradient with a glowing water-vortex effect */
            background-image: 
                radial-gradient(circle at 50% 30%, rgba(0, 191, 255, 0.15) 0%, transparent 60%),
                radial-gradient(circle at 50% 50%, rgba(0, 100, 200, 0.3) 0%, #0b0e1a 80%),
                radial-gradient(circle at 30% 80%, rgba(0, 50, 150, 0.4) 0%, transparent 50%),
                linear-gradient(180deg, #0d111f 0%, #070a13 100%);
            background-attachment: fixed;
            background-size: cover;
            min-height: 100vh;
        }

        /* Starry overlay generated via CSS box-shadows */
        .stars-layer {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .stars-layer::after {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background-image: 
                radial-gradient(2px 2px at 20px 30px, #eee, transparent),
                radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
                radial-gradient(2px 2px at 50px 160px, #ddd, transparent),
                radial-gradient(2px 2px at 90px 40px, rgba(255,255,255,0.6), transparent),
                radial-gradient(2px 2px at 130px 80px, #fff, transparent),
                radial-gradient(2px 2px at 160px 30px, rgba(255,255,255,0.7), transparent);
            background-size: 200px 200px;
            animation: starDrift 60s linear infinite;
            opacity: 0.6;
        }

        @keyframes starDrift {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-50px, -50px); }
        }

        a { text-decoration: none; color: inherit; }
        ul { list-style: none; }
        img { max-width: 100%; display: block; }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            position: relative;
            z-index: 1;
        }

        /* ====================================================================
               TYPOGRAPHY & SPECIAL EFFECTS
               ==================================================================== */
        h1, h2, h3, h4 {
            font-weight: 700;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(0, 191, 255, 0.3);
        }

        .glow-text {
            color: #ffffff;
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.8), 0 0 20px rgba(0, 191, 255, 0.4), 0 0 40px rgba(0, 191, 255, 0.2);
        }

        .cyan-text {
            color: #00bfff;
        }

        .section-title {
            text-align: center;
            margin-bottom: 50px;
        }

        .section-title h2 {
            font-size: 32px;
            text-transform: uppercase;
            border-bottom: 2px solid rgba(0, 191, 255, 0.3);
            display: inline-block;
            padding-bottom: 10px;
        }

        /* ====================================================================
               BUTTONS & INTERACTIVE ELEMENTS
               ==================================================================== */
        .btn-cyber {
            display: inline-block;
            padding: 15px 40px;
            background: transparent;
            border: 2px solid #00bfff;
            color: #00bfff;
            text-transform: uppercase;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 2px;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 191, 255, 0.2);
            border-radius: 30px;
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
        }

        .btn-cyber:hover {
            background: #00bfff;
            color: #0b0e1a;
            box-shadow: 0 0 40px rgba(0, 191, 255, 0.6);
            transform: scale(1.05);
        }

        .btn-cyber::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 191, 255, 0.1), transparent);
            transform: rotate(45deg);
            transition: 0.5s;
        }
        .btn-cyber:hover::before {
            left: 100%;
        }

        /* Pulsing Animation for main button */
        .pulse-btn {
            animation: pulseNeon 2s infinite;
        }

        @keyframes pulseNeon {
            0% { box-shadow: 0 0 10px rgba(0, 191, 255, 0.3); }
            50% { box-shadow: 0 0 30px rgba(0, 191, 255, 0.8), 0 0 60px rgba(0, 191, 255, 0.4); }
            100% { box-shadow: 0 0 10px rgba(0, 191, 255, 0.3); }
        }

        /* ====================================================================
               HEADER & TOP NAVIGATION (Ribbon Style)
               ==================================================================== */
        header {
            padding: 20px 0;
            position: relative;
            background: rgba(11, 14, 26, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 191, 255, 0.2);
            z-index: 10;
        }

        .header-inner {
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }

        /* Metallic Shield Logo Area */
        .logo-container {
            position: relative;
            padding: 10px 30px;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #1a1a2e);
            border: 2px solid #00bfff;
            transform: perspective(500px) rotateX(10deg);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(0, 191, 255, 0.2);
            border-radius: 0 0 20px 20px;
            text-align: center;
            margin-top: -10px;
        }

        .logo-container h1 {
            font-size: 32px;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 0 0 15px rgba(0, 191, 255, 0.6);
            letter-spacing: 4px;
        }
        .logo-container span {
            color: #00bfff;
        }
        .logo-container small {
            display: block;
            font-size: 10px;
            color: #88ccff;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: -5px;
        }

        /* ====================================================================
               TOP ICON MENU (6 High-Tech Glowing Circular Icons)
               ==================================================================== */
        .top-icons {
            padding: 30px 0 10px;
        }
        .top-icons ul {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }
        .top-icons ul li {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            transition: 0.3s;
        }
        .top-icons ul li:hover {
            transform: translateY(-5px);
        }
        .icon-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 191, 255, 0.2), rgba(11, 14, 26, 0.8));
            border: 2px solid #00bfff;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(0, 191, 255, 0.2);
            transition: 0.3s;
        }
        .top-icons ul li:hover .icon-circle {
            box-shadow: 0 0 40px rgba(0, 191, 255, 0.6);
            background: rgba(0, 191, 255, 0.15);
        }
        .icon-circle svg {
            width: 28px;
            height: 28px;
            fill: #00bfff;
        }
        .top-icons ul li span {
            font-size: 12px;
            text-transform: uppercase;
            color: #88ccff;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        /* ====================================================================
               HERO & MAIN CTA SECTION
               ==================================================================== */
        .hero {
            padding: 60px 0 40px;
            text-align: center;
        }

        .hero h2 {
            font-size: 48px;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .hero .sub-text {
            font-size: 18px;
            color: #88ccff;
            letter-spacing: 4px;
            margin-bottom: 40px;
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.2);
        }

        .hero .sub-text span {
            font-weight: 700;
            color: #ffffff;
        }

        /* Central Water Vortex CSS Effect */
        .vortex-container {
            width: 300px;
            height: 300px;
            margin: 30px auto 40px;
            position: relative;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 191, 255, 0.2), transparent 70%);
            animation: spinVortex 20s linear infinite;
        }

        @keyframes spinVortex {
            0% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(180deg) scale(1.05); }
            100% { transform: rotate(360deg) scale(1); }
        }

        .vortex-container::before {
            content: '';
            position: absolute;
            top: 10%;
            left: 10%;
            width: 80%;
            height: 80%;
            border-radius: 50%;
            border: 2px dashed rgba(0, 191, 255, 0.3);
            animation: spinVortex 15s linear infinite reverse;
        }
        .vortex-container::after {
            content: '';
            position: absolute;
            top: 25%;
            left: 25%;
            width: 50%;
            height: 50%;
            border-radius: 50%;
            border: 1px solid rgba(0, 191, 255, 0.5);
            background: radial-gradient(circle, rgba(0, 191, 255, 0.4), transparent);
            filter: blur(5px);
        }

        /* ====================================================================
               LOWER 4 FEATURE PILLARS (Water Drop, Purity, Delivery, Tracker)
               ==================================================================== */
        .features-4 {
            padding: 60px 0 80px;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 30px;
        }

        .feature-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 191, 255, 0.1);
            padding: 30px 20px;
            text-align: center;
            border-radius: 15px;
            backdrop-filter: blur(5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: 0.4s;
        }

        .feature-box:hover {
            border-color: #00bfff;
            transform: translateY(-10px);
            box-shadow: 0 10px 40px rgba(0, 191, 255, 0.15);
        }

        .feature-box .f-icon {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 191, 255, 0.2), transparent);
            border: 2px solid #00bfff;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 0 20px rgba(0, 191, 255, 0.2);
        }

        .feature-box .f-icon svg {
            width: 35px;
            height: 35px;
            fill: #00bfff;
        }

        .feature-box h4 {
            font-size: 18px;
            margin-bottom: 10px;
            color: #ffffff;
        }

        .feature-box p {
            font-size: 14px;
            color: #88aaff;
            line-height: 1.7;
            margin-bottom: 15px;
        }

        .feature-box .link-arrow {
            font-size: 12px;
            color: #00bfff;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 1px;
            cursor: pointer;
        }
        .feature-box .link-arrow:hover {
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
        }

        /* ====================================================================
               MODAL FOR WATER ORDERING (The Central CTA)
               ==================================================================== */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(11, 14, 26, 0.9);
            backdrop-filter: blur(8px);
            z-index: 9999;
            justify-content: center;
            align-items: center;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-content {
            background: linear-gradient(135deg, #141b33, #0b0e1a);
            border: 2px solid #00bfff;
            border-radius: 20px;
            padding: 40px;
            max-width: 550px;
            width: 90%;
            box-shadow: 0 0 60px rgba(0, 191, 255, 0.2);
            position: relative;
            animation: slideUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        @keyframes slideUp {
            from { transform: translateY(100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal-close {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 28px;
            color: #88ccff;
            cursor: pointer;
            transition: 0.3s;
        }
        .modal-close:hover {
            color: #00bfff;
            transform: rotate(90deg);
        }

        .modal-content h2 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .modal-content .form-group {
            margin-bottom: 20px;
        }
        .modal-content label {
            display: block;
            color: #88ccff;
            font-size: 14px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .modal-content select, .modal-content input {
            width: 100%;
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 191, 255, 0.3);
            color: #ffffff;
            border-radius: 8px;
            outline: none;
            font-size: 16px;
        }
        .modal-content select:focus, .modal-content input:focus {
            border-color: #00bfff;
            box-shadow: 0 0 15px rgba(0, 191, 255, 0.2);
        }
        .modal-content select option {
            background: #141b33;
        }

        .modal-content .btn-submit {
            width: 100%;
            padding: 15px;
            background: transparent;
            border: 2px solid #00bfff;
            color: #00bfff;
            font-weight: 700;
            font-size: 18px;
            border-radius: 30px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 20px rgba(0, 191, 255, 0.2);
        }
        .modal-content .btn-submit:hover {
            background: #00bfff;
            color: #0b0e1a;
            box-shadow: 0 0 40px rgba(0, 191, 255, 0.6);
        }

        .order-msg {
            display: none;
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
            font-weight: 600;
        }
        .order-msg.success { color: #00ffcc; display: block; }
        .order-msg.error { color: #ff4466; display: block; }

        /* ====================================================================
               PRICE CALCULATOR WIDGET (Embedded in layout)
               ==================================================================== */
        .calculator-widget {
            padding: 40px 0;
            background: rgba(255, 255, 255, 0.02);
            border-top: 1px solid rgba(0, 191, 255, 0.1);
            border-bottom: 1px solid rgba(0, 191, 255, 0.1);
        }
        .calc-inner {
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
        }
        .calc-inner h3 { margin-bottom: 20px; font-size: 24px; }
        .calc-row {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .calc-row input {
            padding: 10px 15px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(0,191,255,0.3);
            color: #fff;
            border-radius: 8px;
            width: 120px;
            text-align: center;
            outline: none;
        }
        .calc-row input:focus { border-color: #00bfff; }
        .calc-result {
            font-size: 28px;
            font-weight: 700;
            color: #00bfff;
            text-shadow: 0 0 20px rgba(0, 191, 255, 0.4);
            margin-top: 10px;
        }

        /* ====================================================================
               FOOTER & CONTACT FORM
               ==================================================================== */
        footer {
            padding: 60px 0 30px;
            background: rgba(0, 0, 0, 0.4);
            border-top: 1px solid rgba(0, 191, 255, 0.1);
        }

        footer .container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 50px;
        }

        footer h4 {
            color: #00bfff;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        footer p, footer li {
            color: #88aaff;
            font-size: 14px;
            margin-bottom: 10px;
        }
        footer li a:hover { color: #00bfff; }

        .contact-cyber input, .contact-cyber textarea {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(0,191,255,0.2);
            border-radius: 8px;
            color: #fff;
            outline: none;
        }
        .contact-cyber input:focus, .contact-cyber textarea:focus {
            border-color: #00bfff;
        }
        .contact-cyber button {
            padding: 12px 30px;
            background: transparent;
            border: 2px solid #00bfff;
            color: #00bfff;
            border-radius: 30px;
            font-weight: 700;
            cursor: pointer;
            text-transform: uppercase;
        }
        .contact-cyber button:hover {
            background: #00bfff;
            color: #0b0e1a;
        }

        .contact-msg-footer {
            display: none;
            margin-top: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        .contact-msg-footer.success { color: #00ffcc; display: block; }
        .contact-msg-footer.error { color: #ff4466; display: block; }

        .copyright {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            font-size: 12px;
            color: #556688;
        }

        /* ====================================================================
               RESPONSIVE MEDIA QUERIES
               ==================================================================== */
        @media screen and (max-width: 992px) {
            .features-grid { grid-template-columns: repeat(2, 1fr); }
            footer .container { grid-template-columns: 1fr; }
        }

        @media screen and (max-width: 768px) {
            .hero h2 { font-size: 32px; }
            .hero .sub-text { font-size: 14px; letter-spacing: 2px; }
            .top-icons ul { gap: 15px; }
            .icon-circle { width: 50px; height: 50px; }
            .icon-circle svg { width: 22px; height: 22px; }
            .top-icons ul li span { font-size: 10px; }
            .logo-container { padding: 10px 15px; }
            .logo-container h1 { font-size: 24px; }
            .features-grid { grid-template-columns: 1fr; }
            .modal-content { padding: 25px; }
        }

        @media screen and (max-width: 480px) {
            .hero h2 { font-size: 24px; }
            .btn-cyber { padding: 12px 25px; font-size: 14px; }
        }
    </style>
</head>
<body>

    <!-- CSS Starry Layer -->
    <div class="stars-layer"></div>

    <!-- ================================================================
    HEADER & LOGO RIBBON
    ================================================================ -->
    <header>
        <div class="container header-inner">
            <div class="logo-container">
                <h1>QUA<span>ZAR</span></h1>
                <small>Water Delivery Systems</small>
            </div>
        </div>
    </header>

    <!-- ================================================================
    TOP ICON MENU
    ================================================================ -->
    <section class="top-icons">
        <div class="container">
            <ul>
                <li onclick="openOrderModal()">
                    <div class="icon-circle">
                        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                    </div>
                    <span>Order Water</span>
                </li>
                <li onclick="alert('My Bookings module is live. Check console for DB logs.')">
                    <div class="icon-circle">
                        <svg viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>
                    </div>
                    <span>My Bookings</span>
                </li>
                <li onclick="alert('Live Tracker currently updating via satellite.')">
                    <div class="icon-circle">
                        <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                    </div>
                    <span>Tracking</span>
                </li>
                <li onclick="alert('Purity Report: 7-Stage RO + UV Filtration active.')">
                    <div class="icon-circle">
                        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/></svg>
                    </div>
                    <span>Purity Report</span>
                </li>
                <li onclick="document.getElementById('footerContact').scrollIntoView();">
                    <div class="icon-circle">
                        <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
                    </div>
                    <span>Get In Touch</span>
                </li>
                <li onclick="document.getElementById('calcWidget').scrollIntoView();">
                    <div class="icon-circle">
                        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/></svg>
                    </div>
                    <span>Price Calc</span>
                </li>
            </ul>
        </div>
    </section>

    <!-- ================================================================
    HERO SECTION
    ================================================================ -->
    <section class="hero">
        <div class="container">
            <h2 class="glow-text">PURE WATER <span class="cyan-text">DELIVERY</span></h2>
            <div class="sub-text">& Mobile Solutions for <span>Healthy Travelers</span></div>
            
            <div class="vortex-container"></div>
            
            <button class="btn-cyber pulse-btn" onclick="openOrderModal()">LAUNCH WATER ORDER</button>
        </div>
    </section>

    <!-- ================================================================
    LOWER 4 FEATURE PILLARS
    ================================================================ -->
    <section class="features-4">
        <div class="container">
            <div class="features-grid">
                <!-- Feature 1: Premium Water Quality -->
                <div class="feature-box">
                    <div class="f-icon">
                        <svg viewBox="0 0 24 24"><path d="M12 22c4.97 0 9-4.03 9-9 0-4.97-9-13-9-13S3 8.03 3 13c0 4.97 4.03 9 9 9zm0-3c-3.31 0-6-2.69-6-6 0-1.09.26-2.14.74-3.08L12 4.59l5.26 5.33c.48.94.74 1.99.74 3.08 0 3.31-2.69 6-6 6z"/></svg>
                    </div>
                    <h4>Premium Water Quality</h4>
                    <p>Our state-of-the-art 7-stage RO + UV purification system ensures 99.9% purity. We remove all heavy metals, bacteria, and contaminants, delivering crisp, clean, and mineral-rich hydration directly to your doorstep.</p>
                    <span class="link-arrow">View Purity Report &rarr;</span>
                </div>

                <!-- Feature 2: Smart IoT Refills -->
                <div class="feature-box">
                    <div class="f-icon">
                        <svg viewBox="0 0 24 24"><path d="M17 4h-2V2h-6v2H7c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM7 6h10v2H7V6zm0 4h10v2H7v-2zm0 4h10v2H7v-2z"/></svg>
                    </div>
                    <h4>Smart IoT Refills</h4>
                    <p>Never run out of water again. Our intelligent IoT sensors on your dispensers automatically detect when you're running low and place a recurring subscription order. Fully customizable delivery frequencies tailored to your consumption.</p>
                    <span class="link-arrow">Setup Auto-Refill &rarr;</span>
                </div>

                <!-- Feature 3: Express Network Delivery -->
                <div class="feature-box">
                    <div class="f-icon">
                        <svg viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm12 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-4H6V6h11.5l3.5 4.5V14H17z"/></svg>
                    </div>
                    <h4>Express Network Delivery</h4>
                    <p>Powered by our local cyber-fleet network, we guarantee delivery within 2 hours for urgent requests. Real-time GPS tracking provides complete transparency, allowing you to monitor your water shipment from our hub to your location.</p>
                    <span class="link-arrow">Track Live Orders &rarr;</span>
                </div>

                <!-- Feature 4: Hydration Tracker -->
                <div class="feature-box">
                    <div class="f-icon">
                        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
                    </div>
                    <h4>Interactive Hydration Tracker</h4>
                    <p>Maintain optimal health with our interactive dashboard. Simply input your weight and activity level, and our AI algorithm calculates your daily water intake needs, sending smart reminders to keep you perfectly hydrated.</p>
                    <span class="link-arrow">Start Health Tracker &rarr;</span>
                </div>
            </div>
        </div>
    </section>

    <!-- ================================================================
    PRICE CALCULATOR WIDGET
    ================================================================ -->
    <section class="calculator-widget" id="calcWidget">
        <div class="container calc-inner">
            <h3><span class="cyan-text">Bulk Price</span> Calculator</h3>
            <div class="calc-row">
                <div>
                    <label style="color:#88ccff; font-size:14px;">Cans (20L)</label>
                    <input type="number" id="calcQty" value="1" min="1" max="100" oninput="calculatePrice()">
                </div>
                <div>
                    <label style="color:#88ccff; font-size:14px;">Distance (km)</label>
                    <input type="number" id="calcDist" value="5" min="0" max="50" oninput="calculatePrice()">
                </div>
            </div>
            <div class="calc-result" id="calcResult">$ 6.00</div>
            <p style="font-size:12px; color:#556688; margin-top:5px;">*Base price $2.00 per can + $0.40/km delivery fee.</p>
        </div>
    </section>

    <!-- ================================================================
    ORDER MODAL (The Central CTA)
    ================================================================ -->
    <div class="modal-overlay" id="orderModal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeOrderModal()">&times;</span>
            <h2>Launch <span class="cyan-text">Order</span></h2>
            <form id="orderForm">
                <div class="form-group">
                    <label>Water Can Size</label>
                    <select name="can_size" id="canSize">
                        <option value="20L Premium RO">20L Premium RO</option>
                        <option value="15L Dispenser">15L Dispenser</option>
                        <option value="5L Pet Bottle">5L Pet Bottle</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Quantity (Cans)</label>
                    <input type="number" name="quantity" value="2" min="1" max="50">
                </div>
                <div class="form-group">
                    <label>Delivery Date</label>
                    <input type="date" id="deliveryDate" name="delivery_date">
                </div>
                <div class="form-group">
                    <label>Delivery Time Slot</label>
                    <select name="time_slot">
                        <option value="Morning (8am-12pm)">Morning (8am-12pm)</option>
                        <option value="Afternoon (12pm-4pm)">Afternoon (12pm-4pm)</option>
                        <option value="Evening (4pm-8pm)">Evening (4pm-8pm)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Your Email (for confirmation)</label>
                    <input type="email" name="email" placeholder="your@email.com" required>
                </div>
                <button type="submit" class="btn-submit">Confirm Launch</button>
                <div id="orderMsgSuccess" class="order-msg success">Order successfully transmitted! Check your email for tracking details.</div>
                <div id="orderMsgError" class="order-msg error">Transmission failed. Please check your network and try again.</div>
            </form>
        </div>
    </div>

    <!-- ================================================================
    FOOTER & CONTACT FORM
    ================================================================ -->
    <footer id="footerContact">
        <div class="container">
            <div class="contact-cyber">
                <h4>Establish <span class="cyan-text">Connection</span></h4>
                <form id="contactFormFooter">
                    <input type="text" name="name" placeholder="Your Name" required>
                    <input type="email" name="email" placeholder="Your Email" required>
                    <input type="text" name="subject" placeholder="Subject" required>
                    <textarea name="message" rows="4" placeholder="Your Inquiry..." required></textarea>
                    <button type="submit">Transmit Message</button>
                    <div id="contactMsgSuccess" class="contact-msg-footer success">Message transmitted successfully! Our team will respond shortly.</div>
                    <div id="contactMsgError" class="contact-msg-footer error">Failed to transmit message. Please try again.</div>
                </form>
            </div>
            <div>
                <h4>Quick Links</h4>
                <ul>
                    <li><a href="#" onclick="openOrderModal()">Launch Order</a></li>
                    <li><a href="#">IoT Subscriptions</a></li>
                    <li><a href="#">Delivery Tracking</a></li>
                    <li><a href="#">Purity Laboratory</a></li>
                    <li><a href="#">Support Center</a></li>
                </ul>
                <h4 style="margin-top:20px;">Cyber Hub</h4>
                <ul>
                    <li>Neo City, Sector 7, Starlight Tower</li>
                    <li>Support: +1 (555) 789-1011</li>
                    <li>Email: command@aquazar.com</li>
                </ul>
            </div>
        </div>
        <div class="copyright">
            &copy; 2026 AQUAZAR Water Delivery Systems. Deep Space Hydration Solutions.
        </div>
    </footer>

    <!-- ================================================================
    JAVASCRIPT LOGIC (MODALS, CALCULATOR, AJAX)
    ================================================================ -->
    <script>
        (function() {
            "use strict";

            // -----------------------------------------------------------------
            // 1. DATE DEFAULT FOR MODAL
            // -----------------------------------------------------------------
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('deliveryDate').setAttribute('min', today);
            document.getElementById('deliveryDate').value = today;

            // -----------------------------------------------------------------
            // 2. MODAL CONTROLS
            // -----------------------------------------------------------------
            window.openOrderModal = function() {
                document.getElementById('orderModal').classList.add('active');
                document.body.style.overflow = 'hidden';
            };

            window.closeOrderModal = function() {
                document.getElementById('orderModal').classList.remove('active');
                document.body.style.overflow = 'auto';
            };

            document.getElementById('orderModal').addEventListener('click', function(e) {
                if (e.target === this) closeOrderModal();
            });

            // -----------------------------------------------------------------
            // 3. PRICE CALCULATOR
            // -----------------------------------------------------------------
            window.calculatePrice = function() {
                const qty = parseInt(document.getElementById('calcQty').value) || 0;
                const dist = parseInt(document.getElementById('calcDist').value) || 0;
                const basePrice = 2.00; // per can
                const deliveryRate = 0.40; // per km
                
                const total = (qty * basePrice) + (dist * deliveryRate);
                document.getElementById('calcResult').textContent = '$ ' + total.toFixed(2);
            };

            // -----------------------------------------------------------------
            // 4. ORDER FORM AJAX SUBMISSION
            // -----------------------------------------------------------------
            document.getElementById('orderForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const successMsg = document.getElementById('orderMsgSuccess');
                const errorMsg = document.getElementById('orderMsgError');

                successMsg.className = 'order-msg';
                errorMsg.className = 'order-msg';
                successMsg.style.display = 'none';
                errorMsg.style.display = 'none';

                fetch('/api/order', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        successMsg.style.display = 'block';
                        successMsg.className = 'order-msg success';
                        document.getElementById('orderForm').reset();
                        document.getElementById('deliveryDate').value = today;
                        setTimeout(() => {
                            closeOrderModal();
                            successMsg.style.display = 'none';
                        }, 3000);
                    } else {
                        errorMsg.style.display = 'block';
                        errorMsg.className = 'order-msg error';
                    }
                })
                .catch(err => {
                    console.error(err);
                    errorMsg.style.display = 'block';
                    errorMsg.className = 'order-msg error';
                });
            });

            // -----------------------------------------------------------------
            // 5. CONTACT FOOTER FORM AJAX SUBMISSION
            // -----------------------------------------------------------------
            document.getElementById('contactFormFooter').addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const successMsg = document.getElementById('contactMsgSuccess');
                const errorMsg = document.getElementById('contactMsgError');

                successMsg.className = 'contact-msg-footer';
                errorMsg.className = 'contact-msg-footer';
                successMsg.style.display = 'none';
                errorMsg.style.display = 'none';

                fetch('/api/contact', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        successMsg.style.display = 'block';
                        successMsg.className = 'contact-msg-footer success';
                        document.getElementById('contactFormFooter').reset();
                        setTimeout(() => {
                            successMsg.style.display = 'none';
                        }, 5000);
                    } else {
                        errorMsg.style.display = 'block';
                        errorMsg.className = 'contact-msg-footer error';
                    }
                })
                .catch(err => {
                    console.error(err);
                    errorMsg.style.display = 'block';
                    errorMsg.className = 'contact-msg-footer error';
                });
            });

        })();
    </script>
</body>
</html>
"""

# ==============================================================================
# 4. ROUTES & CONTROLLERS
# ==============================================================================
@app.route('/')
def index():
    """Render the main futuristic water delivery homepage."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/order', methods=['POST'])
def create_order():
    """Handle the AJAX water order submission."""
    email = request.form.get('email')
    can_size = request.form.get('can_size')
    quantity = request.form.get('quantity')
    delivery_date = request.form.get('delivery_date')
    time_slot = request.form.get('time_slot')

    if not all([email, can_size, quantity, delivery_date, time_slot]):
        return jsonify({'success': False, 'message': 'All fields are required.'})
    
    try:
        quantity = int(quantity)
        if quantity < 1: raise ValueError
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity.'})

    conn = get_db_connection()
    try:
        # Simple user lookup/creation for the demo
        user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if not user:
            conn.execute('INSERT INTO users (name, email, phone, address) VALUES (?, ?, ?, ?)', 
                          ('Cyber Customer', email, 'N/A', 'Local Network Address'))
            conn.commit()
            user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        
        user_id = user['id']
        total_price = (quantity * 2.00) # base price without distance for demo
        
        conn.execute('''
            INSERT INTO orders (user_id, can_size, quantity, delivery_date, delivery_time_slot, total_price) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, can_size, quantity, delivery_date, time_slot, total_price))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Order placed successfully!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle the AJAX footer contact form submission."""
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    if not all([name, email, subject, message]):
        return jsonify({'success': False, 'message': 'All fields are required.'})

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO messages (name, email, subject, message) VALUES (?, ?, ?, ?)', 
                     (name, email, subject, message))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Message sent!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

# ==============================================================================
# 5. MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("           AQUAZAR - Water Delivery & Booking System")
    print("                Cyber-Space Themed Web App")
    print("=" * 60)
    
    # Initialize and seed database if not exists
    if not os.path.exists(DATABASE):
        print("[INFO] Database not found. Initializing and seeding...")
        init_db()
        seed_db()
    else:
        try:
            conn = sqlite3.connect(DATABASE)
            conn.execute('SELECT 1 FROM orders LIMIT 1')
            conn.close()
        except sqlite3.OperationalError:
            print("[WARNING] Database schema outdated. Recreating...")
            os.remove(DATABASE)
            init_db()
            seed_db()
            
    print("[INFO] Starting Flask development server...")
    print("[INFO] Access the system at: http://127.0.0.1:5000")
    print("[INFO] Press CTRL+C to stop the server.")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
