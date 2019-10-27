from deeppavlov import build_model, configs



model = build_model(configs.squad.squad_bert, load_trained=True, download=True)


print(model(['In meteorology, precipitation is any product of the condensation of atmospheric water vapor that falls under gravity. The main forms of precipitation include drizzle, rain, sleet, snow, graupel and hail… Precipitation forms as smaller droplets coalesce via collision with other rain drops or ice crystals within a cloud. Short, intense periods of rain in scattered locations are called “showers”.'], ['Where do water droplets collide with ice crystals to form precipitation?']))

