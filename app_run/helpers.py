from django.db.models import F, Func, FloatField, ExpressionWrapper, Value

R = 6371000


class Radians(Func):
    function = 'RADIANS'
    output_field = FloatField()


class Cos(Func):
    function = 'COS'
    output_field = FloatField()


class Sin(Func):
    function = 'SIN'
    output_field = FloatField()


class Acos(Func):
    function = 'ACOS'
    output_field = FloatField()


def get_distance(lat_a, long_a):
    return ExpressionWrapper(
        R * Acos(
            Cos(Radians(Value(lat_a))) *
            Cos(Radians(F('latitude'))) *
            Cos(Radians(F('longitude') - Value(long_a))) +
            Sin(Radians(Value(lat_a))) *
            Sin(Radians(F('latitude')))
        ),
        output_field=FloatField()
    )