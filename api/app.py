from dotenv import load_dotenv  # noqa: E402 — must run before app imports

load_dotenv()

from src.api import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
