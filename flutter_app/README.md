# RegisLite Flutter GUI

To nowe GUI oparte na Flutterze, zastępujące stary interfejs HTML/JS.

## Wymagania

- Flutter SDK (>= 3.1.0)
- Uruchomiony backend RegisLite (na porcie 8000)

## Uruchomienie

1. Upewnij się, że backend działa:
   ```bash
   python src/main.py
   ```

2. Przejdź do folderu `flutter_app`:
   ```bash
   cd flutter_app
   ```

3. Inicjalizacja platform (jeśli nie istnieją foldery android/web/etc):
   ```bash
   flutter create .
   ```

4. Pobierz zależności:
   ```bash
   flutter pub get
   ```

5. Uruchom aplikację:
   - Web: `flutter run -d chrome`
   - Desktop: `flutter run -d linux` (lub windows/macos)
   - Android: `flutter run` (wymaga emulatora i przekierowania portów adb reverse tcp:8000 tcp:8000)

## Funkcjonalność

- Upload plików ZIP (projektów)
- Terminal / Czat z AI (WebSocket)
- Motyw "Cyber Green"

## Konfiguracja API

Adres API jest domyślnie ustawiony na `localhost:8000` (lub `10.0.2.2:8000` dla Androida). Możesz to zmienić w `lib/services/api_service.dart`.
