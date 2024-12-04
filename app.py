# This is the initial prototype for the tool
import streamlit as st
from modules.placements_qa import placements_qa
from modules.creatives_qa import creatives_qa
from modules.existing_urls import existing_urls
from modules.trafficking import trafficking

# Función para manejar navegación
def main():
    # Titulo de la aplicación
    st.title("AdOps App")

    # Inicializar estado si no esta definido
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    if "traffic_sheet" not in st.session_state:
        st.session_state.traffic_sheet = None
    if "traffic_sheet_sheet_name" not in st.session_state:
        st.session_state.traffic_sheet_sheet_name = None
    if "export_legacy" not in st.session_state:
        st.session_state.export_legacy = None
    if "export_legacy_sheet_name" not in st.session_state:
        st.session_state.export_legacy_sheet_name = None

    # Navegación basada en la página actual
    if st.session_state.current_page == "Home":
        home()
    elif st.session_state.current_page == "Placements QA":
        placements_qa()
    elif st.session_state.current_page == "Creatives QA":
        creatives_qa()
    elif st.session_state.current_page == "Existing URLs":
        existing_urls()
    elif st.session_state.current_page == "Trafficking":
        trafficking()

# Página Home con botones para navegar
def home():
    st.header("Bienvenido a AdOps App")
    st.write("Carga los archivos necesarios para trabajar en los módulos:")

    # Cargar Traffic Sheet
    traffic_file = st.file_uploader("Cargar Traffic Sheet", type=["xls", "xlsx"], key="traffic_file")
    traffic_sheet_name = st.text_input("Nombre de la hoja para Traffic Sheet (dejar en blanco para usar la predeterminada)", key="traffic_sheet_name")

    if traffic_file:
        st.session_state.traffic_sheet = traffic_file
        st.session_state.traffic_sheet_sheet_name = traffic_sheet_name if traffic_sheet_name.strip() else None
        st.success("Traffic Sheet cargado con éxito.")

    # Cargar Export Legacy
    export_file = st.file_uploader("Cargar Export Legacy", type=["xls", "xlsx"], key="export_file")
    export_sheet_name = st.text_input("Nombre de la hoja para Export Legacy (dejar en blanco para usar la predeterminada)", key="export_sheet_name")

    if export_file:
        st.session_state.export_legacy = export_file
        st.session_state.export_legacy_sheet_name = export_sheet_name if export_sheet_name.strip() else None
        st.success("Export Legacy cargado con éxito.")

    # Crear botones únicos para cada módulo
    if st.button("Placements QA", key="home_to_placements"):
        st.session_state.current_page = "Placements QA"
    if st.button("Creatives QA", key="home_to_creatives"):
        st.session_state.current_page = "Creatives QA"
    if st.button("Existing URLs", key="home_to_existing_urls"):
        st.session_state.current_page = "Existing URLs"
    if st.button("Trafficking", key="home_to_trafficking"):
        st.session_state.current_page = "Trafficking"

# Llamar la función principal
if __name__ == "__main__":
    main()