from flask_swagger_ui import get_swaggerui_blueprint

swagger_url = '/swagger'
_api_url = '/static/swagger.json'  # TODO update swagger or change to FastAPI - it builds swagger automatically
swagger_ui_blueprint = get_swaggerui_blueprint(
    swagger_url,
    _api_url,
    config={
        'app_name': "text-analysis"
    }
)
