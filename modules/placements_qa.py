import streamlit as st
import pandas as pd

def placements_qa():
    st.header("Placements QA")
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

            # Mostrar botón para comenzar QA de placements
            if st.button("Start Placement QA") or st.session_state.get("placements_qa_started", False):
                st.session_state.placements_qa_started = True  # Activar estado del botón
                # Obtener los valores únicos de la columna "Placement Name" en ambos archivos
                traffic_unique_placements = traffic_df["Placement Name"].nunique()
                export_unique_placements = export_df["Placement Name"].nunique()

                # Crear una tabla con los resultados
                data = {
                    "Archivo": ["Traffic Sheet", "Legacy Export"],
                    "No de placements": [traffic_unique_placements, export_unique_placements]
                }

                result_df = pd.DataFrame(data)

                # Mostrar la tabla con los resultados
                st.write("Resumen de placements por archivo:")
                st.dataframe(result_df)

                 # Filtrar los placements que son "New Placement" en el Traffic Sheet
                new_placement_df = traffic_df[traffic_df["Status"] == "New Placement"]

                # Contar cuántos placements tienen el estado "New Placement"
                new_placements_count = new_placement_df["Placement Name"].nunique()

                # Mostrar mensaje con la cantidad de placements a traficar
                st.write(f"La cantidad de placements a traficar son: {new_placements_count}")

                # Obtener los valores únicos de la columna "Placement Name" donde "Status" es "New Placement"
                placements_to_traffic = new_placement_df["Placement Name"].unique()

                # Crear la tabla con los placements a traficar
                traffic_data = {
                    "Placements To Traffic": placements_to_traffic
                }

                traffic_result_df = pd.DataFrame(traffic_data)

                # Mostrar la tabla con los placements a traficar
                st.write("Placements a traficar:")
                st.dataframe(traffic_result_df)

                # Mostrar botón para verificar si los placements están cargados en CM360
                if st.button("Placements uploaded on CM360?", key="cm360_check") or st.session_state.get("cm360_checked", False):
                    st.session_state.cm360_checked = True  # Activar estado del segundo botón
                    # Verificar si todos los placements a traficar están en el archivo Export Legacy
                    export_placements = export_df["Placement Name"].unique()
                    all_placements_in_export = all(
                        placement in export_placements for placement in placements_to_traffic
                    )

                    # Mostrar el resultado de la verificación
                    if all_placements_in_export:
                        st.success("Yes, all placements were uploaded on CM360.")
                    else:
                        st.error("No, not all placements were uploaded on CM360. Please reach to Planning Team")

                    # Mostrar los placements a traficar que no están en el archivo Export Legacy
                    missing_placements = [
                        placement for placement in placements_to_traffic if placement not in export_placements
                    ]

                    if missing_placements:
                        st.warning(f"The following placements need to be uploaded on CM360:")
                        missing_data = {"Missing Placements": missing_placements}
                        missing_df = pd.DataFrame(missing_data)
                        st.dataframe(missing_df)
                    else:
                        st.success("All the placements are on CM360, you can continue!.")

                # Botón para verificar fechas
                if st.button("Are dates matching?", key="dates_check"):
                    mismatched_dates = []

                    for placement in placements_to_traffic:
                        traffic_row = new_placement_df[new_placement_df["Placement Name"] == placement]
                        export_row = export_df[export_df["Placement Name"] == placement]

                        if not export_row.empty and not traffic_row.empty:
                            traffic_start = traffic_row["Start Date"].values[0]
                            traffic_end = traffic_row["End Date"].values[0]
                            export_start = export_row["Start Date"].values[0]
                            export_end = export_row["End Date"].values[0]

                            if traffic_start != export_start or traffic_end != export_end:
                                if export_start <= traffic_start and export_end >= traffic_end:
                                    issue = "Dates within range, but not matching"
                                else:
                                    issue = "Dates out of range"
                                mismatched_dates.append({
                                    "Placement Name": placement,
                                    "Start Date TS": traffic_start,
                                    "Start Date Export": export_start,
                                    "End Date TS": traffic_end,
                                    "End Date Export": export_end,
                                    "Status": issue
                                })
                            else:
                                mismatched_dates.append({
                                    "Placement Name": placement,
                                    "Start Date TS": traffic_start,
                                    "Start Date Export": export_start,
                                    "End Date TS": traffic_end,
                                    "End Date Export": export_end,
                                    "Status": "Dates match"
                                })

                    mismatched_df = pd.DataFrame(mismatched_dates)

                    # Mostrar resultados
                    if not mismatched_dates:
                        st.success("The dates match!")
                    else:
                        st.write("Date status for the following placements:")
                        st.dataframe(mismatched_df)

                # Botón para verificar dimensiones
                if st.button("Check Dimensions", key="dimensions_check"):
                    dimension_issues = []

                    for placement in placements_to_traffic:
                        traffic_row = new_placement_df[new_placement_df["Placement Name"] == placement]
                        export_row = export_df[export_df["Placement Name"] == placement]

                        if not export_row.empty and not traffic_row.empty:
                            traffic_dimensions = traffic_row["Dimensions"].values[0]
                            export_dimensions = export_row["Dimensions"].values[0]

                            if traffic_dimensions != export_dimensions:
                                dimension_issues.append({
                                    "Placement Name": placement,
                                    "Dimensions (Traffic Sheet)": traffic_dimensions,
                                    "Dimensions (Export)": export_dimensions
                                })

                    if not dimension_issues:
                        st.success("Dimensions are right, you can continue.")
                    else:
                        st.error("Dimensions are wrong. Please review the following placements:")
                        dimension_issues_df = pd.DataFrame(dimension_issues)
                        st.dataframe(dimension_issues_df)

        except Exception as e:
            st.error(f"Error al cargar los archivos: {e}")
    else:
        st.error("Por favor, carga los archivos Traffic Sheet y Export Legacy desde el Home antes de continuar.")

    # Boton de regreso al home
    if st.button("Volver al Home", key="placements_qa_home"):
        st.session_state.current_page = "Home"