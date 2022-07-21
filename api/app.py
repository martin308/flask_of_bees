import os
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.sdk.trace.export import (SimpleSpanProcessor, ConsoleSpanExporter)

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
print("Initializing tracing")
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Bee(db.Model):
    __tablename__ = "bees"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

@app.before_first_request
def create_tables():
    db.create_all()

class BeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Bee
    id = ma.auto_field()
    name = ma.auto_field()

bee_schema = BeeSchema()
bees_schema = BeeSchema(many=True)

@app.route('/')
def welcome():
    return jsonify({'status': 'api working'})

@app.route('/bees', methods=['GET'])
def bees():
   bees = Bee.query.all()
   return make_response(jsonify(bees_schema.dump(bees)))

@app.route('/bees/<int:id>', methods=['GET'])
def get_bee(id):
    bee = Bee.query.get(id)
    return make_response(jsonify(bee_schema.dump(bee)))

@app.route('/bees', methods=['POST'])
def create_bee():
    data = request.get_json()
    bee = Bee(name=data['name'])
    db.session.add(bee)
    db.session.commit()
    return make_response(jsonify(bee_schema.dump(bee)), 200)

@app.route('/bees/<int:id>', methods=['DELETE'])
def delete_bee(id):
    bee = Bee.query.get(id)
    db.session.delete(bee)
    db.session.commit()
    return make_response("", 204)

if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    # in some future article, we are going to use an env variable instead a hardcoded port
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
