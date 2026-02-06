# Success Map - Career Guidance Application

A FastAPI-based career guidance and restaurant finder application with user authentication and MongoDB integration.

## 🏗️ Project Structure

```
Major_Project/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration settings
│   ├── database.py              # MongoDB connection (singleton)
│   ├── auth_utils.py            # Authentication utilities
│   ├── restaurant_service.py   # Restaurant finder service
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── user.py             # User models
│   ├── routes/                  # Route modules
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes (login, signup, logout)
│   │   └── main.py             # Main app routes (home, profile, search)
│   ├── static/                  # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/               # Jinja2 HTML templates
│       ├── base.html
│       ├── index.html
│       ├── landing.html
│       ├── login.html
│       ├── profile.html
│       └── signup.html
├── main.py                      # Application entry point
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
├── app.log                      # Application logs
└── old_backup/                  # Backup of old files

```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB running on localhost:27017
- Required Python packages (see requirements.txt)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create/update `.env` file:
   ```env
   MONGO_URI=mongodb://localhost:27017/
   DATABASE_NAME=restaurant_finder
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   ```

3. **Start MongoDB:**
   Ensure MongoDB service is running on your system.

### Running the Application

**Start the server:**
```bash
python main.py
```

The application will be available at: **http://localhost:8000**

## 📋 Features

### Authentication
- ✅ User registration (signup)
- ✅ User login with JWT tokens
- ✅ Password hashing with Argon2
- ✅ Secure HTTP-only cookies
- ✅ User profile page

### Restaurant Finder
- 🔍 Search restaurants by dish and location
- 📍 Filter by city and sub-location
- ⭐ Rating-based sorting
- 🍽️ Detailed restaurant information

## 🔧 Key Components

### Configuration (`app/config.py`)
Centralized configuration for:
- Database settings
- Security keys
- Server settings
- Debug mode

### Database (`app/database.py`)
Singleton pattern for MongoDB connection:
- Automatic connection handling
- Database and collection access
- Connection pooling

### Authentication (`app/auth_utils.py`)
- Password hashing/verification (Argon2)
- JWT token generation
- User authentication
- Token validation from cookies/headers

### Routes

#### Authentication Routes (`app/routes/auth.py`)
- `GET /login` - Display login page
- `POST /login` - Handle login form
- `GET /signup` - Display signup page
- `POST /signup` - Handle signup form
- `GET /logout` - Logout user

#### Main Routes (`app/routes/main.py`)
- `GET /` - Redirect to welcome page
- `GET /welcome` - Landing page
- `GET /app` - Main app (requires auth)
- `GET /profile` - User profile (requires auth)
- `POST /search` - Search restaurants
- `GET /api/cities` - Get available cities
- `GET /api/sublocations` - Get sub-locations
- `GET /api/dishes` - Get available dishes

## 🐛 Troubleshooting

### "Method Not Allowed" Error on Login

**Cause:** This error (HTTP 405) occurs when:
- Form method doesn't match the route definition
- Form action points to wrong URL
- Missing route definition

**How to Debug:**
1. Open browser Developer Tools (F12)
2. Go to "Network" tab
3. Attempt login/signup
4. Check the request:
   - Method (should be POST for login/signup)
   - URL (should match `/login` or `/signup`)
   - Status code and error message

**Solution:**
Ensure your login form has:
```html
<form action="/login" method="post">
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <button type="submit">Sign In</button>
</form>
```

### Connection Refused Error

**Cause:** Server not running or wrong port

**Solution:**
1. Check if Python process is running
2. Verify MongoDB is running
3. Check logs in `app.log`
4. Restart the server: `python main.py`

### Database Connection Error

**Cause:** MongoDB not running or wrong connection string

**Solution:**
1. Start MongoDB service
2. Check `MONGO_URI` in `.env`
3. Verify database name in configuration

## 📝 Development Tips

### Adding New Routes
1. Create route in appropriate file (`app/routes/`)
2. Import and include router in `main.py`
3. Add templates to `app/templates/`

### Adding New Models
1. Create model in `app/models/`
2. Export in `app/models/__init__.py`
3. Import where needed

### Database Operations
```python
from app.database import db

# Insert document
db.users.insert_one({"email": "user@example.com"})

# Find document
user = db.users.find_one({"email": "user@example.com"})

# Update document
db.users.update_one({"email": "user@example.com"}, {"$set": {"name": "John"}})
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## 🔒 Security Notes

1. **Change SECRET_KEY** in production
2. **Enable HTTPS** (set `secure=True` for cookies)
3. **Use strong passwords** (8+ characters)
4. **Keep dependencies updated**
5. **Don't commit `.env` file** to version control

## 📦 Dependencies

Main packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pymongo` - MongoDB driver
- `python-jose` - JWT handling
- `passlib` - Password hashing
- `argon2-cffi` - Argon2 password hashing
- `python-dotenv` - Environment variables
- `pandas` - Data processing

## 🗂️ Old Files

Old implementation files have been moved to `old_backup/` folder:
- `old_backup/app.py` - Old monolithic app file
- `old_backup/auth.py` - Old auth module
- `old_backup/database.py` - Old database module
- `old_backup/templates/` - Old templates folder

You can safely delete this folder once you've verified the new structure works.

## ⚠️ Note on "major project" Folder

The nested `major project/` folder appears to be a different implementation (React + Node.js). If you're not using it, you can:
1. Move it to `old_backup/`
2. Delete it entirely
3. Keep it as a separate project

## 📧 Support

For issues or questions:
1. Check the logs in `app.log`
2. Review the troubleshooting section
3. Verify all dependencies are installed
4. Ensure MongoDB is running

---

**Last Updated:** October 24, 2025
