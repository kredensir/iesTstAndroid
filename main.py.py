"""Cruz Robinson Boris 
Cotizador de PC - Local de informatica (Flet).
Archivo: 1-tp-resuelto.py  (entregable: cotizador_flet_apellido.py)

Estructura modular:
  1. Tablas de precios / potencias (datos)
  2. Declaracion de componentes de la interfaz
  3. Funciones controladoras de eventos (on_click + page.update)
  4. Ensamblado final de la pagina (formulario | resultados)
"""
import flet as ft

# ------------------------------------------------------------------
# 1. DATOS / TABLAS COMERCIALES
# ------------------------------------------------------------------
PROCESADORES = {
    "Ryzen 5 5600": {"precio": 180000, "potencia": 65},
    "Intel i5-12400F": {"precio": 200000, "potencia": 117},
    "Ryzen 7 7800X3D": {"precio": 350000, "potencia": 120},
    "Intel i7-13700K": {"precio": 420000, "potencia": 125},
}

RAM_PRECIOS = {8: 45000,
               16: 85000,
               32: 160000,
               64: 300000
               }
RAM_OPCIONES = [8, 16, 32, 64]  # indices 0..3 del Slider

PRECIO_GPU = 450000
POTENCIA_GPU = 200
PRECIO_SSD = 90000
PRECIO_ARMADO = 25000

COSTO_ENVIO = 15000
BASE_SISTEMA_W = 100      # margen base (mother, coolers, etc.)
FACTOR_SEGURIDAD = 1.25   # +25% tolerancia
UMBRAL_FUENTE_W = 450     # si consumo estimado > 450 -> 650W o superior


def main(page: ft.Page):
    page.title = "Local de informática - Cotizador de PC"
    page.window.width = 1000
    page.window.height = 750
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # ------------------------------------------------------------------
    # 2. DECLARACION DE COMPONENTES
    # ------------------------------------------------------------------
    # --- Entrada: cliente ---
    txt_nombre = ft.TextField(label="Nombre del cliente", hint_text="Ingrese su nombre")
    txt_presupuesto = ft.TextField(
        label="Presupuesto tope ($)",
        hint_text="Ej: 800000",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    # --- Entrada: procesador (Dropdown) ---
    dd_procesador = ft.Dropdown(
        label="Procesador",
        hint_text="Seleccione un procesador",
        options=[ft.dropdown.Option(nombre) for nombre in PROCESADORES],
        value=None,
    )

    # --- Entrada: RAM (Slider discreto 8/16/32/64) ---
    # Se usa indice 0..3 con divisions=3 para lograr solo 4 saltos exactos.
    txt_ram_valor = ft.Text("RAM seleccionada: 8 GB ($45.000)", weight=ft.FontWeight.BOLD)

    def on_ram_change(e):
        gb = RAM_OPCIONES[int(slider_ram.value)]
        txt_ram_valor.value = f"RAM seleccionada: {gb} GB (${RAM_PRECIOS[gb]:,})".replace(",", ".")
        page.update()

    slider_ram = ft.Slider(
        label="{value} GB",
        min=0, max=3, value=0, divisions=3,
        width=300,
        on_change=on_ram_change,
    )

    # --- Entrada: adicionales (Checkboxes) ---
    chk_gpu = ft.Checkbox(label=f"Placa de video dedicada (+ ${PRECIO_GPU:,})".replace(",", "."), value=False)
    chk_ssd = ft.Checkbox(label=f"SSD extra 1TB (+ ${PRECIO_SSD:,})".replace(",", "."), value=False)
    chk_armado = ft.Checkbox(label=f"Servicio de armado (+ ${PRECIO_ARMADO:,})".replace(",", "."), value=False)

    # --- Entrada: entrega (Switch) ---
    switch_envio = ft.Switch(
        label=f"Envío a domicilio (+ ${COSTO_ENVIO:,}) / Retiro en tienda".replace(",", "."),
        value=False,
    )

    # --- Entrada: medio de pago (RadioGroup) ---
    radio_pago = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="efectivo", label="Efectivo / Transferencia (10% descuento)"),
            ft.Radio(value="debito", label="Tarjeta de Débito (precio de lista)"),
            ft.Radio(value="credito", label="Tarjeta de Crédito 3 cuotas (15% recargo)"),
        ]),
        value=None,  # sin seleccion inicial -> obliga a validar
    )

    # --- Salida: resultados (cuadros de texto) ---
    res_subtotal = ft.Text("Subtotal: —")
    res_pago = ft.Text("Total a pagar: —", weight=ft.FontWeight.BOLD, size=16)
    res_cuota = ft.Text("Cuota: —")
    res_consumo = ft.Text("Consumo estimado: —")
    res_fuente = ft.Text("Fuente recomendada: —")
    res_presupuesto = ft.Text("Presupuesto: —", weight=ft.FontWeight.BOLD)
    lbl_alerta = ft.Text("", color=ft.Colors.RED, weight=ft.FontWeight.BOLD)

    # ------------------------------------------------------------------
    # 3. FUNCIONES CONTROLADORAS DE EVENTOS
    # ------------------------------------------------------------------
    def fmt(valor: float) -> str:
        return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def calcular(e):
        # Validacion: procesador y forma de pago obligatorios
        if not dd_procesador.value:
            lbl_alerta.value = "⚠ Seleccione un procesador antes de cotizar."
            page.update()
            return
        if not radio_pago.value:
            lbl_alerta.value = "⚠ Seleccione un medio de pago antes de cotizar."
            page.update()
            return

        # Lectura protegida del presupuesto (ValueError si vacio / no numerico)
        try:
            presupuesto = float(txt_presupuesto.value.strip().replace(".", "").replace(",", "."))
        except (ValueError, AttributeError):
            lbl_alerta.value = "⚠ Presupuesto inválido: ingrese un número (ej: 800000)."
            page.update()
            return

        lbl_alerta.value = ""  # limpio alerta previa

        # --- Subtotal: procesador + RAM + adicionales + envio ---
        cpu = PROCESADORES[dd_procesador.value]
        gb_ram = RAM_OPCIONES[int(slider_ram.value)]
        subtotal = cpu["precio"] + RAM_PRECIOS[gb_ram]
        if chk_gpu.value:
            subtotal += PRECIO_GPU
        if chk_ssd.value:
            subtotal += PRECIO_SSD
        if chk_armado.value:
            subtotal += PRECIO_ARMADO
        if switch_envio.value:
            subtotal += COSTO_ENVIO

        # --- Politica comercial segun RadioGroup ---
        medio = radio_pago.value
        if medio == "efectivo":
            total = subtotal * 0.90
            detalle_pago = "Efectivo/Transferencia: 10% descuento aplicado."
            cuota_txt = "Cuota: no aplica (pago único)."
        elif medio == "debito":
            total = subtotal
            detalle_pago = "Débito: precio de lista (sin cambios)."
            cuota_txt = "Cuota: no aplica (pago único)."
        else:  # credito
            total = subtotal * 1.15
            cuota = total / 3
            detalle_pago = "Crédito 3 cuotas: 15% recargo aplicado."
            cuota_txt = f"Valor de cada cuota: {fmt(cuota)} (3 x {fmt(cuota)})"

        # --- Consumo energetico + fuente recomendada ---
        potencia = cpu["potencia"] + BASE_SISTEMA_W
        if chk_gpu.value:
            potencia += POTENCIA_GPU
        consumo = potencia * FACTOR_SEGURIDAD
        if consumo > UMBRAL_FUENTE_W:
            fuente = "Fuente de 650W o superior"
        else:
            fuente = "Fuente convencional de 500W"

        # --- Comparacion con presupuesto tope ---
        if total <= presupuesto:
            saldo = presupuesto - total
            nombre = txt_nombre.value.strip() or "Cliente"
            msg = f"✅ Aprobado, {nombre}: dentro del presupuesto. Saldo a favor: {fmt(saldo)}."
            res_presupuesto.color = ft.Colors.GREEN
        else:
            faltante = total - presupuesto
            msg = f"⚠ Excede el presupuesto. Faltan {fmt(faltante)} para cubrir el total."
            res_presupuesto.color = ft.Colors.RED

        # --- Volcar resultados ---
        res_subtotal.value = f"Subtotal componentes: {fmt(subtotal)}"
        res_pago.value = f"Total a pagar: {fmt(total)} ({detalle_pago})"
        res_cuota.value = cuota_txt
        res_consumo.value = f"Consumo estimado: {consumo:.1f} W (CPU {cpu['potencia']}W + base {BASE_SISTEMA_W}W" + \
            (f" + GPU {POTENCIA_GPU}W" if chk_gpu.value else "") + f") x 1.25"
        res_fuente.value = f"Fuente recomendada: {fuente}"
        res_presupuesto.value = msg
        page.update()

    def limpiar(e):
        txt_nombre.value = ""
        txt_presupuesto.value = ""
        dd_procesador.value = None
        slider_ram.value = 0
        on_ram_change(None)
        chk_gpu.value = False
        chk_ssd.value = False
        chk_armado.value = False
        switch_envio.value = False
        radio_pago.value = None
        lbl_alerta.value = ""
        for r in (res_subtotal, res_pago, res_cuota, res_consumo, res_fuente, res_presupuesto):
            r.value = r.value.split(":")[0] + ": —" if ":" in r.value else "—"
        res_pago.value = "Total a pagar: —"
        res_presupuesto.value = "Presupuesto: —"
        res_presupuesto.color = None
        page.update()

    btn_calcular = ft.Button("Calcular cotización", on_click=calcular)
    btn_limpiar = ft.Button("Limpiar", on_click=limpiar)

    # ------------------------------------------------------------------
    # 4. ENSAMBLADO FINAL (formulario | resultados)
    # ------------------------------------------------------------------
    formulario = ft.Column(
        [
            ft.Text("1) Datos del cliente", weight=ft.FontWeight.BOLD, size=16),
            txt_nombre,
            txt_presupuesto,
            ft.Divider(),
            ft.Text("2) Componentes", weight=ft.FontWeight.BOLD, size=16),
            dd_procesador,
            ft.Text("Memoria RAM (saltos de 8 / 16 / 32 / 64 GB):"),
            slider_ram,
            txt_ram_valor,
            chk_gpu,
            chk_ssd,
            chk_armado,
            switch_envio,
            ft.Divider(),
            ft.Text("3) Medio de pago", weight=ft.FontWeight.BOLD, size=16),
            radio_pago,
            ft.Divider(),
            ft.Row([btn_calcular, btn_limpiar]),
            lbl_alerta,
        ],
        width=450,
        scroll=ft.ScrollMode.AUTO,
    )

    resultados = ft.Column(
        [
            ft.Text("Resultados de la cotización", weight=ft.FontWeight.BOLD, size=16),
            res_subtotal,
            res_pago,
            res_cuota,
            ft.Divider(),
            res_consumo,
            res_fuente,
            ft.Divider(),
            res_presupuesto,
        ],
        width=450,
        scroll=ft.ScrollMode.AUTO,
    )

    page.add(
        ft.Text("Cotizador - Local de informática", size=22, weight=ft.FontWeight.BOLD),
        ft.Text("Complete el formulario y presione «Calcular cotización»."),
        ft.Row(
            [formulario, ft.VerticalDivider(width=1), resultados],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )

ft.run(main)