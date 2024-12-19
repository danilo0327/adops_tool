import streamlit as st
import pandas as pd

def existing_urls():
    st.header("Existing URLs")
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
            st.write("Aquí puedes realizar el QA de URLs.")

            # Mostrar botón para comenzar QA de creatives
            if st.button("Start URLs QA") or st.session_state.get("url_qa_started", False):
                st.session_state.url_qa_started = True  # Activar estado del botón
                # Obtener los valores únicos de la columna "Landing Page" en TS 
                # y la columna "Creative Click-Through URL" en el export
                traffic_unique_url = traffic_df["Landing Page"].nunique()
                export_unique_url = export_df["Creative Click-Through URL"].nunique()

                # Crear una tabla con los resultados
                data = {
                    "Archivo": ["Traffic Sheet", "Legacy Export"],
                    "No de URLs": [traffic_unique_url, export_unique_url]
                }

                result_df = pd.DataFrame(data)

                # Mostrar la tabla con los resultados
                st.write("Resumen de URLs por archivo:")
                st.dataframe(result_df)

                # Filtrar los placements que son "New Placement" en el Traffic Sheet
                new_placement_df = traffic_df[traffic_df["Status"] == "New Placement"]

                # Contar cuántos URLs (unicas) tienen el estado "New Placement"
                new_url_count = new_placement_df["Landing Page"].nunique()

                # Mostrar mensaje con la cantidad de URLs a traficar
                st.write(f"La cantidad de URLs a traficar son: {new_url_count}")

                # Obtener los valores únicos de la columna "Landing Page" donde "Status" es "New Placement"
                url_to_traffic = new_placement_df["Landing Page"].unique()

                # Crear la tabla con las URLs a traficar
                traffic_data = {
                    "URLs To Traffic": url_to_traffic
                }

                traffic_result_df = pd.DataFrame(traffic_data)

                # Mostrar la tabla con las URLs a traficar
                st.write("URLs a traficar:")
                st.dataframe(traffic_result_df)

                # Mostrar botón para verificar si las URLs están cargados en CM360
                if st.button("URLs uploaded on CM360?", key="url_cretives_check") or st.session_state.get("url_creatives_checked", False):
                    st.session_state.url_creatives_checked = True  # Activar estado del segundo botón
                    # Verificar si todas las URLs a traficar están en el archivo Export Legacy
                    export_url = export_df["Creative Click-Through URL"].unique()
                    all_url_in_export = all(
                        url in export_url for url in url_to_traffic
                    )

                    # Mostrar el resultado de la verificación
                    if all_url_in_export:
                        st.success("Yes, all URLs were uploaded on CM360.")
                    else:
                        st.error("No, not all URLs were uploaded on CM360. Please reach to Planning Team")

                    # Mostrar las URLs a traficar que no están en el archivo Export Legacy
                    missing_url = [
                        url for url in url_to_traffic if url not in export_url
                    ]

                    if missing_url:
                        st.warning(f"The following URLs need to be uploaded on CM360:")
                        missing_data = {"Missing URLs": missing_url}
                        missing_df = pd.DataFrame(missing_data)
                        st.dataframe(missing_df)
                    else:
                        st.success("All the URLs are on CM360, you can continue!.")

        except Exception as e:
            st.error(f"Error al cargar los archivos: {e}")
    else:
        st.error("Por favor, carga los archivos Traffic Sheet y Export Legacy desde el Home antes de continuar.")

    # Boton de regreso al home
    if st.button("Volver al Home", key="existing_urls_home"):
        st.session_state.current_page = "Home"