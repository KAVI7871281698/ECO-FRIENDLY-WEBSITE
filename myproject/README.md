# 🌿 Verdana — Eco-Friendly E-commerce & Sustainability Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-3.2+-forest.svg)](https://www.djangoproject.com/)

**Verdana** is a premium sustainability platform designed to empower users to live a greener, more eco-conscious lifestyle. It combines a high-end e-commerce experience with interactive tools for carbon footprint tracking and waste management.

---

## 🎨 Visual Identity

![Verdana Project Mockup](docs/images/hero.png)
*Modern, minimalist, and nature-inspired UI/UX.*

---

## 🚀 Key Features

### 🛒 1. Sustainable Marketplace
A curated collection of eco-certified products, including cold-pressed oils, botanical serums, and plastic-free bamboo essentials. 
- **Detailed Order Tracking:** Users can view detailed breakdowns of their orders and individual product specs.
- **Premium Checkout:** Seamless integration with **Razorpay** for secure payments.

### ♻️ 2. Smart Recycling Program
- **Pickup Requests:** Users can schedule recycling pickups for plastic, paper, metal, and electronic waste directly to their doorstep.
- **Admin Logistics:** A dedicated dashboard for admins to manage pickup statuses (Pending, Assigned, Completed).

### 📉 3. Carbon Calculator
An interactive tool that calculates the user's carbon footprint based on transport, electricity, and plastic usage, providing actionable suggestions to reduce environmental impact.

### 🤖 4. AI-Powered Assistant
A smart, context-aware chatbot ("Verdana Brain") that helps users:
- Track order statuses.
- Explore product ecological impacts.
- Receive personalized sustainability advice.

---

## 📊 Administrative Management

![Admin Dashboard Preview](docs/images/admin.png)
*Elegant and feature-rich management interface.*

- **Inventory Control:** Add, update, and manage product listings with thumbnail support and categorization.
- **Real-time Stats:** Track total revenue, order volume, and user growth at a glance.
- **Detailed Order Review:** Interactive table allowing admins to inspect full order details and customer shipping info.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Django (Python) |
| **Database** | SQLite3 (Development / Production) |
| **Styling** | Vanilla CSS (Glassmorphism & Modern UI) |
| **Frontend** | Django Templates & Vanilla JavaScript |
| **AI Integration** | Gemini API / Google Generative AI |
| **Payment Gateway** | Razorpay Integration |

---

## 🌲 Features at a Glance

![Features Showcase](docs/images/features.png)

- **User Authentication:** Secure sign-in/sign-up with profile image management.
- **Responsive Design:** Optimized for Desktop, Tablet, and Mobile.
- **Impact Tracking:** Every purchase and pickup is tracked to visualize the user's positive impact on the planet.

---

## 📁 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/eco-friendly-verdana.git
   cd eco-friendly-verdana
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings:**
   - Update `settings.py` with your **Razorpay Key ID/Secret** and **Gemini API Key**.

4. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

---

## 📜 Contributing
We welcome contributions that help push the mission of sustainability forward! Please fork this repository and submit a pull request with your enhancements.

---

## ✉️ Contact & Support
If you have questions, feedback, or want to partner with **Verdana**, please reach out to our team via the [Contact Page](#).

**Verdana: Vote for a Greener Future. 🌍**
