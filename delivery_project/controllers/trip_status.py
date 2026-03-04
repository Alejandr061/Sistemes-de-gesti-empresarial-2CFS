# delivery_project/controllers/trip_status.py
from odoo import http
from odoo.http import request


class DeliveryTripStatusController(http.Controller):
    @http.route(
        "/delivery/trip_status/<string:code>",
        auth="public",
        type="json",
    )
    def trip_status(self, code, **kwargs):
        # busca repartiment
        trip = request.env["delivery.trip"].sudo().search([("name", "=", code)], limit=1)
        if not trip:
            return {"code": code, "found": False}
        # retorna estat repartiment
        return {
            "code": trip.name,
            "found": True,
            "state": trip.state,
        }