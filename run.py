import subprocess

# Add root folder to sys.path so streamlit runs properly
sys.path.append(os.path.abspath("."))

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/ui/dashboard.py"])
