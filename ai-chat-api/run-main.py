import uvicorn

def main():
    try:
        # Uvicorn 서버 실행
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()