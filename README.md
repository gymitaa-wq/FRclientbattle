# Project CAII - The AI-Proof Financial Advisor Simulator

**Northwestern Mutual AI-Proof Sales Strategy Simulator**

A Python-based multi-agent simulation framework that tests how human financial advisors compete against Artificial Intelligence. This "Virtual Proving Ground" simulates thousands of sales interactions to uncover which human strategies successfully persuade clients who are using AI tools (like ChatGPT) to scrutinize their advice.

## 🎯 Core Concept

Every simulation runs a complete story between three characters:
1.  **The Client Agent:** A virtual person with a unique personality, bank account, family situation, and level of skepticism.
2.  **The Digital Twin (The Rival):** The client's personal AI assistant. Before ever meeting a human, the client asks this AI for "free, unbiased financial advice" (which usually favors cheap, DIY solutions).
3.  **The Human Advisor Agent:** A professional advisor who must analyze the client's needs and present a premium, holistic financial plan (Life Insurance, Disability, Annuities) that justifies the cost over the AI's cheap alternatives.

## 📋 Interaction Workflow

1.  **The Dig**: The system builds a deep psychological profile of the client.
2.  **The Pre-Consultation**: The client consults their AI to get a "baseline" opinion.
3.  **The Pitch**: The Human Advisor presents a comprehensive, professional proposal.
4.  **The Fact Check**: The client "uploads" the advisor's proposal to their AI for a second opinion.
5.  **The Showdown**: The client weighs the Advisor's expertise against the AI's data.
6.  **The Verdict**: The client makes a final decision (Convert or Reject) and provides specific reasons.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/gymitaa-wq/FRclientbattle.git
cd FRclientbattle

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory (copy `.env.template`):

```bash
GOOGLE_API_KEY="your-gemini-api-key"
```

### Run the App

```bash
streamlit run streamlit_streamlined.py
```

Open your browser to `http://localhost:8501`.

## 🤖 Features

-   **Automatic Batch Simulator**: Run hundreds of simulations in a loop to gather statistical data ("War Room" mode).
-   **Persistent History**: All results are saved to a local database (`simulation_data.db`) or PostgreSQL (if configured).
-   **Live Analytics**: Dashboard showing Win Rate, Friction Scores, and Winning Factors.
-   **Smart Model Fallback**: Automatically switches between Gemini models (Flash, Pro, 8b) if rate limits are hit.
-   **Resilient Intelligence**: If quotas are exhausted, the system prompts for a user API key to continue uninterrupted.

## 📁 Project Structure

*   `streamlit_streamlined.py`: Main Web Interface (Entry Point).
*   `project_caii_framework.py`: Core AI Framework & LLM Handling.
*   `streamlined_simulation.py`: Simulation Logic & Agents.
*   `database.py`: Database Management (SQLAlchemy).
*   `structured_profile_generator.py`: Client Profile Generation.
*   `legacy/`: Archived older versions and scripts.

## 📄 License

Proprietary - Northwestern Mutual Internal Use Only
