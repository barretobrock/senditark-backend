from senditark_api.app import create_app
from senditark_api.config import ProductionConfig

app = create_app(config_class=ProductionConfig)

if __name__ == '__main__':
    app.run(host=ProductionConfig.DB_SERVER, port=ProductionConfig.PORT)
