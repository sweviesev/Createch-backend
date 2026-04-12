@echo off
REM ============================================================
REM CREATECH API — HTTPie Test Commands
REM Run these AFTER starting the server: python manage.py runserver
REM Install HTTPie: pip install httpie
REM ============================================================

echo ============================================================
echo CREATECH API — HTTPie Testing
echo ============================================================

REM --- 1. Register a new user ---
echo.
echo [1] POST /api/auth/register/
http POST http://127.0.0.1:8000/api/auth/register/ email=httpietest@createch.com password=Httpie@1234 confirm_password=Httpie@1234 first_name=HTTPie last_name=Tester role=client phone=09111222333

REM --- 2. Login ---
echo.
echo [2] POST /api/auth/login/
http POST http://127.0.0.1:8000/api/auth/login/ email=creator@createch.com password=Creator@1234

REM --- 3. Save the token from login response, then test authenticated endpoint ---
echo.
echo [3] GET /api/auth/me/   (paste token from step 2)
echo     http GET http://127.0.0.1:8000/api/auth/me/ "Authorization:Bearer YOUR_TOKEN_HERE"

REM --- 4. List services (public) ---
echo.
echo [4] GET /api/services/
http GET http://127.0.0.1:8000/api/services/

REM --- 5. List orders ---
echo.
echo [5] GET /api/orders/
http GET http://127.0.0.1:8000/api/orders/

REM --- 6. List users ---
echo.
echo [6] GET /api/users/
http GET http://127.0.0.1:8000/api/users/

REM --- 7. List categories ---
echo.
echo [7] GET /api/categories/
http GET http://127.0.0.1:8000/api/categories/

echo.
echo ============================================================
echo All HTTPie tests complete!
echo ============================================================
pause
