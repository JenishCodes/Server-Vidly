import signal

from app import create_app, db, load_app_modules, greceful_shutdown

app = create_app()

with app.app_context():
    db.create_all()  # Ensure all tables are created
    load_app_modules(app)

# Handle graceful shutdown signals
signal.signal(signal.SIGTERM, greceful_shutdown)
signal.signal(signal.SIGINT, greceful_shutdown)

if __name__ == "__main__":
    print("Starting app...")
    app.run()
