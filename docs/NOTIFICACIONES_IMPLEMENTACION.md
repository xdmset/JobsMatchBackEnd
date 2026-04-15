# Guía de Implementación de Notificaciones Push

## Estado actual del backend

### Lo que YA está implementado

| Componente | Archivo | Estado |
|---|---|---|
| Modelo BD `notificaciones` | `app/models/notificacion.py` | Completo |
| Schemas Pydantic | `app/schemas/notificacion.py` | Completo |
| CRUD notificaciones | `app/crud/crud_notificacion.py` | Completo |
| Endpoints REST | `app/api/v1/endpoints/notificaciones.py` | Completo |
| Firebase Admin SDK | `app/services/notification_service.py` | Parcial |
| Credenciales FCM | `jobmatch-notifications-firebase-adminsdk-*.json` | Completo |
| Trigger en swipes | `app/api/v1/endpoints/swipes.py` | Sin token |
| Trigger en postulaciones | `app/api/v1/endpoints/postulaciones.py` | Sin token |

### Lo que FALTA en el backend

#### 1. Campo `fcm_token` en el modelo User

**Archivo:** `app/models/user.py`

Agregar la columna al modelo:

```python
fcm_token = Column(String(512), nullable=True)
```

Y crear la migración:

```bash
alembic revision --autogenerate -m "add_fcm_token_to_usuarios"
alembic upgrade head
```

---

#### 2. Endpoint para registrar el token FCM

Crear o agregar en `app/api/v1/endpoints/users.py` (o donde manejes el perfil del usuario):

```python
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User

class FCMTokenUpdate(BaseModel):
    fcm_token: str

@router.put("/me/fcm-token", status_code=204)
def actualizar_fcm_token(
    body: FCMTokenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.fcm_token = body.fcm_token
    db.commit()
```

---

#### 3. Pasar el token al servicio de notificaciones

En `app/api/v1/endpoints/swipes.py`, cuando se llama a `notificar_like_recibido` o `notificar_match`, recuperar el token del usuario destinatario:

```python
# Ejemplo: buscar el usuario empresa y pasar su token
usuario_empresa = db.query(User).filter(User.id == empresa_user_id).first()
notification_service.notificar_like_recibido(
    db=db,
    empresa_id=empresa_user_id,
    estudiante_nombre=...,
    vacante_titulo=...,
    vacante_id=...,
    estudiante_id=...,
    fcm_token=usuario_empresa.fcm_token,  # <-- agregar esto
)
```

Lo mismo aplica en `app/api/v1/endpoints/postulaciones.py` para `notificar_cambio_estado_postulacion`.

---

## Implementación en React (Web)

### 1. Instalar dependencias

```bash
npm install firebase
```

### 2. Configurar Firebase en el proyecto

Crear `src/lib/firebase.js`:

```javascript
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

const firebaseConfig = {
  // Obtener estos valores de la consola de Firebase del proyecto "jobmatch-notifications"
  apiKey: "...",
  authDomain: "...",
  projectId: "jobmatch-notifications",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "...",
};

const app = initializeApp(firebaseConfig);
export const messaging = getMessaging(app);
```

### 3. Crear el Service Worker

Crear el archivo `public/firebase-messaging-sw.js` (debe estar en `/public`):

```javascript
importScripts("https://www.gstatic.com/firebasejs/10.0.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.0.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "...",
  authDomain: "...",
  projectId: "jobmatch-notifications",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "...",
});

const messaging = firebase.messaging();

// Maneja notificaciones cuando la app está en segundo plano
messaging.onBackgroundMessage((payload) => {
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
    icon: "/logo.png",
    data: payload.data,
  });
});
```

### 4. Hook para manejar notificaciones

Crear `src/hooks/useNotifications.js`:

```javascript
import { useEffect } from "react";
import { getToken, onMessage } from "firebase/messaging";
import { messaging } from "../lib/firebase";
import api from "../lib/api"; // tu cliente axios/fetch

const VAPID_KEY = "..."; // Obtener de Firebase Console > Project Settings > Cloud Messaging > Web Push certificates

export function useNotifications() {
  useEffect(() => {
    requestPermissionAndRegisterToken();
    
    const unsubscribe = onMessage(messaging, (payload) => {
      // Notificación recibida con la app en primer plano
      console.log("Notificación recibida:", payload);
      // Mostrar toast/snackbar con payload.notification.title y .body
      // También puedes actualizar el contador de notificaciones no leídas
    });

    return () => unsubscribe();
  }, []);
}

async function requestPermissionAndRegisterToken() {
  try {
    const permission = await Notification.requestPermission();
    if (permission !== "granted") return;

    const token = await getToken(messaging, { vapidKey: VAPID_KEY });
    if (token) {
      // Registrar el token en nuestro backend
      await api.put("/api/v1/users/me/fcm-token", { fcm_token: token });
    }
  } catch (error) {
    console.error("Error registrando token FCM:", error);
  }
}
```

### 5. Usar el hook en el componente raíz

En `src/App.jsx` o el componente que envuelve la app autenticada:

```javascript
import { useNotifications } from "./hooks/useNotifications";

export default function App() {
  useNotifications(); // Llamar solo cuando el usuario está autenticado

  return (...);
}
```

### 6. Componente para listar notificaciones

```javascript
import { useEffect, useState } from "react";
import api from "../lib/api";

export function Notificaciones() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [noLeidas, setNoLeidas] = useState(0);

  useEffect(() => {
    cargarNotificaciones();
    cargarResumen();
  }, []);

  async function cargarNotificaciones() {
    const { data } = await api.get("/api/v1/notificaciones/");
    setNotificaciones(data);
  }

  async function cargarResumen() {
    const { data } = await api.get("/api/v1/notificaciones/resumen");
    setNoLeidas(data.no_leidas);
  }

  async function marcarLeida(id) {
    await api.put(`/api/v1/notificaciones/${id}/leer`);
    setNotificaciones((prev) =>
      prev.map((n) => (n.id === id ? { ...n, leida: true } : n))
    );
    setNoLeidas((prev) => Math.max(0, prev - 1));
  }

  return (
    <div>
      <h2>Notificaciones ({noLeidas} sin leer)</h2>
      {notificaciones.map((n) => (
        <div key={n.id} style={{ opacity: n.leida ? 0.5 : 1 }}>
          <strong>{n.titulo}</strong>
          <p>{n.mensaje}</p>
          {!n.leida && (
            <button onClick={() => marcarLeida(n.id)}>Marcar como leída</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

---

## Implementación en Flutter

### 1. Agregar dependencias en `pubspec.yaml`

```yaml
dependencies:
  firebase_core: ^3.0.0
  firebase_messaging: ^15.0.0
  flutter_local_notifications: ^17.0.0
```

### 2. Configuración Android

**`android/app/build.gradle`** — asegúrate de tener `google-services`:

```groovy
apply plugin: 'com.google.gms.google-services'
```

**`android/build.gradle`**:

```groovy
dependencies {
  classpath 'com.google.gms:google-services:4.4.0'
}
```

Descargar `google-services.json` desde Firebase Console y colocarlo en `android/app/`.

### 3. Configuración iOS

Descargar `GoogleService-Info.plist` desde Firebase Console y colocarlo en `ios/Runner/`.

En `ios/Runner/AppDelegate.swift`:

```swift
import UIKit
import Flutter
import FirebaseCore
import FirebaseMessaging

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    FirebaseApp.configure()
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

### 4. Servicio de notificaciones Flutter

Crear `lib/services/notification_service.dart`:

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Handler para mensajes en segundo plano (debe ser top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // No necesitas hacer nada aquí si solo quieres mostrar la notificación
  // Firebase lo hace automáticamente en background
  print('Notificación en background: ${message.notification?.title}');
}

class NotificationService {
  static final _messaging = FirebaseMessaging.instance;
  static final _localNotifications = FlutterLocalNotificationsPlugin();

  static Future<void> initialize({required String authToken, required String baseUrl}) async {
    // Registrar handler de background
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Pedir permisos
    await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Configurar notificaciones locales (para primer plano en Android)
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    await _localNotifications.initialize(
      const InitializationSettings(android: androidSettings, iOS: iosSettings),
    );

    // Crear canal Android
    const channel = AndroidNotificationChannel(
      'jobmatch_channel',
      'JobMatch Notificaciones',
      importance: Importance.high,
    );
    await _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);

    // Obtener token y registrarlo en el backend
    final token = await _messaging.getToken();
    if (token != null) {
      await _registerTokenInBackend(token, authToken, baseUrl);
    }

    // Escuchar cambios de token (FCM puede rotar el token)
    _messaging.onTokenRefresh.listen((newToken) {
      _registerTokenInBackend(newToken, authToken, baseUrl);
    });

    // Manejar notificaciones cuando la app está en primer plano
    FirebaseMessaging.onMessage.listen((message) {
      _showLocalNotification(message);
    });

    // Manejar tap en notificación cuando la app estaba en segundo plano
    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      _handleNotificationTap(message);
    });

    // Manejar tap cuando la app estaba completamente cerrada
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationTap(initialMessage);
    }
  }

  static Future<void> _registerTokenInBackend(
    String token,
    String authToken,
    String baseUrl,
  ) async {
    try {
      await http.put(
        Uri.parse('$baseUrl/api/v1/users/me/fcm-token'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $authToken',
        },
        body: jsonEncode({'fcm_token': token}),
      );
    } catch (e) {
      print('Error registrando FCM token: $e');
    }
  }

  static void _showLocalNotification(RemoteMessage message) {
    final notification = message.notification;
    if (notification == null) return;

    _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'jobmatch_channel',
          'JobMatch Notificaciones',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: DarwinNotificationDetails(),
      ),
      payload: jsonEncode(message.data),
    );
  }

  static void _handleNotificationTap(RemoteMessage message) {
    final tipo = message.data['tipo'];
    // Navegar según el tipo de notificación
    // Ejemplo con GoRouter o Navigator:
    switch (tipo) {
      case 'match':
        // navegar a la pantalla de postulaciones
        break;
      case 'like_recibido':
        // navegar al perfil del estudiante
        break;
      case 'postulacion_estado':
        // navegar al detalle de la postulación
        break;
    }
  }
}
```

### 5. Inicializar el servicio tras el login

```dart
// En tu bloc/provider/controller de auth, después de hacer login:
await NotificationService.initialize(
  authToken: response.accessToken,
  baseUrl: 'https://tu-backend.com',
);
```

### 6. Pantalla de notificaciones Flutter

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NotificacionesScreen extends StatefulWidget {
  final String authToken;
  final String baseUrl;
  const NotificacionesScreen({required this.authToken, required this.baseUrl, super.key});

  @override
  State<NotificacionesScreen> createState() => _NotificacionesScreenState();
}

class _NotificacionesScreenState extends State<NotificacionesScreen> {
  List<Map<String, dynamic>> notificaciones = [];
  int noLeidas = 0;

  @override
  void initState() {
    super.initState();
    _cargarNotificaciones();
    _cargarResumen();
  }

  Future<void> _cargarNotificaciones() async {
    final res = await http.get(
      Uri.parse('${widget.baseUrl}/api/v1/notificaciones/'),
      headers: {'Authorization': 'Bearer ${widget.authToken}'},
    );
    setState(() {
      notificaciones = List<Map<String, dynamic>>.from(jsonDecode(res.body));
    });
  }

  Future<void> _cargarResumen() async {
    final res = await http.get(
      Uri.parse('${widget.baseUrl}/api/v1/notificaciones/resumen'),
      headers: {'Authorization': 'Bearer ${widget.authToken}'},
    );
    final data = jsonDecode(res.body);
    setState(() => noLeidas = data['no_leidas']);
  }

  Future<void> _marcarLeida(int id) async {
    await http.put(
      Uri.parse('${widget.baseUrl}/api/v1/notificaciones/$id/leer'),
      headers: {'Authorization': 'Bearer ${widget.authToken}'},
    );
    setState(() {
      notificaciones = notificaciones.map((n) {
        if (n['id'] == id) return {...n, 'leida': true};
        return n;
      }).toList();
      noLeidas = (noLeidas - 1).clamp(0, 9999);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Notificaciones ($noLeidas sin leer)'),
        actions: [
          TextButton(
            onPressed: () async {
              await http.put(
                Uri.parse('${widget.baseUrl}/api/v1/notificaciones/leer-todas'),
                headers: {'Authorization': 'Bearer ${widget.authToken}'},
              );
              _cargarNotificaciones();
              setState(() => noLeidas = 0);
            },
            child: const Text('Leer todas'),
          )
        ],
      ),
      body: ListView.builder(
        itemCount: notificaciones.length,
        itemBuilder: (ctx, i) {
          final n = notificaciones[i];
          return ListTile(
            title: Text(
              n['titulo'],
              style: TextStyle(
                fontWeight: n['leida'] == false ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            subtitle: Text(n['mensaje']),
            trailing: n['leida'] == false
                ? IconButton(
                    icon: const Icon(Icons.check),
                    onPressed: () => _marcarLeida(n['id']),
                  )
                : null,
          );
        },
      ),
    );
  }
}
```

---

## Resumen de pasos para activar push notifications

1. **Backend** — Agregar `fcm_token` al modelo `User` y hacer la migración
2. **Backend** — Crear endpoint `PUT /api/v1/users/me/fcm-token`
3. **Backend** — En `swipes.py` y `postulaciones.py`, consultar `user.fcm_token` y pasarlo al servicio de notificaciones
4. **React** — Instalar `firebase`, crear `firebase-messaging-sw.js` en `/public`, usar el hook `useNotifications`
5. **Flutter** — Agregar dependencias, colocar `google-services.json` / `GoogleService-Info.plist`, inicializar `NotificationService` tras el login
6. **Firebase Console** — Asegurarse de que el proyecto `jobmatch-notifications` tenga habilitado Cloud Messaging y obtener la VAPID key para web
