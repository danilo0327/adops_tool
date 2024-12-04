import streamlit as st
import pandas as pd

def trafficking():
    st.header("Trafficking")
    # Verificar si los archivos están cargados
    if st.session_state.traffic_sheet and st.session_state.export_legacy:
        try:
            # Leer Traffic Sheet con la hoja especificada
            traffic_sheet_name = st.session_state.traffic_sheet_sheet_name
            traffic_df = pd.read_excel(
                st.session_state.traffic_sheet,
                sheet_name=traffic_sheet_name if traffic_sheet_name else 0,
                engine="xlrd" if st.session_state.traffic_sheet.name.endswith(".xls") else "openpyxl"
            )

            # Leer Export Legacy con la hoja especificada
            export_sheet_name = st.session_state.export_legacy_sheet_name
            export_df = pd.read_excel(
                st.session_state.export_legacy,
                sheet_name=export_sheet_name if export_sheet_name else 0,
                engine="xlrd" if st.session_state.export_legacy.name.endswith(".xls") else "openpyxl"
            )

            # Normalizar el formato de las columnas "Start Date" y "End Date"
            date_columns = ["Start Date", "End Date"]

            # Formatear las fechas del Traffic Sheet
            for col in date_columns:
                if col in traffic_df.columns:
                    traffic_df[col] = pd.to_datetime(traffic_df[col], errors="coerce").dt.strftime("%m/%d/%Y")

            # Formatear las fechas del Export Legacy
            for col in date_columns:
                if col in export_df.columns:
                    export_df[col] = pd.to_datetime(export_df[col], errors="coerce").dt.strftime("%m/%d/%Y")

            # Configurar pandas para mostrar todas las filas y columnas
            pd.set_option("display.max_columns", None)
            pd.set_option("display.max_rows", None)

            # Mostrar un resumen de los datos
            st.write("Resumen de Traffic Sheet:")
            st.dataframe(traffic_df)

            st.write("Resumen de Export Legacy:")
            st.dataframe(export_df)

            # Agregar lógica específica del módulo
            st.write("Aquí puedes realizar el QA de placements.")
        except Exception as e:
            st.error(f"Error al cargar los archivos: {e}")
    else:
        st.error("Por favor, carga los archivos Traffic Sheet y Export Legacy desde el Home antes de continuar.")

    # Boton de regreso al home
    if st.button("Volver al Home", key="trafficking_home"):
        st.session_state.current_page = "Home"