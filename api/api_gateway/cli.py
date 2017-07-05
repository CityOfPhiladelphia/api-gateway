import multiprocessing

import click
import gunicorn.app.base
from gunicorn.six import iteritems
from sqlalchemy import create_engine

from api_gateway.app import app
from api_gateway.worker import run_worker
from api_gateway.models import db

def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

@click.group()
def main():
    pass

@main.command()
@click.option('--sql-alchemy-connection')
def init_db(sql_alchemy_connection):
    connection_string = sql_alchemy_connection or os.getenv('SQL_ALCHEMY_CONNECTION')

    engine = create_engine(connection_string)

    db.Model.metadata.create_all(engine)

@main.command()
@click.option('--bind-host', default='0.0.0.0')
@click.option('--bind-port', default='5000', type=int)
@click.option('--worker-class', default='sync')
@click.option('--prod', is_flag=True, default=False)
def api_server(bind_host, bind_port, worker_class, prod):
    if prod:
        options = {
            'bind': '{}:{}'.format(bind_host, bind_port),
            'workers': number_of_workers(),
            'worker_class': worker_class
        }
        StandaloneApplication(app, options).run()
    else:
        app.run(host=bind_host, port=bind_port)

@main.command()
@click.option('--sql-alchemy-connection')
@click.option('--sqs-queue-url')
@click.option('-n','--num-runs', type=int, default=10)
@click.option('--sleep', type=int, default=0)
def worker(sql_alchemy_connection, sqs_queue_url, num_runs, sleep):
    run_worker(sql_alchemy_connection=sql_alchemy_connection,
               sqs_queue_url=sqs_queue_url,
               num_runs=num_runs,
               sleep=sleep)
