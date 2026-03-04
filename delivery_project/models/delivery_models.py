# delivery_project/models/delivery_models.py
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DeliveryEmployee(models.Model):
    _name = "delivery.employee"
    _description = "Delivery Employee"

    name = fields.Char(string="Nom", required=True)
    surname = fields.Char(string="Cognoms", required=True)
    dni = fields.Char(string="DNI", required=True)
    phone = fields.Char(string="Telefon")
    photo = fields.Image(string="Foto", max_width=256, max_height=256)
    has_moped_license = fields.Boolean(string="Carnet ciclomotor")
    has_van_license = fields.Boolean(string="Carnet furgoneta")
    trip_ids = fields.One2many(
        "delivery.trip",
        "employee_id",
        string="Repartiments",
    )  # relacion un empleado muchos repartos


class DeliveryVehicle(models.Model):
    _name = "delivery.vehicle"
    _description = "Delivery Vehicle"

    name = fields.Char(string="Nom", required=True)
    vehicle_type = fields.Selection(
        [
            ("bike", "Bicicleta"),
            ("moped", "Ciclomotor"),
            ("van", "Furgoneta"),
        ],
        string="Tipus vehicle",
        required=True,
    )
    plate = fields.Char(string="Matricula")
    photo = fields.Image(string="Foto", max_width=256, max_height=256)
    description = fields.Text(string="Descripcio")
    trip_ids = fields.One2many(
        "delivery.trip",
        "vehicle_id",
        string="Repartiments",
    )  # relacion un vehiculo muchos repartos


class DeliveryClient(models.Model):
    _name = "delivery.client"
    _description = "Delivery Client"

    name = fields.Char(string="Nom", required=True)
    surname = fields.Char(string="Cognoms", required=True)
    dni = fields.Char(string="DNI", required=True)
    phone = fields.Char(string="Telefon")
    trip_sender_ids = fields.One2many(
        "delivery.trip",
        "sender_id",
        string="Repartiments emesos",
    )  # relacion un cliente muchos repartos


class DeliveryTrip(models.Model):
    _name = "delivery.trip"
    _description = "Delivery Trip"
    _order = "reception_datetime desc, urgency_priority desc"

    name = fields.Char(
        string="Codi",
        required=True,
        copy=False,
        default="New",
        readonly=True,
    )

    employee_id = fields.Many2one(
        "delivery.employee",
        string="Repartidor",
        required=True,
    )  # relacion muchos repartos un empleado
    vehicle_id = fields.Many2one(
        "delivery.vehicle",
        string="Vehicle",
        required=True,
    )  # relacion muchos repartos un vehiculo
    sender_id = fields.Many2one(
        "delivery.client",
        string="Client emissor",
        required=True,
    )  # relacion muchos repartos un cliente

    receiver_name = fields.Char(string="Nom receptor", required=True)
    receiver_phone = fields.Char(string="Telefon receptor")
    receiver_address = fields.Char(string="Adreca receptor", required=True)

    reception_datetime = fields.Datetime(
        string="Data recepcio",
        required=True,
        default=fields.Datetime.now,
    )
    start_datetime = fields.Datetime(string="Eixida")
    end_datetime = fields.Datetime(string="Retorn")

    distance_km = fields.Float(string="Kilometres", required=True)
    weight_kg = fields.Float(string="Pes (kg)", required=True)
    volume_m3 = fields.Float(string="Volum (m3)")

    state = fields.Selection(
        [
            ("pending", "No ha eixit"),
            ("ongoing", "De cami"),
            ("done", "Entregada"),
        ],
        string="Estat",
        default="pending",
    )

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
    )
    urgency_priority = fields.Integer(
        string="Prioritat num",
        compute="_compute_urgency_priority",
        store=True,
    )  # usado en order

    duration_hours = fields.Float(
        string="Hores durada",
        compute="_compute_duration_hours",
        store=True,
    )  # campo computat

    @api.model
    def create(self, vals):
        # genera codi unic
        if vals.get("name", "New") == "New":
            seq = self.env["ir.sequence"].next_by_code("delivery.trip.code")
            vals["name"] = seq or _("New")
        return super().create(vals)

    @api.depends("urgency")
    def _compute_urgency_priority(self):
        # mapeja urgencia
        for trip in self:
            if trip.urgency == "organs":
                trip.urgency_priority = 5
            elif trip.urgency == "cold_food":
                trip.urgency_priority = 4
            elif trip.urgency == "food":
                trip.urgency_priority = 3
            elif trip.urgency == "high":
                trip.urgency_priority = 2
            elif trip.urgency == "low":
                trip.urgency_priority = 1
            else:
                trip.urgency_priority = 0

    @api.depends("start_datetime", "end_datetime")
    def _compute_duration_hours(self):
        # calcula durada hores
        for trip in self:
            if trip.start_datetime and trip.end_datetime:
                delta = fields.Datetime.to_datetime(trip.end_datetime) - fields.Datetime.to_datetime(
                    trip.start_datetime
                )
                trip.duration_hours = delta.total_seconds() / 3600.0
            else:
                trip.duration_hours = 0.0

    @api.constrains("employee_id", "vehicle_id")
    def _check_employee_license(self):
        # valida carnets
        for trip in self:
            if trip.vehicle_id.vehicle_type in ("moped", "van") and not (
                trip.employee_id.has_moped_license or trip.employee_id.has_van_license
            ):
                raise ValidationError(
                    _("El repartidor no te el carnet requerit per al vehicle.")
                )
            if trip.vehicle_id.vehicle_type == "van" and not trip.employee_id.has_van_license:
                raise ValidationError(_("El repartidor no te carnet de furgoneta."))

    @api.constrains("employee_id", "state")
    def _check_employee_busy(self):
        # valida empleat lliure
        for trip in self:
            if not trip.employee_id:
                continue
            domain = [
                ("id", "!=", trip.id),
                ("employee_id", "=", trip.employee_id.id),
                ("state", "in", ["pending", "ongoing"]),
            ]
            other = self.search_count(domain)
            if other:
                raise ValidationError(
                    _("L'empleat ja te un repartiment pendent o en curs.")
                )

    @api.constrains("vehicle_id", "state")
    def _check_vehicle_busy(self):
        # valida vehicle lliure
        for trip in self:
            if not trip.vehicle_id:
                continue
            domain = [
                ("id", "!=", trip.id),
                ("vehicle_id", "=", trip.vehicle_id.id),
                ("state", "in", ["pending", "ongoing"]),
            ]
            other = self.search_count(domain)
            if other:
                raise ValidationError(
                    _("El vehicle ja te un repartiment pendent o en curs.")
                )

    @api.constrains("vehicle_id", "distance_km")
    def _check_distance_vehicle(self):
        # valida distancia vehicle
        for trip in self:
            if trip.vehicle_id.vehicle_type == "bike" and trip.distance_km > 10:
                raise ValidationError(
                    _("Els repartiments de mes de 10 km no es poden fer en bicicleta.")
                )
            if trip.vehicle_id.vehicle_type == "van" and trip.distance_km < 1:
                raise ValidationError(
                    _("Els repartiments de menys d'1 km no es poden fer en furgoneta.")

                )
