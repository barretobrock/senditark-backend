#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from senditark_api.app import create_app
from senditark_api.config import DevelopmentConfig

if __name__ == '__main__':
    # Instantiate log here, as the hosts API is requested to communicate with influx
    app = create_app(config_class=DevelopmentConfig)
    app.run(host=DevelopmentConfig.DB_SERVER, port=DevelopmentConfig.PORT)
