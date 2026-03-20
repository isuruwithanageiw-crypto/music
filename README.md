# Aura Music (Flet Version)

Aura Music is a premium music application built entirely in **Python** using the **Flet** framework.

## Prerequisites
1. Python 3.8+ installed on your computer.
2. (Optional) A virtual environment.

## Running the App

Follow these steps to run the application on your computer:

1. Open your terminal or command prompt.
2. Navigate to this directory:
   ```bash
   cd "C:\Users\DINITHI\Desktop\mobi app\aura_music_flet"
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```

## Mobile Deployment (Android / iOS)
Because the app is built using Flet, it can be compiled natively to mobile phones using `flet build`. 

To compile to an Android APK:
1. Provide the flutter build tools on your PC (since Flet uses Flutter under the hood for compilation).
2. Run:
   ```bash
   flet build apk
   ```

Note on **Lock Screen Audio**: Flet's `ft.Audio` component naturally utilizes the host platform's native media players. When compiled to APK/AAB, standard iOS/Android background audio rules apply.

Enjoy!
