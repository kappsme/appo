"""
Database initialization script
"""
from app import app, db
from models import Service, Availability
from datetime import time


def init_database():
    """Initialize database with tables and default data"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Create default services if none exist
        if Service.query.count() == 0:
            print("Creating default services...")
            default_services = [
                Service(
                    name='Consulta General',
                    description='Consulta médica general',
                    duration=30,
                    price=50.0,
                    active=True
                ),
                Service(
                    name='Consulta Especializada',
                    description='Consulta con especialista',
                    duration=45,
                    price=80.0,
                    active=True
                ),
                Service(
                    name='Revisión Completa',
                    description='Revisión médica completa',
                    duration=60,
                    price=100.0,
                    active=True
                ),
                Service(
                    name='Terapia',
                    description='Sesión de terapia',
                    duration=60,
                    price=70.0,
                    active=True
                )
            ]
            
            for service in default_services:
                db.session.add(service)
            
            db.session.commit()
            print(f"✓ Created {len(default_services)} default services")
        else:
            print(f"✓ Services already exist ({Service.query.count()} services)")
        
        # Create default availability if none exists
        if Availability.query.count() == 0:
            print("Creating default availability...")
            # Monday to Friday, 9 AM to 6 PM
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            for day in range(5):
                availability = Availability(
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(18, 0),
                    duration_minutes=60,
                    enabled=True
                )
                db.session.add(availability)
                print(f"  ✓ {day_names[day]}: 09:00 - 18:00")
            
            db.session.commit()
            print("✓ Default availability created")
        else:
            print(f"✓ Availability already configured ({Availability.query.count()} days)")
        
        print("\n✅ Database initialization completed successfully!")


if __name__ == '__main__':
    init_database()
