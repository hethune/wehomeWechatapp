from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from application.app import app, db
from application.scripts import sync_map_box_place_name as sync_map
migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()

@manager.command
def sync_data():
  """sync data to database"""
  sync_map.sync_place_data()

if __name__ == '__main__':
    manager.run()