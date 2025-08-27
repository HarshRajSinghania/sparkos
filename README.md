# SparkOS

A digital space where teens can grow, learn, and have fun. SparkOS is a browser-based launcher with built-in apps tailored for teens, combining habit tracking, finance management, and an AI companion into one fun, gamified ecosystem.

## Features

- **Habit Tracker**: Build healthy routines with streaks and rewards
- **Teen Wallet**: Simple money tracker for allowance, chores, and savings
- **AI Chatbot**: Study helper and friendly companion
- **Gamification**: Earn XP, level up, and unlock achievements

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: HTML5, CSS3 (Tailwind CSS), JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login
- **Deployment**: Gunicorn with Nginx (production)

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sparkos.git
   cd sparkos
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///sparkos.db
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   flask run
   ```

7. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
sparkos/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
├── README.md              # This file
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── habit.py
│   └── wallet.py
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
└── templates/             # HTML templates
    ├── base.html
    ├── index.html
    ├── habits.html
    ├── wallet.html
    └── chat.html
```

## Features in Detail

### Habit Tracker
- Create and track daily, weekly, or monthly habits
- Visualize streaks and progress
- Set reminders and notifications
- Earn XP for completing habits

### Teen Wallet
- Track income and expenses
- Set and manage savings goals
- Categorize transactions
- View spending analytics

### AI Chatbot
- Study assistant for homework help
- Casual conversation mode
- Quick action buttons for common tasks
- Personalized responses based on user preferences

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [Tailwind CSS](https://tailwindcss.com/) - For styling
- [Font Awesome](https://fontawesome.com/) - For icons
- [Chart.js](https://www.chartjs.org/) - For data visualization

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/sparkos](https://github.com/yourusername/sparkos)
