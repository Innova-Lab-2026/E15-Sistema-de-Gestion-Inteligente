[README.md](https://github.com/user-attachments/files/32451459/README.md)
# Frontend — Sistema de Gestión Inteligente (TECBA - E15)

Documentación del trabajo realizado en el frente **Frontend** para la tarea:
"Configuración base del proyecto y evaluación de mapa interactivo" (#4).

## Equipo Frontend

- Christiam Salcedo
- Ezequiel Torres
- Mauricio Chambi

## 1. Configuración base del proyecto

- **Framework:** React 
- **Herramienta de build:** Vite
- **Lenguaje:** TypeScript
- **Gestor de paquetes:** npm

### Estructura de carpetas propuesta

```
src/
├── components/    
├── pages/         
├── services/      
├── hooks/         
├── assets/        
└── App.jsx
```

## 2. Arquitectura de componentes

Se propone una arquitectura basada en componentes desacoplados de la lógica
de negocio. El componente del mapa (`MapView`) recibirá los datos por props
(coordenadas, capas, marcadores) sin conocer de dónde vienen, para que
pueda ser reutilizado por otras pantallas del sistema.

## 3. Evaluación técnica: librería para mapa interactivo

Se evaluaron dos opciones para la integración del mapa interactivo:

| Criterio | Leaflet | MapLibre GL JS |


### Decisión

**Librería elegida:** **Leaflet (`react-leaflet`)**

**Justificación:**  Se selecciona Leaflet por su rapidez de implementación para el MVP, bajo consumo de recursos y soporte nativo para visualizar coordenadas y capas territoriales oficiales de CABA.

## 4. Cómo levantar el proyecto localmente

```bash
npm install
npm run dev
```

## Estado

- [x] Estructura base del proyecto configurada
- [x] Arquitectura de componentes definida
- [x] Librería de mapa evaluada y elegida
