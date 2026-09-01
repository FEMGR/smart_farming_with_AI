# Smart Farming Mobile

Expo React Native client for the Smart Urban Farming System backend.

## Prerequisites

- Node.js and npm
- A running Smart Farming backend on port `8000`
- Expo Go, an Android emulator, or a rebuilt Expo development build

## 1. Start the Backend

From the repository root, start the FastAPI backend:

```bash
PYTHONPATH=backend uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or use Docker from the `backend` directory:

```bash
docker compose up --build
```

Check that the API is reachable:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{"message":"Smart Farming API running"}
```

## 2. Start the Mobile App

From this `mobile` directory:

```bash
npm install
npx expo start
```

Then choose one:

- Press `w` to test in a browser.
- Press `a` to open an Android emulator.
- Scan the QR code with Expo Go on a physical phone.
- Use a rebuilt development build if you start Expo in development-build mode.

## 3. Configure the API URL

On the sign-in screen, tap the gear icon and set the backend URL.

Use the URL that matches where the app is running:

| Target | API URL |
| --- | --- |
| Web browser | `http://localhost:8000` |
| Android emulator | `http://10.0.2.2:8000` |
| iOS simulator | `http://localhost:8000` |
| Physical phone | `http://YOUR_COMPUTER_LAN_IP:8000` |

For a physical phone, find your computer IP with:

```bash
hostname -I
```

Example:

```text
http://192.168.1.25:8000
```

The phone and computer must be on the same Wi-Fi network. The backend must be started with `--host 0.0.0.0`, not only `127.0.0.1`.

## 4. Test Register and Sign In

1. Open the app.
2. Tap the gear icon and save the correct API URL.
3. Tap `Don't have an account? Register`.
4. Enter a new email and password.
5. Tap `Register`.

Registration automatically signs you in after the backend creates the account. If it fails, the app shows the backend or network error on the form.

To verify the backend directly:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Then sign in:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

## Common Issues

- `Cannot reach API`: the backend is not running, the API URL is wrong, or a physical phone cannot reach your computer.
- `Email already registered`: switch back to sign in or use another test email.
- Development-build warning: rebuild the native development build after adding native packages like `expo-dev-client`, or press `s` in Expo CLI to switch to Expo Go.
