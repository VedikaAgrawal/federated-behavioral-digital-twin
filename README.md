# Digital Twin & Federated Fraud Detection System 🛡️

A next-generation Credit Card Fraud Detection system that uses **Digital Twins** to model user behavior, **Markov Chains** for sequence modeling, and **Blockchain-based Federated Learning** for collaborative intelligence.

## 🌟 Key Features

### 1. The Digital Twin Model (Behavioral Identity)
Unlike traditional models that look at "Global Fraud Patterns", this system builds a unique profile for **every single user**.
- **State Tracking**: Tracks average spend, frequent locations, and merchant categories using Welford's online algorithm for variance.
- **Adaptive**: Updates in real-time with every legitimate transaction to evolve with the user's habits.

### 2. Sequence Modeling (Markov Chains)
- **Impossible Sequences**: Detects deviations in transaction flow using transition probabilities.
- **Behavioral Habits**: Identifies and validates recurring patterns (e.g., *Gas Station -> Restaurant* vs. *Gas Station -> Luxury Jewelry Store*).

### 3. Federated Learning (Blockchain Ledger)
- **Collaborative Intelligence**: Banks share anonymized behavioral model weights (e.g., high-amount trends, night-time risk) via a blockchain-simulated ledger.
- **Privacy-Preserving**: No sensitive user data (merchant names, locations) is ever shared; only abstracted risk parameters are synced.

### 4. Social Trust Network
- **Graph Analysis**: Tracks "Trusted Recipients" for transfers.
- **Risk Scoring**: Transactions to new recipients are assigned a weighted risk factor, requiring additional behavioral validation.

### 5. Interactive Dashboard
- Built with **Streamlit**.
- **Visualizes the Twin's Brain**: Real-time behavioral profiles, transition probabilities, and the federated global ledger.
- **Live Monitoring**: Simulates a transaction feed with instant decision-making.

## 📊 System Architecture & Flows

### 1. System Flowchart (High-Resolution)
Here is the operational flowchart detailing the system's transaction verification path:

![System Flowchart](assets/flowchart.png)

*For more details, view the formal [System Architecture Design (PDF)](assets/architeture.pdf).*

### 2. Transaction Processing Logic (Interactive Flow)
This flowchart shows how an incoming transaction is evaluated locally by the individual's Digital Twin and globally against the Federated Ledger:

```mermaid
graph TD
    A[Incoming Transaction] --> B[Fraud Engine]
    subgraph Local Analysis
        B --> C[Local Digital Twin]
        C --> C1[Welford's Online Stats]
        C --> C2[Markov Chain Sequence Model]
        C --> C3[Social Trust Graph]
    end
    subgraph Collaborative Defense
        B --> D[Blockchain-Federated Ledger]
        D --> D1[SHA-256 Hash Verification]
        D --> D2[BFT Median Filter Aggregation]
    end
    C --> E[Combined Decision Logic]
    D --> E
    E --> F{Risk Score Evaluation}
    F -->|Risk <= 0.60: APPROVED| G[Update Local Twin State]
    F -->|Risk > 0.85: DECLINED| H[Publish Anonymized Weights to Ledger]
    F -->|0.60 < Risk <= 0.85: REVIEW| I[Hold for Verification]
```

### 2. Privacy-Preserving Federated Learning Flow
This sequence illustrates how bank nodes share collaborative intelligence anonymously without exposing sensitive user data:

```mermaid
sequenceDiagram
    autonumber
    actor User as Cardholder Transaction
    participant BankA as Bank A (Local Node)
    participant Ledger as Shared Blockchain Ledger
    participant BankB as Bank B (Sister Node)

    User->>BankA: Submits transaction
    BankA->>Ledger: Fetches Global Wisdom (BFT Aggregated Weights)
    Ledger-->>BankA: Returns Global Anomaly Trends
    BankA->>BankA: Runs Local Digital Twin & Markov Sequence Check
    Note over BankA: Evaluates combined Risk Score
    alt If Transaction is Flagged as Fraud
        BankA->>Ledger: Publishes Anonymized Knowledge Block (SHA-256)
        Note over Ledger: Appends block & runs BFT Median Filter
    else If Transaction is Approved
        BankA->>BankA: Updates user's behavioral baseline in memory
    end
    Ledger->>BankB: Syncs updated global trends on next query
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.8+

### Installation
1.  Clone/Download this folder.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage
Run the dashboard:
```bash
streamlit run app.py
```

### How to Demo
1.  **Bootstrap**: Expand the *"Data Bootstrapping"* section in the sidebar and click **"Train Model from CSV"** to load historical data.
2.  **Train**: Click **"Generate Legit Transaction"** to see the Digital Twin learn and update its Behavioral Identity Profile.
3.  **Test**: Click **"Generate FRAUD Transaction"** to trigger the system's reaction to high amounts, impossible travel, or suspicious sequences.
4.  **Network**: Use the **"Global Sync"** controls to simulate collaborative defense by triggering attacks at a sister bank.

---

## 📂 Project Structure
- `src/`:
    - `digital_twin.py`: Core logic for state tracking, Markov Chains, and risk scoring.
    - `fraud_engine.py`: Orchestration layer for local twin and global ledger analysis.
    - `bfl_ledger.py`: Blockchain-simulated federated learning implementation.
    - `data_generator.py`: Synthetic data factory for simulation.
- `app.py`: The Streamlit Dashboard interface.
