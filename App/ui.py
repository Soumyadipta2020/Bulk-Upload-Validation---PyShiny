from shiny import ui


# Application UI
# - `app_ui` defines the page layout, file upload controls, download
#   template buttons, and placeholders for assignment/validation cards.
#   This is passed to `App` together with `server` to run the app.
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("File Upload"),
        ui.div(
            ui.h5("Download Sample Templates"),
            ui.download_button(
                "download_attrition",
                "Download Attrition Template",
                class_="btn-outline-primary btn-sm me-2 mb-2",
            ),
            ui.download_button(
                "download_recruitment",
                "Download Recruitment Template",
                class_="btn-outline-primary btn-sm me-2 mb-2",
            ),
            ui.download_button(
                "download_fte",
                "Download FTE Template",
                class_="btn-outline-primary btn-sm me-2 mb-2",
            ),
            ui.download_button(
                "download_fte_wide",
                "Download FTE Wide Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            ui.download_button(
                "download_patch_mapping",
                "Download Patch Mapping Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            ui.download_button(
                "download_demand",
                "Download Demand Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            ui.download_button(
                "download_resource_allocation",
                "Download Resource Allocation Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            class_="mb-3",
        ),
        ui.hr(),
        ui.input_file(
            "uploaded_files",
            "Upload Files (CSV or Excel)",
            accept=[".csv", ".xlsx", ".xls", ".xlsm"],
            multiple=True,
        ),
        ui.br(),
        ui.output_ui("file_assignment_ui"),
    ),
    ui.card(ui.card_header("File Assignment"), ui.output_ui("file_assignment_display")),
    ui.br(),
    ui.card(ui.card_header("File Validation Results"), ui.output_ui("validation_results")),
    ui.br(),
    ui.card(ui.card_header("Uploaded Files Preview"), ui.output_ui("file_previews")),
)
