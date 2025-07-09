# Claude Development Notes

## Server Management

### Django Development Server
- Start: `source venv/bin/activate && python manage.py runserver`
- Stop: `pkill -f "python manage.py runserver"` or Ctrl+C if running in foreground
- **Important**: Always stop test servers after testing is complete

### Commands to Remember
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt` (if requirements.txt exists)
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

## Project Structure
- Main app: `lyrics_analyzer/`
- Templates: `lyrics_analyzer/templates/lyrics_analyzer/`
- Static files: Not yet configured
- Database: SQLite (db.sqlite3)

## Current Features
- Lyrics input form with POST handling
- Google Gemini API integration for real AI analysis
- User authentication system (login/logout/register)
- Database storage for logged-in users (Song model with decimal sad_score)
- Session-based storage for anonymous users (ephemeral)
- Dark typewriter aesthetic theme
- Results sorted by sad score (highest first)
- Error handling with fallback for API failures

## API Setup
1. Get a Google AI Studio API key from https://aistudio.google.com/app/apikey
2. Copy the example environment file: `cp .env.local.example .env.local`
3. Edit `.env.local` and replace `your_api_key_here` with your actual API key
4. The app will automatically load the API key from the .env.local file

Note: The `.env.local` file is gitignored to keep your API key secure.

## API Features
- Real-time analysis of lyrics using Gemini 1.5 Flash model
- Structured JSON response with sad_score (1.0-10.0), tags, and description
- Fallback to dummy data if API fails
- Logging for debugging API issues

## Next Steps for Enhancement
1. Add API rate limiting and caching
2. Implement user feedback system for analysis quality
3. Add batch analysis for multiple songs
4. Create admin interface for managing analyses
5. Add export functionality for user data
6. Create requirements.txt file