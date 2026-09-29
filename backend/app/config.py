"""Application configuration and default assumptions."""
import os

# Mosca's Theorem defaults
CRQC_HORIZON_YEARS = int(os.getenv("ECDAT_CRQC_HORIZON", "7"))
DEFAULT_DATA_LIFETIME_YEARS = int(os.getenv("ECDAT_DEFAULT_DATA_LIFETIME", "5"))
DEFAULT_MIGRATION_TIME_YEARS = int(os.getenv("ECDAT_DEFAULT_MIGRATION_TIME", "2"))

# Scanner settings
MAX_FILE_SIZE_BYTES = int(os.getenv("ECDAT_MAX_FILE_SIZE", str(5 * 1024 * 1024)))  # 5MB
SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".c", ".cpp", ".h",
    ".rs", ".rb", ".php", ".cs", ".swift", ".kt",
    ".conf", ".cfg", ".yml", ".yaml", ".toml", ".ini", ".json", ".xml",
    ".pem", ".crt", ".cer", ".key", ".der",
    ".sh", ".bash", ".zsh",
    ".txt", ".md", ".lock",
}
SCAN_FILENAMES = {
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "requirements.txt", "package.json", "pom.xml", "build.gradle",
    "Cargo.toml", "go.mod", "Gemfile", "Makefile",
}

# API
CORS_ORIGINS = os.getenv("ECDAT_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
