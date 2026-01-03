# 🚢 Naval WAF Anomaly Detection System

A **Dockerized, Streamlit-based security dashboard** that simulates real-time web traffic interception and anomaly detection for a Naval Web Application Firewall (WAF).  
The project focuses on **operator-friendly visualization**, rule-based threat detection, and production-style deployment.

---

## 🔍 Project Overview

This system simulates how a Naval security operations team can monitor intercepted web traffic, detect suspicious activities, and analyze threats through a centralized command center dashboard.

The project is designed as a **working prototype**, prioritizing clarity, performance, and deployability rather than heavy machine learning complexity.

---

## ✨ Key Features

- 📡 **Traffic Interception Simulation**  
  Generates synthetic web traffic events for analysis.

- 🛡️ **Rule-Based Anomaly Detection**  
  Detects common attack patterns such as suspicious IPs, abnormal request rates, and injection-like behavior.

- 📊 **Interactive Dashboard**  
  Displays interceptions, threat severity, and insights using Streamlit.

- 🐳 **Dockerized Application**  
  Entire system runs inside a Docker container for consistent execution.

- 🤖 **CI/CD Ready Structure**  
  Organized to support automated pipelines using GitHub Actions.

---

## 🏗️ Tech Stack

- **Programming Language:** Python 3.10  
- **Dashboard Framework:** Streamlit  
- **Data & Visualization:** Pandas, Plotly  
- **Containerization:** Docker  
- **Version Control:** Git & GitHub  
- **CI/CD:** GitHub Actions

## 📂 Project Structure
naval-waf-anomaly-detection/
│
├── dashboard/ # Streamlit dashboard
├── simulator/ # Traffic simulation logic
├── rules/ # Rule-based detection engine
├── ml/ # Simulated ML layer (conceptual)
├── data/ # Sample datasets
├── Dockerfile
├── requirements.txt
├── README.md
└── .github/workflows # CI/CD pipeline


