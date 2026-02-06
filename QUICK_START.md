# Quick Start Guide

## 🚀 Start the Application

```bash
python main.py
```

## 🌐 Access URLs

- **Landing Page:** http://localhost:8000/
- **Login:** http://localhost:8000/login
- **Signup:** http://localhost:8000/signup
- **Profile:** http://localhost:8000/profile

## 📁 Project Structure at a Glance

```
app/
├── config.py           → All settings (DB, secrets, etc.)
├── database.py         → MongoDB connection
├── auth_utils.py       → Login/password logic
├── restaurant_service.py → Search logic
├── models/user.py      → User data structure
├── routes/
│   ├── auth.py        → /login, /signup routes
│   └── main.py        → /profile, /search routes
├── templates/         → HTML files
└── static/           → CSS, JS, images
```

## 🔧 Common Tasks

### Add a New Route
1. Open `app/routes/main.py` or `app/routes/auth.py`
2. Add your route:
```python
@router.get("/mypage")
async def my_page(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})
```

### Access Database
```python
from app.database import db

# Find user
user = db.users.find_one({"email": "user@example.com"})

# Insert data
db.users.insert_one({"email": "new@example.com", "name": "John"})
```

### Add Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Something happened")
logger.error("Error occurred")
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Connection Refused** | Check if server is running: `netstat -ano \| findstr :8000` |
| **Method Not Allowed** | Check form `method="post"` matches route `@router.post()` |
| **Template Not Found** | Templates must be in `app/templates/` folder |
| **Import Error** | Make sure you're running from project root |
| **MongoDB Error** | Check MongoDB service is running |

## 📝 Check Logs

```bash
# View last 20 lines
Get-Content app.log -Tail 20

# Watch logs in real-time
Get-Content app.log -Wait -Tail 20
```

## 🧹 Cleanup Old Files

Once you verify everything works:

```bash
# Delete backup folder
Remove-Item -Recurse -Force old_backup

# Delete unused nested project
Remove-Item -Recurse -Force "major project"
```

## ⚙️ Environment Variables (.env)

```env
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=restaurant_finder
SECRET_KEY=your-secret-key-change-this
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 📚 More Help

- See `README.md` for detailed documentation
- See `REFACTORING_SUMMARY.md` for what changed
- Check `app.log` for error details
