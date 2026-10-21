# index.html

PHENOM CELL / Split Run: simulación local de células que intercambian genes digitales sin destruirse. Abre `index.html` en un navegador moderno; no requiere compilación ni servicios externos.

## Controles

- Pausar / Continuar detiene o reanuda el movimiento.
- Reiniciar y cambiar la cantidad crean una población nueva, manteniendo la velocidad y el estado de pausa.
- Velocidad ajusta el avance de la simulación entre 0.2× y 3×.
- Tocar o hacer clic cerca de una célula muestra sus genes. Tocar un espacio vacío limpia la selección.
- Arrastrar desplaza la cámara; Centrar vista recupera la posición inicial.
- Prueba de velocidad ejecuta 300 pasos por lotes sobre una copia independiente. El resultado mide tiempo de cálculo local, excluye dibujo y esperas, y no altera la población visible.

Las colisiones conservan los objetos, identificadores y cantidad de células; solo modifican posición, velocidad, genes y memoria. No hay absorción ni eliminación por colisión.

## Pruebas

Requisitos: Python 3, Playwright y Chromium. Instala Playwright en un entorno virtual (`python -m pip install playwright`). Por defecto se utiliza `/usr/bin/chromium`; para otra instalación establece `CHROMIUM_PATH` con la ruta al ejecutable.

```sh
python -m unittest discover -s tests -v
```

Se añadieron siete pruebas de navegador: pausa/continuación/velocidad; cantidades y reinicio; superposición exacta e intercambio; conservación de 2000 identidades y límites durante 300 pasos; benchmark independiente y cooperativo; selección/arrastre/cancelación/centrado; diseño adaptable y entrada táctil.

Validación realizada con Chromium: 7/7 pruebas aprobadas, sin errores JavaScript capturados en las páginas principales. Dimensiones comprobadas: 320×568, 390×844, 844×390 y 1440×900. Revisadas capturas de móvil y escritorio. La entrada táctil y densidad de pantalla se emulan; queda pendiente validar Safari en un iPhone físico y medir rendimiento en ese dispositivo. No existían pruebas ni configuración de CI en el repositorio original.

## Integración

Revisar la solicitud de cambios y su pestaña Files changed. Fusionarla en `main` con Merge pull request cuando se apruebe. El código original permanece en el historial de Git; la rama principal no cambia hasta fusionar. Si GitHub Pages publica desde `main`, comprobar el despliegue después de la fusión.
