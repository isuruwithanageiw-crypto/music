$ErrorActionPreference = 'Stop'

Write-Host "1/5: Installing Java 17..."
winget install --id Microsoft.OpenJDK.17 --silent --accept-package-agreements --accept-source-agreements
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.10.7-hotspot" # winget default
if (!(Test-Path $env:JAVA_HOME)) { 
    $env:JAVA_HOME = (Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Filter "jdk-17*" | Select-Object -First 1).FullName 
}
if (!(Test-Path $env:JAVA_HOME)) {
    $env:JAVA_HOME = (Get-ChildItem "C:\Program Files\Microsoft" -Filter "jdk-17*" | Select-Object -First 1).FullName
}

Write-Host "2/5: Setting up Android SDK..."
$androidHome = "C:\Android"
if (!(Test-Path "$androidHome\cmdline-tools\latest\bin\sdkmanager.bat")) {
    New-Item -ItemType Directory -Force -Path "$androidHome\cmdline-tools"
    Invoke-WebRequest -Uri "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip" -OutFile "cmdline-tools.zip"
    Expand-Archive -Path "cmdline-tools.zip" -DestinationPath "$androidHome\cmdline-tools" -Force
    Rename-Item -Path "$androidHome\cmdline-tools\cmdline-tools" -NewName "latest"
}

[Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidHome, "User")
$env:ANDROID_HOME = $androidHome
$env:Path += ";$androidHome\cmdline-tools\latest\bin"

Write-Host "3/5: Accepting Licenses..."
echo y | sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" | Out-Null
echo y | sdkmanager --licenses | Out-Null

Write-Host "4/5: Configuring Flutter..."
$flutterBin = "C:\src\flutter\bin"
$env:Path += ";$flutterBin"
flutter config --android-sdk $androidHome
flutter doctor --android-licenses

Write-Host "5/5: Building Aura Music APK via Flet..."
cd "C:\Users\DINITHI\Desktop\mobi app\aura_music_flet"
flet build apk --verbose > build_log.txt 2>&1

Write-Host "FINISHED!"
