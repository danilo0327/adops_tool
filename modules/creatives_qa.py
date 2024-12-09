import streamlit as st
import pandas as pd

def creatives_qa():
    st.header("Creatives QA")

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
            st.write("Aquí puedes realizar el QA de Creatives.")

            # Mostrar botón para comenzar QA de creatives
            if st.button("Start Creatives QA") or st.session_state.get("creatives_qa_started", False):
                st.session_state.creatives_qa_started = True  # Activar estado del botón
                # Obtener los valores únicos de la columna "creatives Name" en ambos archivos
                traffic_unique_creatives = traffic_df["Creative Name"].nunique()
                export_unique_creatives = export_df["Creative Name"].nunique()

                # Crear una tabla con los resultados
                data = {
                    "Archivo": ["Traffic Sheet", "Legacy Export"],
                    "No de creatives": [traffic_unique_creatives, export_unique_creatives]
                }

                result_df = pd.DataFrame(data)

                # Mostrar la tabla con los resultados
                st.write("Resumen de creatives por archivo:")
                st.dataframe(result_df)

                # Filtrar los placements que son "New Placement" en el Traffic Sheet
                new_placement_df = traffic_df[traffic_df["Status"] == "New Placement"]

                # Contar cuántos creativos (unicos) tienen el estado "New Placement"
                new_creatives_count = new_placement_df["Creative Name"].nunique()

                # Mostrar mensaje con la cantidad de creatives a traficar
                st.write(f"La cantidad de creatives a traficar son: {new_creatives_count}")

                # Obtener los valores únicos de la columna "Creative Name" donde "Status" es "New Placement"
                creatives_to_traffic = new_placement_df["Creative Name"].unique()

                # Crear la tabla con los creatives a traficar
                traffic_data = {
                    "Creatives To Traffic": creatives_to_traffic
                }

                traffic_result_df = pd.DataFrame(traffic_data)

                # Mostrar la tabla con los creatives a traficar
                st.write("Creativos a traficar:")
                st.dataframe(traffic_result_df)

                # Mostrar botón para verificar si los creatives están cargados en CM360
                if st.button("Creatives uploaded on CM360?", key="cm360_cretives_check") or st.session_state.get("cm360_creatives_checked", False):
                    st.session_state.cm360_creatives_checked = True  # Activar estado del segundo botón
                    # Verificar si todos los creatives a traficar están en el archivo Export Legacy
                    export_creatives = export_df["Creative Name"].unique()
                    all_crearives_in_export = all(
                        creative in export_creatives for creative in creatives_to_traffic
                    )

                    # Mostrar el resultado de la verificación
                    if all_crearives_in_export:
                        st.success("Yes, all creatives were uploaded on CM360.")
                    else:
                        st.error("No, not all creatives were uploaded on CM360. Please reach to Planning Team")

                    # Mostrar los creatives a traficar que no están en el archivo Export Legacy
                    missing_creatives = [
                        creative for creative in creatives_to_traffic if creative not in export_creatives
                    ]

                    if missing_creatives:
                        st.warning(f"The following creatives need to be uploaded on CM360:")
                        missing_data = {"Missing creatives": missing_creatives}
                        missing_df = pd.DataFrame(missing_data)
                        st.dataframe(missing_df)
                    else:
                        st.success("All the creatives are on CM360, you can continue!.")

                # Inicializar la variable antes del bloque de botón
                contains_1x1 = None
                # Botón para verificar dimensiones
                if st.button("Check Dimensions", key="dimensions_check"):
                    # Verificar si algún valor contiene "1x1"
                    contains_1x1 = [
                        creative for creative in creatives_to_traffic if "1x1" in str(creative)
                ]
                    
                    # Mostrar los resultados
                    if contains_1x1:
                        st.success("The following creatives contain '1x1':")
                        contains_1x1_df = pd.DataFrame({"Creatives with '1x1'": contains_1x1})
                        st.dataframe(contains_1x1_df)
                    else:
                        st.warning("None of the creatives contain '1x1'. You can't continue.")

        except Exception as e:
            st.error(f"Error al cargar los archivos: {e}")
    else:
        st.error("Por favor, carga los archivos Traffic Sheet y Export Legacy desde el Home antes de continuar.")

    # Boton de regreso al home
    if st.button("Volver al Home", key="creatives_qa_home"):
        st.session_state.current_page = "Home"