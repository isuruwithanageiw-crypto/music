$ErrorActionPreference = 'Stop'

# Setup paths entirely in user profile to bypass Windows UAC Admin prompts
$userDir = "$env:USERPROFILE"
$javaDir = "$userDir\Java"
$androidDir = "$userDir\Android"

Write-Host "1/5: Downloading Portable Java 17..."
if (!(Test-Path "$javaDir\jdk-17.0.2\bin\java.exe")) {
    New-Item -ItemType Directory -Force -Path $javaDir | Out-Null
    Invoke-WebRequest -Uri "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_windows-x64_bin.zip" -OutFile "$javaDir\jdk.zip"
    Expand-Archive -Path "$javaDir\jdk.zip" -DestinationPath $javaDir -Force
}
$env:JAVA_HOME = "$javaDir\jdk-17.0.2"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path

Write-Host "2/5: Downloading Android SDK Tools..."
if (!(Test-Path "$androidDir\cmdline-tools\latest\bin\sdkmanager.bat")) {
    New-Item -ItemType Directory -Force -Path "$androidDir\cmdline-tools" | Out-Null
    Invoke-WebRequest -Uri "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip" -OutFile "$androidDir\cmdline-tools.zip"
    Expand-Archive -Path "$androidDir\cmdline-tools.zip" -DestinationPath "$androidDir\cmdline-tools" -Force
    Rename-Item -Path "$androidDir\cmdline-tools\cmdline-tools" -NewName "latest"
}
$env:ANDROID_HOME = $androidDir
$env:Path += ";$androidDir\cmdline-tools\latest\bin"

Write-Host "3/5: Accepting Licenses..."
Start-Process "cmd.exe" -ArgumentList "/c echo y| sdkmanager.bat `"platform-tools`" `"platforms;android-34`" `"build-tools;34.0.0`"" -NoNewWindow -Wait
Start-Process "cmd.exe" -ArgumentList "/c echo y| sdkmanager.bat --licenses" -NoNewWindow -Wait

Write-Host "4/5: Configuring Flutter..."
$flutterBin = "C:\src\flutter\bin"
$env:Path += ";$flutterBin"
flutter.bat config --android-sdk $androidDir
flutter.bat doctor --android-licenses

Write-Host "5/5: Building Aura Music APK..."
cd "C:\Users\DINITHI\Desktop\mobi app\aura_music_flet"
flet.exe build apk --verbose > build_log.txt 2>&1

Write-Host "FINISHED!"
