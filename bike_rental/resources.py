from import_export import fields, resources, widgets
from .models import BikeModel, BikeType, RidePurpose, Bike, Price

class BikeModelResource(resources.ModelResource):
    bike_type = fields.Field(
        column_name='bike_type',
        attribute='bike_type',
        widget=widgets.ForeignKeyWidget(BikeType, 'name')
    )
    ride_purposes = fields.Field(
        column_name='ride_purposes',
        attribute='ride_purposes',
        widget=widgets.ManyToManyWidget(RidePurpose, field='name', separator='|')
    )

    class Meta:
        model = BikeModel
        fields = ('id', 'brand', 'model', 'transmission', 'gears', 'displacement', 'tank', 'fuel_system', 'max_speed', 'wheel_size', 'description', 'bike_model_photo', 'seat_height', 'fuel_consumption', 'weight', 'bike_type', 'ride_purposes')
        export_order = fields
    
class BikeModelResource(resources.ModelResource):
    class Meta:
        model = BikeModel

class BikeResource(resources.ModelResource):
    class Meta:
        model = Bike

class PriceResource(resources.ModelResource):
    class Meta:
        model = Price