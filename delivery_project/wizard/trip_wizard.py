# delivery_project/wizard/trip_wizard.py
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DeliveryTripWizard(models.TransientModel):
    _name = "delivery.trip.wizard"
    _description = "Wizard crear repartiment"

    employee_id = fields.Many2one(
        "delivery.employee",
        string="Repartidor",
        required=True,
    )  # relacion employee
    vehicle_id = fields.Many2one(
        "delivery.vehicle",
        string="Vehicle",
        required=True,
    )  # relacion vehicle
    sender_id = fields.Many2one(
        "delivery.client",
        string="Client emissor",
        required=True,
    )  # relacion client
    receiver_name = fields.Char(string="Nom receptor", required=True)
    receiver_phone = fields.Char(string="Telefon receptor")
    receiver_address = fields.Char(string="Adreca receptor", required=True)
    distance_km = fields.Float(string="Kilometres", required=True)
    weight_kg = fields.Float(string="Pes (kg)", required=True)
    volume_m3 = fields.Float(string="Volum (m3)")
    urgency = fields.Selection(
        [
            ("organs", "Òrgans humans"),
            ("cold_food", "Aliments refrigerats"),
            ("food", "Aliments"),
            ("high", "Alta prioritat"),
            ("low", "Baixa prioritat"),
        ],
        string="Urgencia",
        required=True,
        default="high",
    )

    def action_create_trip(self):
        # crea repartiment
        self.ensure_one()
        vals = {
            "employee_id": self.employee_id.id,
            "vehicle_id": self.vehicle_id.id,
            "sender_id": self.sender_id.id,
            "receiver_name": self.receiver_name,
            "receiver_phone": self.receiver_phone,
            "receiver_address": self.receiver_address,
            "distance_km": self.distance_km,
            "weight_kg": self.weight_kg,
            "volume_m3": self.volume_m3,
            "urgency": self.urgency,
        }
        trip = self.env["delivery.trip"].create(vals)
        return {
            "type": "ir.actions.act_window",
            "res_model": "delivery.trip",
            "view_mode": "form",
            "res_id": trip.id,
            "target": "current",
        }