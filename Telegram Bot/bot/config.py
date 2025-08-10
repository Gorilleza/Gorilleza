import os
from pathlib import Path
from dotenv import load_dotenv
from collections import deque, defaultdict

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ============================= ПУТИ =============================
BASE_DIR = Path(__file__).parent.parent.absolute()
DOWNLOADS_DIR = BASE_DIR / "downloads"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Файлы
INSTAGRAM_COOKIES = LOGS_DIR / "instagram_cookies.txt"
PENDING_QUEUE_FILE = LOGS_DIR / "pending_queue.json"
ADMIN_ACTIONS = LOGS_DIR / "admin_actions.log"
USER_STATES_FILE = LOGS_DIR / "user_states.txt"
USER_STATS_FILE = LOGS_DIR / "users.txt"
FEEDBACK_LOG = LOGS_DIR / "feedback.log"
REPORT_LOG = LOGS_DIR / "reports.log"
HISTORY_LOG = LOGS_DIR / "history.log"
MESSAGES_LOG = LOGS_DIR / "messages.log"
ERRORS_LOG = LOGS_DIR / "errors.log"
GIF_PATH = BASE_DIR / "assets/start.mp4"
LAST_LOG = LOGS_DIR / "last.log"

# Создание папок
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# =========================== КОНСТАНТЫ ==========================
COOKIE_AGE_LIMIT = 30 * 24 * 3600  # 30 дней
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_USER_QUEUE = 5
MAX_GLOBAL_QUEUE = 10
REQUEST_TIMEOUT = 300

TEST_URLS = {
    "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "youtube_shorts": "https://youtube.com/shorts/9JsL7wexSgI?si=tgf4SKLmwajsN58U",
    "instagram": "https://www.instagram.com/reel/DDrb-mPs3Tv/?igsh=OTk1ZmV0dXhtYzdu",
    "tiktok": "https://vt.tiktok.com/ZSrFHSc9u/"
}

RATE_LIMITS = {
    "default": {"interval": 5, "requests": 3},
    "status": {"interval": 60, "requests": 2},
    "download": {"interval": 10, "requests": 1}
}

# =============== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ =================
queue = deque()
user_queues = defaultdict(deque)

user_lang = defaultdict(lambda: "ru")
last_command_time = defaultdict(lambda: 0)
banned_users = dict()

request_counters = defaultdict(lambda: defaultdict(int))
last_request_time = defaultdict(float)