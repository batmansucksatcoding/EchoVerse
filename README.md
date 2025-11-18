# 🌌 EchoVerse - Your Emotional Journey
EchoVerse is an innovative emotional journaling platform that transforms your feelings into beautiful visual art. Track your emotional journey, gain AI-powered insights, and watch your mood evolve into a unique "blob" that represents your emotional landscape.

## ✨ Features

### 📝 **Smart Journaling**
- Write daily entries with a beautiful, intuitive interface
- Automatic emotion detection using AI
- Rich text support for expressive writing
- Entry search and filtering

### 🎨 **Mood Blob Visualization**
- Watch your emotions evolve into unique, generative art
- Each entry influences your blob's appearance
- Track visual evolution over time
- Beautiful, shareable mood representations

### 🤖 **AI-Powered Insights**
- Powered by Google Gemini AI
- Emotion analysis using Hugging Face models
- Pattern recognition in your emotional journey
- Personalized recommendations and observations
- Weekly/monthly emotional summaries

### 📊 **Analytics & Tracking**
- Emotion trend visualization
- Streak tracking to build consistent habits
- Weekly emotion breakdown
- Historical data analysis
- Export your data anytime

### 🔐 **Privacy & Security**
- Secure user authentication
- Private, encrypted journal entries
- Your data belongs to you
- No third-party data sharing

## 🚀 Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Django 4.2+ |
| **Frontend** | HTML5, Tailwind CSS, JavaScript |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **AI/ML** | Google Gemini API, Hugging Face Transformers |
| **Image Processing** | Pillow, Python Imaging Library |
| **Authentication** | Django Built-in Auth |

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** ([Download](https://git-scm.com/downloads))
- **Virtual Environment** (venv or virtualenv)

You'll also need API keys:
- **Google Gemini API Key** ([Get here](https://makersuite.google.com/app/apikey))
- **Hugging Face API Token** ([Get here](https://huggingface.co/settings/tokens))

## 🛠️ Installation & Setup

See our detailed [SETUP.md](SETUP.md) guide for step-by-step instructions.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/batmansucksatcoding/EchoVerse.git
cd EchoVerse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` 🎉

## 📁 Project Structure

```
EchoVerse/
├── echoverse_project/      # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── journal/                # Main application
│   ├── models.py           # Database models (Entry, EmotionAnalysis, etc.)
│   ├── views.py            # View functions and logic
│   ├── urls.py             # App URL routing
│   ├── forms.py            # Django forms
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template
│   │   ├── dashboard.html  # Dashboard view
│   │   ├── entry_list.html # Journal entries
│   │   └── ...
│   ├── static/             # Static files (CSS, JS, images)
│   └── utils/              # Utility functions
│       ├── emotion_detection.py
│       └── blob_generator.py
├── media/                  # User-generated content
│   ├── mood_blobs/         # Generated blob images
│   └── uploads/            # User uploads
├── static_root/            # Collected static files (production)
├── .env                    # Environment variables (not in git)
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
├── README.md               # This file
└── SETUP.md                # Detailed setup guide
```

## 🔑 Environment Variables

Create a `.env` file in the project root with these variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/echoverse

# API Keys
GEMINI_API_KEY=your-gemini-api-key
HUGGING_FACE_TOKEN=hf_your_token_here

# Optional Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

## 📚 Usage Guide

### Creating Your First Entry

1. **Sign up** for an account
2. Navigate to **Dashboard**
3. Click **"New Entry"**
4. Write your thoughts and feelings
5. Submit - AI will analyze emotions automatically
6. View your **Mood Blob** evolve!

### Generating AI Insights

1. Go to **Insights** page
2. Click **"Generate New Insight"**
3. Wait for AI analysis (takes 10-30 seconds)
4. Explore patterns and recommendations

### Viewing Emotional Trends

1. Visit **Visuals** page
2. See emotion breakdown charts
3. Track your streak
4. View blob evolution timeline

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@batmansucksatcoding](https://github.com/batmansucksatcoding)
- Email: krishjha9702@gmail.com

## 🙏 Acknowledgments

- **Google Gemini** - For powerful AI insights
- **Hugging Face** - For emotion detection models
- **Tailwind CSS** - For beautiful, responsive design
- **Django Community** - For excellent documentation and support

<div align="center">
  <strong>Made with ❤️ and lots of ☕</strong>
  <br>
  <em>EchoVerse - Where emotions come alive</em>
</div>
