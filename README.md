# Krishi Sahayak AI (कृषि सहायक AI)
![Image](https://github.com/shreyaspathak11/krishi-sahayak-ai/blob/main/assets/krishi_sahayak.png)
## 1. Project Vision & Executive Summary
Krishi Sahayak AI is a revolutionary voice-first, AI-powered advisory platform engineered to empower the Indian farmer. It directly tackles the critical information gap in Indian agriculture caused by the digital divide and a lack of access to timely, reliable data.

Our vision is to provide every farmer with a personal, trusted agricultural expert they can consult simply by making a phone call. By leveraging a sophisticated Agentic AI grounded in a Retrieval-Augmented Generation (RAG) architecture, our system delivers scientifically accurate, context-aware, and actionable advice. We move beyond generic information by integrating a unique "Goldmine" Knowledge Base derived from thousands of real-world Kisan Call Centre (KCC) transcripts, ensuring our advice is not just academically sound but also practically proven in the Indian context.

## 2. How It Works: A Farmer's Journey
The user experience is designed for maximum simplicity:

1.  A farmer dials a standard Indian phone number.
2.  They are greeted by the AI assistant and can ask their question in their natural language.
3.  The AI engages in a brief, diagnostic conversation to understand the farmer's specific context (location, crop, etc.).
4.  Behind the scenes, the AI's "Agentic Brain" uses a suite of specialized tools to fetch real-time data (weather, market prices, news) and search its expert knowledge base.
5.  The AI synthesizes all this information into a simple, clear, and actionable spoken response, providing the farmer with a complete solution.

## 3. Core Features & Innovations
- **Voice-First Accessibility**: Our primary interface, powered by Exotel, eliminates the need for a smartphone or internet connection, making the service universally accessible.
- **Agentic Reasoning Engine**: The system is built around a powerful Agentic AI (Google Gemini) that can reason, delegate tasks to specialized tools, and synthesize information from multiple sources to provide a holistic answer.
- **"Goldmine" KCC Knowledge Base**: Our key innovation is a custom-built knowledge base created by ingesting and indexing thousands of Kisan Call Centre (KCC) transcripts. This allows our AI to learn from real-world farmer problems and expert solutions, making its advice incredibly practical and relevant.
- **Trustworthy RAG Architecture**: To eliminate AI "hallucinations," all advice is strictly grounded in our verified knowledge base using a Retrieval-Augmented Generation (RAG) pipeline. The AI finds facts first, then answers.
- **Real-Time Data Integration**: The AI has a comprehensive toolkit to access live data feeds, ensuring its advice is always current and contextually aware.

## 4. System Architecture & Technology
We have chosen a modern, scalable tech stack optimized for performance and reliability.

- **Backend Framework**: FastAPI (Python) for building a high-performance, asynchronous API.
- **AI Orchestration**: LangChain provides the framework for our agentic architecture, connecting the LLM with our custom tools.
- **Core Language Model**: Google Gemini Pro is used for its advanced reasoning, multilingual capabilities, and tool-calling functions.
- **Voice & Telephony**: Exotel provides the robust IVR, Speech-to-Text (STT), and Text-to-Speech (TTS) services necessary for a seamless voice experience in India.
- **Knowledge Base**: ChromaDB serves as our efficient, local vector store for the RAG pipeline.
- **External Data APIs**:
    - **PyOWM**: For real-time weather, air pollution, and UV index data from OpenWeatherMap.
    - **GNews API**: For fetching the latest agricultural news.
    - **data.gov.in APIs**: For integrating official government data like real-time market prices.
- **Deployment (Demo)**: Uvicorn, ngrok

---

## 🤝 Getting Started: How to Contribute

We are thrilled to have you join us! Follow these steps to get the project running on your local machine.

### Prerequisites

- Python 3.9+
- An Exotel Free Trial account
- API keys for Google AI Studio and OpenWeatherMap

### Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [URL_OF_YOUR_GIT_REPOSITORY]
   cd krishi_sahayak_ai
   ```

2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   - Make a copy of `.env.example` (or create a new file) and name it `.env`
   - Fill in your API keys and Exotel credentials in the `.env` file

5. **Build the Knowledge Base:**
   
   **Option A: Complete Setup (PDF + KCC Data) [RECOMMENDED]**
   ```bash
   # First run PDF ingestion
   python app/knowledge_base/ingest.py
   
   # Then run KCC ingestion for real farmer data
   python app/knowledge_base/ingest_kcc_data.py
   ```
   
   **Option B: PDF Documents Only**
   ```bash
   # Place your agricultural PDF documents into data/source_documents/
   python app/knowledge_base/ingest.py
   ```
   
   The KCC integration adds 50,000+ real farmer queries and expert answers from the official government agricultural helpline database.

### Running the Application

1. **Start the AI Server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Expose Your Server with ngrok:**
   - Open a new terminal
   - Start ngrok to create a public URL for your server:
   ```bash
   ngrok http 8000
   ```
   - Copy the `https://` forwarding URL provided by ngrok

3. **Configure Exotel:**
   - Log in to your Exotel dashboard
   - Go to the "App Bazaar" and create a call flow
   - Point the "Connect" applet to your ngrok URL: `[YOUR_NGROK_URL]/handle-call-initial`
   - Remember to update the `YOUR_NGROK_URL` placeholder in `app/main.py` as well!

**You are now ready to call your Exophone and interact with the AI!**

---

## 5. Future Scope & Vision 🚀
This project has been built on a solid foundation, designed for future growth. While our current implementation is a powerful proof-of-concept, we have a clear vision for its evolution into a national-scale, production-grade service.

### A. Upgrading Voice and Telephony Infrastructure
Our use of Exotel was highly effective for the demo phase but was constrained by trial limitations. The next step is to secure funding to transition to a fully-featured, enterprise-grade cloud telephony plan. This would unlock:

- **Scalability**: The ability to handle thousands of concurrent calls without issue.
- **Reliability**: A service-level agreement (SLA) guaranteeing uptime for mission-critical availability.
- **Advanced Features**: Access to richer call analytics and management features.

### B. State-of-the-Art Speech Models
To create a more natural and seamless conversational experience, we will integrate best-in-class, specialized models for speech processing:

- **Speech-to-Text (STT)**: We will fine-tune a model like Whisper on Indian agricultural dialects. This will dramatically improve transcription accuracy, especially for farmers speaking in regional accents or using colloquial terms.
- **Text-to-Speech (TTS)**: We will leverage advanced TTS models like Google's WaveNet or ElevenLabs to provide a more human-like, empathetic, and clear voice for the AI assistant, moving beyond standard robotic IVR tones.

### C. Expansion to a Multi-Channel Platform
While voice will always be our primary interface, we will expand to other channels to cater to a wider range of users:

- **WhatsApp Integration**: A WhatsApp chatbot will allow farmers to send text queries and receive text-based answers, links, and even images (e.g., sending a photo of a diseased plant for analysis).
- **Simple Mobile App**: A low-bandwidth mobile application will provide a graphical interface for accessing advisories, market prices, and news in a more structured format.

By pursuing these advancements, Krishi Sahayak AI can evolve from an innovative project into an essential, life-changing tool for millions of farmers across India.

---

## 🌱 Core Principles

- **Farmer-First**: Every feature we build must be easy to use, accessible, and solve a real-world problem for farmers.
- **Trust Through Grounding**: We will always prioritize factual accuracy. Our AI is designed to be an explainer of verified data, not a creator of new information.
- **Open and Collaborative**: We believe the best solutions are built together. All ideas are welcome.

---

## 📂 Project Structure

```
krishi_sahayak_ai/
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── agentic_core.py      # Core AI agent logic
│   ├── tools.py             # AI tools (weather, knowledge base, etc.)
│   └── knowledge_base/
│       ├── __init__.py
│       └── ingest.py        # PDF ingestion and vector store creation
├── data/
│   └── source_documents/    # Agricultural PDF documents
└── vector_store/            # ChromaDB vector database
```

---

## 🤝 Contributing

We welcome contributions from developers, agricultural experts, and anyone passionate about empowering farmers! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Areas Where We Need Help:
- Integration with government agricultural APIs
- Multi-language support (Hindi, regional languages)
- UI/UX improvements for voice interactions
- Documentation and testing
- Mobile app development (future phase)

---

**We are incredibly excited to build this future with you. Let's empower our farmers, together.** 🌾🤝

---

*Made with ❤️ for Indian farmers*
