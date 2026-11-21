# Diseñador de carruseles — Coldwell Banker Zetaté

Agente diseñador gráfico que produce carruseles de Instagram para Coldwell Banker Zetaté
(Punta del Este). **No publica nada:** deja todo en la carpeta de Drive "Listo para publicar"
y desde ahí el agente community manager lo programa.

Las instrucciones completas del agente están en [`CLAUDE.md`](CLAUDE.md).

## Flujo

```
Drive (carpeta de la propiedad)  ──┐
Tema (Mateo / agente estratega)  ──┤
                                   ▼
                       Agente diseñador
         (selección de fotos, ajuste de luz, copy, Canva)
                                   ▼
                   Vista previa → OK de Mateo
                                   ▼
               Drive: "Listo para publicar"
                                   ▼
                  Agente community manager
```

## Estructura

| Ruta | Para qué sirve |
|---|---|
| `CLAUDE.md` | Rol, los dos modos de trabajo, las reglas y el checklist |
| `copy/plantilla-propiedad.md` | Estructura y tono del copy de una propiedad |
| `copy/plantilla-educativo.md` | Estructura de los slides y del copy educativo |
| `copy/hashtags.md` | Banco de hashtags locales |
| `scripts/ajuste_fotos.py` | Ajuste suave de luz y export 1080x1350 numerado |

## Ajuste de fotos

Requisitos: Python 3.10+, `pip install -r requirements.txt`.

```bash
python scripts/ajuste_fotos.py fotos_elegidas/ salida/ --orden orden.txt --fuerza 0.5
```

`orden.txt` lleva una foto por línea, en el orden del carrusel. Para anclar el recorte
arriba o abajo, agregá `|top` o `|bottom`:

```
fachada.jpg
living.jpg
cocina.jpg|top
...
```

El script solo corrige balance de blancos, exposición y contraste, con límites que lo
mantienen suave. Para llegar a 4:5 **recorta, nunca estira**. Revisá siempre el resultado
antes de mostrarle la vista previa a Mateo.
