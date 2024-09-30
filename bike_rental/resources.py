from import_export import fields, resources, widgets
from .models import BikeModel, BikeType, RidePurpose, Bike, Price, Promouter, BikeOrder, Season

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
        export_order = fields #['id', 'brand', 'model', 'transmission', 'gears', 'displacement', 'tank', 'fuel_system', 'max_speed', 'wheel_size', 'description', 'bike_model_photo', 'seat_height', 'fuel_consumption', 'weight', 'bike_type', 'ride_purposes']
    

class BikeResource(resources.ModelResource):
    class Meta:
        model = Bike

class PromouterResource(resources.ModelResource):
    class Meta:
        model = Promouter
        fields = ('id', 'user__username', 'promo_pyte', 'comition_percent', 'qr_codes')

class BikeOrderResource(resources.ModelResource):
    class Meta:
        model = BikeOrder
        fields = ('id', 'bike__bike_model__brand__name', 'bike__bike_model__model', 'start_date', 'duration', 'amount_bikes', 'total_price', 'client__name', 'client__contact')
        export_order = fields #['id', 'bike__bike_model__brand__name', 'bike__bike_model__model', 'start_date', 'duration', 'amount_bikes', 'total_price', 'client__name', 'client__contact']  # Задан список полей

class SeasonResource(resources.ModelResource):
    class Meta:
        model = Season
        fields = ('id', 'name', 'start_date', 'close_date', 'bike_provider__name')
        export_order = fields #['id', 'name', 'start_date', 'close_date', 'bike_provider__name']  # Задан список полей

class PriceResource(resources.ModelResource):
    bike_id = fields.Field(attribute='bike_id', column_name='bike_id')
    season_id = fields.Field(attribute='season_id', column_name='season_id')
    season_name = fields.Field(attribute='season__name', column_name='season_name', readonly=True)

    class Meta:
        model = Price
        fields = ('id', 'bike_id', 'bike__bike_model__brand__name', 'bike__bike_model__model', 'season_id', 'season_name', 'duration', 'cost')
        export_order = fields #['id', 'bike_id', 'bike__bike_model__brand__name', 'bike__bike_model__model', 'season_id', 'season_name', 'duration', 'cost']  # Задан список полей
        import_id_fields = ('bike_id', 'season_id', 'duration')