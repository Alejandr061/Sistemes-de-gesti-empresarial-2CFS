# delivery_project/__manifest__.py
{
    "name": "Delivery Project",
    "summary": "Gestio empresa repartidors",
    "version": "17.0.1.0.0",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "report/delivery_report.xml",      # primero el report
        "views/delivery_views.xml",        # luego vistas (botón usa el report)
        "views/delivery_wizard_views.xml",
    ],
    "application": True,
}