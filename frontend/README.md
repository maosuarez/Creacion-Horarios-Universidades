# Generador de Horarios Universitarios

Este es un proyecto open-source diseñado para ayudar a los estudiantes universitarios a crear, visualizar y gestionar sus horarios académicos de manera eficiente. La aplicación permite a los usuarios buscar asignaturas, seleccionar las comisiones deseadas y generar automáticamente todas las combinaciones de horarios posibles, evitando conflictos.

![Captura de pantalla de la aplicación](https://via.placeholder.com/800x450.png?text=Visualización+del+Generador+de+Horarios)

## 🎯 Sobre el Proyecto

El objetivo principal de este proyecto es simplificar el tedioso proceso de inscripción de materias que enfrentan los estudiantes cada semestre. En lugar de probar manualmente combinaciones en hojas de cálculo o papel, esta herramienta automatiza la búsqueda de horarios compatibles, permitiendo a los usuarios enfocarse en elegir la opción que mejor se adapte a sus necesidades.

### ✨ Características Principales

- **Búsqueda Inteligente de Asignaturas:** Filtra y busca asignaturas por nombre, código o departamento.
- **Selección de Comisiones:** Elige las comisiones (teóricas, prácticas, laboratorios) que deseas cursar.
- **Generador Automático de Horarios:** Crea todas las combinaciones de horarios posibles sin solapamientos.
- **Visualización Clara:** Muestra los horarios generados en una parrilla semanal fácil de leer.
- **Gestión de Perfil:** Guarda tus preferencias y horarios generados (funcionalidad en desarrollo).
- **Diseño Responsivo:** Accede y utiliza la aplicación desde cualquier dispositivo, ya sea de escritorio o móvil.

## 🛠️ Construido Con

Este proyecto utiliza un stack de tecnologías moderno, enfocado en el rendimiento y la experiencia de usuario.

- **[Next.js](https://nextjs.org/)** - Framework de React para producción (SSR, SSG).
- **[React](https://react.dev/)** - Librería para construir interfaces de usuario.
- **[TypeScript](https://www.typescriptlang.org/)** - Superset de JavaScript que añade tipado estático.
- **[Tailwind CSS](https://tailwindcss.com/)** - Framework de CSS "utility-first" para un diseño rápido y personalizado.
- **[Shadcn/UI](https://ui.shadcn.com/)** - Componentes de UI reutilizables y accesibles.
- **[React Hook Form](https://react-hook-form.com/)** - Manejo de formularios performante y flexible.
- **[Zod](https://zod.dev/)** - Validación de esquemas y tipos.

Para una lista más detallada, consulta el archivo [`docs/TECHNOLOGIES.md`](./docs/TECHNOLOGIES.md).

## 🚀 Cómo Empezar

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### Prerrequisitos

Asegúrate de tener instalado [Node.js](https://nodejs.org/) (versión 22.x o superior) y un gestor de paquetes como `npm` o `yarn`.

```bash
node --version
npm --version
```

### Instalación

1.  Clona el repositorio:
    ```bash
    git clone https://URL_DEL_REPOSITORIO.git
    cd nextjs-crear-horarios
    ```
2.  Instala las dependencias del proyecto:
    ```bash
    npm install
    ```

### Ejecución

1.  Inicia el servidor de desarrollo:
    ```bash
    npm run dev
    ```
2.  Abre tu navegador y visita [http://localhost:3000](http://localhost:3000).

## 🚢 Despliegue

La forma más sencilla de desplegar esta aplicación Next.js es a través de la [plataforma Vercel](https://vercel.com/new), de los creadores de Next.js.

Para más detalles sobre el proceso de build y despliegue, consulta el archivo [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md).

## 📂 Estructura del Proyecto

La arquitectura general del proyecto sigue las convenciones de Next.js App Router.

-   `src/app/`: Contiene las rutas, páginas y layouts de la aplicación.
-   `src/components/`: Almacena todos los componentes de React reutilizables.
-   `src/lib/`: Módulos auxiliares, como clientes de API y funciones de utilidad.
-   `src/styles/`: Archivos de estilos globales.

Para una explicación más profunda de la arquitectura, visita el archivo [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE.txt` para más información.