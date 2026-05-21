from app import create_app

print("1. Starting App")

app = create_app()

print("2. App Created")

if __name__ == '__main__':

    print("3. Running Server")

    app.run(
        debug=True,
        use_reloader=False
    )