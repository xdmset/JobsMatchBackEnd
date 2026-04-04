# PayPal En React Y Flutter

Esta guia describe como integrar el flujo de suscripciones PayPal del backend de JOBMATCH desde:

- React web
- Flutter movil

El backend ya expone estos endpoints:

- `GET /api/v1/payments/paypal/plans`
- `GET /api/v1/payments/paypal/plans/me`
- `POST /api/v1/payments/paypal/bootstrap`
- `POST /api/v1/payments/paypal/subscriptions`
- `POST /api/v1/payments/paypal/subscriptions/{paypal_subscription_id}/sync`
- `POST /api/v1/payments/paypal/subscriptions/{paypal_subscription_id}/cancel`
- `POST /api/v1/payments/paypal/webhook`
- `GET /api/v1/suscripciones/usuario/{usuario_id}/actual`
- `GET /api/v1/user/me`

## 1. Preparacion

Antes de tocar React o Flutter:

1. Configura PayPal Sandbox en tu backend.
2. Ejecuta migraciones.
3. Registra el webhook de PayPal.
4. Ejecuta `POST /api/v1/payments/paypal/bootstrap` con un usuario admin.
5. Verifica que `GET /api/v1/payments/paypal/plans` devuelva los 6 planes premium.
6. Verifica que `GET /api/v1/payments/paypal/plans/me` devuelva solo los planes del rol autenticado.

Variables importantes en backend:

```env
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_WEBHOOK_ID=...
PAYPAL_CURRENCY=MXN
```

## 2. Flujo Comun

El flujo es el mismo en web y movil:

1. El cliente consulta los planes.
2. El usuario elige uno.
3. El cliente llama `POST /payments/paypal/subscriptions`.
4. El backend devuelve `paypal_subscription_id` y `approve_url`.
5. El cliente abre `approve_url`.
6. El usuario aprueba en PayPal.
7. El cliente llama `POST /payments/paypal/subscriptions/{id}/sync`.
8. El backend sincroniza la suscripcion y actualiza `es_premium`.
9. El cliente consulta `GET /api/v1/user/me` o `GET /api/v1/suscripciones/usuario/{usuario_id}/actual`.

Importante:

- No actives premium solo porque PayPal redirigio al cliente.
- El estado final debe salir de `sync` o del webhook del backend.
- El cliente solo manda `billing_cycle`; el backend resuelve el plan premium correcto segun el rol autenticado.

## 3. React Web

### 3.1 URLs recomendadas

Usa rutas web como estas:

- `https://jobmatch.com.mx/payments/paypal/success`
- `https://jobmatch.com.mx/payments/paypal/cancel`

### 3.2 Obtener planes

```ts
export async function getPaypalPlans(token: string) {
  const response = await fetch("https://api.jobmatch.com.mx/api/v1/payments/paypal/plans/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("No fue posible obtener los planes");
  }

  return response.json();
}
```

### 3.3 Crear suscripcion

```ts
type BillingCycle = "mensual" | "semestral" | "anual";

export async function createPaypalSubscription(token: string, billingCycle: BillingCycle) {
  const response = await fetch("https://api.jobmatch.com.mx/api/v1/payments/paypal/subscriptions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      billing_cycle: billingCycle,
      return_url: "https://jobmatch.com.mx/payments/paypal/success",
      cancel_url: "https://jobmatch.com.mx/payments/paypal/cancel",
    }),
  });

  if (!response.ok) {
    throw new Error("No fue posible crear la suscripcion PayPal");
  }

  return response.json();
}
```

Respuesta esperada:

```json
{
  "paypal_subscription_id": "I-XXXX",
  "status": "APPROVAL_PENDING",
  "approve_url": "https://www.sandbox.paypal.com/..."
}
```

### 3.4 Redirigir al usuario

```ts
const result = await createPaypalSubscription(token, "mensual");
window.location.href = result.approve_url;
```

### 3.5 Pagina de success

Tu pagina React de success debe:

1. Leer query params o estado de navegacion.
2. Recuperar `paypal_subscription_id`.
3. Llamar al endpoint `sync`.
4. Refrescar el perfil del usuario.

Ejemplo:

```ts
export async function syncPaypalSubscription(token: string, paypalSubscriptionId: string) {
  const response = await fetch(
    `https://api.jobmatch.com.mx/api/v1/payments/paypal/subscriptions/${paypalSubscriptionId}/sync`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("No fue posible sincronizar la suscripcion");
  }

  return response.json();
}
```

### 3.6 Estado actual del usuario

Para saber si debe ver UI premium:

```ts
export async function getCurrentSubscription(token: string, userId: number) {
  const response = await fetch(
    `https://api.jobmatch.com.mx/api/v1/suscripciones/usuario/${userId}/actual`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("No fue posible obtener la suscripcion actual");
  }

  return response.json();
}
```

## 4. Flutter

### 4.1 URLs recomendadas

Para Flutter tienes dos opciones:

- Usar una ruta web intermedia como `https://jobmatch.com.mx/payments/paypal/mobile-success`
- Usar app links o universal links y redirigir desde esa ruta a la app

Recomendacion practica:

- `return_url`: `https://jobmatch.com.mx/payments/paypal/mobile-success`
- `cancel_url`: `https://jobmatch.com.mx/payments/paypal/mobile-cancel`

### 4.2 Crear suscripcion con `dio`

```dart
import 'package:dio/dio.dart';

final dio = Dio(
  BaseOptions(
    baseUrl: 'https://api.jobmatch.com.mx/api/v1',
    headers: {
      'Authorization': 'Bearer TU_TOKEN',
      'Content-Type': 'application/json',
    },
  ),
);

Future<Map<String, dynamic>> createPaypalSubscription(String billingCycle) async {
  final response = await dio.post(
    '/payments/paypal/subscriptions',
    data: {
      'billing_cycle': billingCycle,
      'return_url': 'https://jobmatch.com.mx/payments/paypal/mobile-success',
      'cancel_url': 'https://jobmatch.com.mx/payments/paypal/mobile-cancel',
    },
  );

  return Map<String, dynamic>.from(response.data);
}
```

### 4.3 Abrir PayPal

Puedes abrir `approve_url` con:

- `url_launcher`
- un navegador externo
- una custom tab / safari view controller

Ejemplo simple:

```dart
import 'package:url_launcher/url_launcher.dart';

Future<void> openPaypalApproval(String approveUrl) async {
  final uri = Uri.parse(approveUrl);
  await launchUrl(uri, mode: LaunchMode.externalApplication);
}
```

### 4.4 Volver a la app

Debes configurar una de estas estrategias:

1. App Links / Universal Links.
2. Una pagina intermedia en web que abra un deep link como `jobmatch://paypal/success?...`.

La app Flutter debe recuperar `paypal_subscription_id` y llamar `sync`.

```dart
Future<Map<String, dynamic>> syncPaypalSubscription(String subscriptionId) async {
  final response = await dio.post('/payments/paypal/subscriptions/$subscriptionId/sync');
  return Map<String, dynamic>.from(response.data);
}
```

### 4.5 Cancelar suscripcion

```dart
Future<Map<String, dynamic>> cancelPaypalSubscription(String subscriptionId) async {
  final response = await dio.post(
    '/payments/paypal/subscriptions/$subscriptionId/cancel',
    data: {
      'reason': 'Cancelada por el usuario desde Flutter',
    },
  );

  return Map<String, dynamic>.from(response.data);
}
```

## 5. Desarrollo Local

Para pruebas locales:

1. Usa `PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com`.
2. Usa cuentas Sandbox de comprador y vendedor.
3. Expone el backend local con `ngrok` o similar.
4. Registra el webhook Sandbox con la URL publica de `ngrok`.

Ejemplo:

```bash
ngrok http 8000
```

Webhook:

```text
https://TU_SUBDOMINIO.ngrok-free.app/api/v1/payments/paypal/webhook
```

En React local:

- `return_url`: `http://localhost:3000/payments/paypal/success`
- `cancel_url`: `http://localhost:3000/payments/paypal/cancel`

En Flutter local:

- usa una URL intermedia publica o una ruta web de desarrollo con deep link

## 6. Eventos PayPal Recomendados

Configura al menos estos eventos en el webhook:

- `BILLING.SUBSCRIPTION.ACTIVATED`
- `BILLING.SUBSCRIPTION.CANCELLED`
- `BILLING.SUBSCRIPTION.EXPIRED`
- `BILLING.SUBSCRIPTION.SUSPENDED`
- `PAYMENT.SALE.COMPLETED`
- `PAYMENT.SALE.DENIED`

## 7. Errores Comunes

- `approve_url` nulo:
  Normalmente indica una respuesta inesperada de PayPal o un problema de configuracion del plan.

- `es_premium` sigue en `false`:
  Asegurate de llamar `sync` despues del regreso del usuario o de que el webhook este entrando correctamente.

- `GET /plans/me` no devuelve planes:
  Verifica que el usuario tenga rol `estudiante` o `empresa` y que ya corriste `POST /api/v1/payments/paypal/bootstrap`.

- El webhook no llega:
  Verifica HTTPS, DNS, proxy reverse, Nginx y que la URL apunte al backend, no al frontend.

- La app movil no reabre:
  Falta configurar app links, universal links o una pagina intermedia que redirija al deep link.

## 8. Orden Recomendado De Implementacion

1. Termina primero el flujo React web.
2. Verifica Sandbox end to end.
3. Deja funcionando el webhook.
4. Implementa la misma logica en Flutter.
5. Añade app links o deep links para el retorno movil.
6. Cambia de Sandbox a Live al final.
